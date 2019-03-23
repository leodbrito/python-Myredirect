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

    def read_conf_file(self):
        with open(self.filepath,'r') as conf_file_openned:
            conf_file = conf_file_openned.readlines()
        return conf_file

    def create_rule_list(self):
        source_url = str(self.source_url).strip().split()
        dest_url = str(self.dest_url).strip()
        rule_list = []
        compile1 = re.compile(r'^(http[s]?|www|gshow|ge|globoesporte|g1).*com(.br)?/', flags=re.IGNORECASE)
        for url in source_url:
            compiled = str(compile1.sub(r'rewrite ^/',url))
            rule_list.append(compiled+f'$ {dest_url} permanent;')
        return rule_list

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
        conf_file = self.read_conf_file()
        compile1 = re.compile(r'^(http[s]?|www|gshow|ge|globoesporte|g1).*com(.br)?/', flags=re.IGNORECASE)
        for url in source_url:
            rule = str(compile1.sub(r'rewrite ^/',url))
            for line in conf_file:
                if line.find(rule) != -1 and line[0] != '#' :
                    line_index_redirect_already_exist_list.append(conf_file.index(line))
                    url_redirect_already_exist_list.append(url)
                    line_redirect_already_exist_list.append(line)
        
        return {'line_index_list':line_index_redirect_already_exist_list, 'line_list':line_redirect_already_exist_list, 'url_list':url_redirect_already_exist_list}
    
    def edit_file_line(self, line_index, new_line):
        conf_file = self.filepath
        with open(conf_file,'r') as f:
            file=f.readlines()
        with open(conf_file,'w') as f:
            for line in file:
                if file.index(line) == line_index:
                    f.write(new_line)
                else:
                    f.write(line)

    def chgcurl(self):
        pass
    
    def chg_pre_build(self):
        pass

    def build_chg_undo_redirect(self):
        
        pass

    def build_chg_new_redircet(self):
        protocol = str(self.protocol).strip().upper()
        source_url = str(self.source_url).strip().split()
        dest_url = str(self.dest_url).strip()
        
        # Carregando o arquivo de configuração
        conf_file = self.read_conf_file()

        # Cria a linha comentada referenciando o numero do protocolo
        if protocol[0] != '#':
            protocol = '#'+protocol

        # criar a lista de regras
        rule_list = []
        rule_list = self.create_rule_list()
        
        # Checa se a URL de destino informada está OK
        dest_url_ok = self.check_dest_url_ok()
        if not dest_url_ok:
            dest_url_ok = f'ATENÇÃO: a URL de destino, {dest_url}, NÃO está retornando status 200, necessário checar!'

        # Retorna as URLs informadas que ja possuem redirect configurado no arquivo
        rae = self.check_redirect_already_exist()
        
        # Se a URL informada já possuir redirect configurado no arquivo, sua linha é comentada
        comment_line_list = []
        if rae['line_index_list'] != "":
            for index in rae['line_index_list']:
                comment_line = '#'+conf_file[index]
                self.edit_file_line(index, comment_line)
                comment_line_list.append(str(index)+' '+comment_line)

        # Insere as CHGs no arquivo
        for line in conf_file:
            if line.find('# EOF') != -1:
                eof_index = conf_file.index(line)
                
            pass

        return {'prot':protocol, 'rule_list':rule_list, 'conf_file':conf_file, 'dest_url_ok':dest_url_ok, 'rae':rae, 'comment_line_list':comment_line_list}

class Usuario:
    def __init__(self, id, nome, senha):
        self.id = id
        self.nome = nome
        self.senha = senha

usuario1 = Usuario('leo', 'Leonardo Brito', '123')
usuario2 = Usuario('Nico', 'Nico Steppat', '123')

usuarios = {usuario1.id: usuario1,
            usuario2.id: usuario2}
chg_input_list = []

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
    chg_input = myredirect.build_chg_new_redircet()
    chg_input_list.append(chg_input)
    return redirect(url_for('verbose'))

@app.route('/verbose')
def verbose():
    return render_template('verbose.html', titulo='Meus Redirects', chg_input_list=chg_input_list)

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
