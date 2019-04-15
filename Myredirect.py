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
        p1 = subprocess.Popen(['curl', '-sIL', '--connect-timeout', '3', dest_url], stdout=subprocess.PIPE)
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
        will_comment_line_list = ['[ ATENÇÃO ]: As seguintes linhas serão comentadas no arquivo de configuração:']
        conf_file = self.read_conf_file()
        compile1 = re.compile(r'^(http[s]?|www|gshow|ge|globoesporte|g1).*com(.br)?/', flags=re.IGNORECASE)
        for url in source_url:
            rule = str(compile1.sub(r'rewrite ^/',url))
            for line in conf_file:
                if line.find(rule) != -1 and line[0] != '#' :
                    line_index_redirect_already_exist_list.append(conf_file.index(line))
                    url_redirect_already_exist_list.append(url)
                    line_redirect_already_exist_list.append(line)
                    will_comment_line_list.append(str(conf_file.index(line))+'\t'+line)
        
        return {'line_index_list':line_index_redirect_already_exist_list, 'line_list':line_redirect_already_exist_list, 'url_list':url_redirect_already_exist_list, 'will_comment_line_list':will_comment_line_list}
    
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
        protocol = str(self.protocol).strip().upper()
        source_url = str(self.source_url).strip().split()
        dest_url = str(self.dest_url).strip()

        # Cria a linha comentada referenciando o numero do protocolo
        if protocol != "" and  protocol[0] != '#':
            protocol = '#'+protocol

        # criar a lista de regras
        rule_list = []
        rule_list = self.create_rule_list()
        
        # Checa se a URL de destino informada está OK
        dest_url_ok = self.check_dest_url_ok()
        if not dest_url_ok:
            dest_url_ok = f'[ ATENÇÃO ]: A URL de destino, {dest_url}, NÃO está retornando status 200, necessário checar!'

        # Instancia a função check_redirect_already_exist (rae) que verifica e retorna um dicionario com os indces e 
        # suas linhas, bem como as URLs informadas que ja possuem redirect configurado no arquivo
        rae = self.check_redirect_already_exist()
        
        return {'prot':protocol, 'rule_list':rule_list, 'dest_url_ok':dest_url_ok, 'rae':rae}
        

    def build_chg_new_redircet(self):
        
        # Carregando o arquivo de configuração
        conf_file = self.read_conf_file()

        # Carregando os dados do pre build
        chg_pre_build = self.chg_pre_build()
        protocol = chg_pre_build['prot']
        rae = chg_pre_build['rae']
        rule_list = chg_pre_build['rule_list']
        
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
        if eof_index != "":
            format_rules = ""
            for rule in rule_list:
                if format_rules == "":
                    format_rules = f'{rule}'
                else:
                    format_rules = f'{format_rules}\n{rule}'
            new_lines = f'{protocol}\n{format_rules}\n\n# EOF'
            self.edit_file_line(eof_index, new_lines)

        return {'comment_line_list':comment_line_list}

class Usuario:
    def __init__(self, id, nome, senha):
        self.id = id
        self.nome = nome
        self.senha = senha

usuario1 = Usuario('leo', 'Leonardo Brito', '123')
usuario2 = Usuario('Nico', 'Nico Steppat', '123')

usuarios = {usuario1.id: usuario1,
            usuario2.id: usuario2}

# Lista de CHGs a serem configuradas
chg_input_list = []
# Lista de objetos do tipo Myredirect
myredirect_list = []
# Variavel para carregar o arquivo de configuração
changed_conf_file = ""

@app.route('/')
def index():
    return render_template('login.html', proxima=url_for('welcome'))

@app.route('/welcome')
def welcome():
    if 'logged_user' not in session or session['logged_user'] == None:
        return redirect(url_for('login', proxima=url_for('welcome')))
    return render_template('welcome.html', titulo='Bem Vindo!')

@app.route('/new')
def new():
    return render_template('new.html', titulo='Novo Redirect')

@app.route('/create', methods=['POST',])
def create():
    protocol = request.form['protocol']
    source_url = request.form['source_url']
    dest_url = request.form['dest_url']
    myredirect = Myredirect(protocol, source_url, dest_url)
    myredirect_list.append(myredirect)
    chg_input = myredirect.chg_pre_build()
    chg_input_list.append(chg_input)
    return redirect(url_for('check_pre_build'))

@app.route('/check_pre_build')
def check_pre_build():
    return render_template('check_pre_build.html', titulo='Meus Redirects', myredirect_list=myredirect_list, chg_input_list=chg_input_list)

@app.route('/clean_pre_build')
def clean_pre_build():
    global chg_input_list
    global myredirect_list
    chg_input_list = []
    myredirect_list = []
    return render_template('check_pre_build.html', titulo='Meus Redirects', myredirect_list=myredirect_list, chg_input_list=chg_input_list)

@app.route('/clean_chg_input/<chg_input_prot>')
@app.route('/clean_chg_input_prot', defaults={'chg_input_prot':None})
def clean_chg_input(chg_input_prot=None):
    global chg_input_list
    for chg_input in chg_input_list:
        if chg_input.prot() == chg_input_prot:
            chg_input_list.remove(chg_input)
    return redirect(url_for('check_pre_build.html', titulo='Meus Redirects', myredirect_list=myredirect_list, chg_input_list=chg_input_list))

@app.route('/build_chg')
def build_chg():
    for myredirect in myredirect_list:
        myredirect.build_chg_new_redircet()
    global changed_conf_file
    changed_conf_file = Myredirect().read_conf_file()
    return redirect(url_for('verbose', changed_conf_file='changed_conf_file'))

@app.route('/verbose')
def verbose():
    global chg_input_list
    chg_input_list = []
    return render_template('verbose.html', titulo='Meus Redirects', changed_conf_file=changed_conf_file)

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
