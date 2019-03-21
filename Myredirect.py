import re, subprocess
from flask import Flask, render_template, request, redirect, session, flash, url_for

app = Flask(__name__)
app.secret_key = 'bolsominion'

class Myredirect:
    def __init__(self, protocol=None, source_url=None, dest_url=None, filepath='show-services.conf'):
        self.protocol = protocol
        self.source_url = source_url
        self.dest_url = dest_url
        self.filepath = filepath

    def check_dest_url_ok(self):
        dest_url = str(self.dest_url).strip()
        p1 = subprocess.Popen(['curl', '-sIL' , dest_url], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(['grep', ' 200'], stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        output = str(p2.communicate()[0].decode()).strip()
        if output.find(' 200') != -1 :
            return True
        else:
            return False

    def check_redirect_already_exist(self):
        source_url = str(self.source_url).strip().split()
        line_index_redirect_already_exist_list= []
        url_redirect_already_exist_list = []
        line_redirect_already_exist_list = []
        with open(self.filepath,'r') as conf_file_openned:
            conf_file = conf_file_openned.readlines()

        compile1 = re.compile(r'^http[s]?.*com/', flags=re.IGNORECASE)
        for url in source_url:
            uri = str(compile1.sub(r'rewrite ^/',url))
            for line in conf_file:
                if line.find(uri) != -1 and line[0] != '#' :
                    line_index_redirect_already_exist_list.append(conf_file.index(line))
                    url_redirect_already_exist_list.append(url)
                    line_redirect_already_exist_list.append(line)
        
        return {'line_index_list':line_index_redirect_already_exist_list, 'line_list':line_redirect_already_exist_list, 'url_list':url_redirect_already_exist_list, 'conf_file':conf_file}
    
    def edit_file_line(self, line_index, new_line):
        conf_file = self.filepath
        with open(conf_file,'r') as f:
            file=f.readlines()
        with open(conf_file,'w') as f:
            for line in file:
                if file.index(line) == line_index:
                    f.write(new_line+'\n')
                else:
                    f.write(line)

    def chgcurl(self):
        pass
    
    def build_redirect(self):
        protocol = str(self.protocol).strip().upper()
        source_url = str(self.source_url).strip().split()
        dest_url = str(self.dest_url).strip()
        
        # Cria a linha comentada referenciando o numero do protocolo
        if protocol[0] != '#':
            protocol = '#'+protocol

        # Compila os inputs para criar a lista de regras
        rule_list = []
        compile1 = re.compile(r'^http[s]?.*com/', flags=re.IGNORECASE)
        for url in source_url:
            replace1 = compile1.sub(r'rewrite ^/',url)
            rule_list.append(replace1+f'$ {dest_url} permanent;')
        
        # Checa se a URL de destino informada está OK
        dest_url_ok = self.check_dest_url_ok()
        if not dest_url_ok:
            dest_url_ok = f'ATENÇÃO: a URL de destino, {dest_url}, NÃO está retornando status 200, necessário checar!'

        # Retorna as URLs informadas que ja possuem redirect configurado no arquivo
        rae = self.check_redirect_already_exist()
        
        # Se a URL informada já possuir redirect configurado no arquivo, a sua linha é comentada
        new_lines=[]
        if rae['line_index_list'][0] != "" :
            for index in rae['line_index_list']:
                new_line = '#'+rae['conf_file'][index]
                self.edit_file_line(index, new_line)
                new_lines.append(str(index)+' '+new_line)
                
        return {'prot':protocol, 'rule':rule_list, 'dest_url_ok':dest_url_ok, 'rae':rae, 'new_lines':new_lines}

class Usuario:
    def __init__(self, id, nome, senha):
        self.id = id
        self.nome = nome
        self.senha = senha

usuario1 = Usuario('leo', 'Leonardo Brito', '123')
usuario2 = Usuario('Nico', 'Nico Steppat', '123')

usuarios = {usuario1.id: usuario1,
            usuario2.id: usuario2}
redirect_input_list = []

@app.route('/')
def index():
    return render_template('login.html', proxima=url_for('new'))

@app.route('/new')
def new():
    if 'logged_user' not in session or session['logged_user'] == None:
        return redirect(url_for('login', proxima=url_for('new')))
    return render_template('new.html', titulo='Novo Redirect')

@app.route('/create', methods=['POST',])
def create():
    protocol = request.form['protocol']
    source_url = request.form['source_url']
    dest_url = request.form['dest_url']
    myredirect = Myredirect(protocol, source_url, dest_url)
    redirect_input = myredirect.build_redirect()
    redirect_input_list.append(redirect_input)
    return redirect(url_for('verbose'))

@app.route('/verbose')
def verbose():
    return render_template('verbose.html', titulo='Meus Redirects', redirect_input_list=redirect_input_list)

@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)

@app.route('/authenticate', methods=['POST', ])
def authenticate():
    if request.form['usuario'] in usuarios:
        usuario = usuarios[request.form['usuario']]
        if usuario.senha == request.form['senha']:
            session['logged_user'] = usuario.id
            flash(usuario.nome +' logou com sucesso!')
            proxima_pagina = request.form['proxima']
            return redirect(proxima_pagina)
        else:
            flash('Senha incorreta, tente novamente!')
            return redirect(url_for('login'))
    else:
        flash('Usuário e/ou senha incorretos, tente novamente!')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session['logged_user'] = None
    flash('Nenhum usuário logado!')
    return redirect(url_for('index'))

app.run(debug=True, host='0.0.0.0', port=8080)
