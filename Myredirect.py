import re, subprocess
from flask import Flask, render_template, request, redirect, session, flash, url_for

app = Flask(__name__)
app.secret_key = 'bolsominion'

class Myredirect:
    def __init__(self, protocol=None, source_url=None, dest_url=None, filepath=None):
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

    def check_redirect_exist(self):
        source_url = str(self.source_url).strip().split()
        url_redirect_exist_list = []
        url_redirect_not_exist_list = []
        uri_list = []
        compile1 = re.compile(r'^http[s]?.*com/', flags=re.IGNORECASE)
        conf_file = open('show-services.conf','r')
        for url in source_url:
            uri = compile1.sub(r'/',url)
            for line in conf_file:
                if line.find(uri) != -1:
                    url_redirect_exist_list.append(url)
        return {'yes':url_redirect_exist_list , 'no':url_redirect_not_exist_list}
    
    def chgcurl(self):
        pass
    
    def build_redirect(self):
        protocol = str(self.protocol).strip().upper()
        source_url = str(self.source_url).strip().split()
        dest_url = str(self.dest_url).strip()
        
        if protocol[0] != '#':
            protocol = '#'+protocol

        compile1 = re.compile(r'^http[s]?.*com/', flags=re.IGNORECASE)
        rule_list = []
        for url in source_url:
            replace1 = compile1.sub(r'rewrite ^/',url)
            rule_list.append(replace1+f'$ {dest_url} permanent;')
        
        return {'prot':protocol, 'rule':rule_list}

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
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('new')))
    return render_template('new.html', titulo='Novo Redirect')

@app.route('/create', methods=['POST',])
def create():
    protocol = request.form['protocol']
    source_url = request.form['source_url']
    dest_url = request.form['dest_url']
    redirect_input = Myredirect(protocol, source_url, dest_url).build_redirect()
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
            session['usuario_logado'] = usuario.id
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
    session['usuario_logado'] = None
    flash('Nenhum usuário logado!')
    return redirect(url_for('index'))

app.run(debug=True, host='0.0.0.0', port=8080)
