import subprocess
import re
from flask import Flask, render_template, request, redirect, session, flash, url_for

app = Flask(__name__)
app.secret_key = 'bolsominion'

class Myredirect:
    def __init__(self, protocol=None, source_url=None, dest_url=None, filepath=None):
        self.protocol = protocol
        self.source_url = source_url
        self.dest_url = dest_url
        self.filepath = filepath

    def chgcurl(self):
        pass

    def check_redirect(self):
        pass
    
    def build_redirect(self):
        protocol = str(self.protocol).strip()
        source_url = str(self.source_url).strip().split()
        dest_url = str(self.dest_url).strip()
        
        if protocol.find('#') != 0:
            protocol = '#'+protocol.upper()

        compile1 = re.compile("^http[s]?.*com/")
        concat1 = []
        for url in source_url:
            replace1 = compile1.sub(r'rewrite ^/',url)
            concat1.append(replace1+f'$ {dest_url} permanent;')
        #redirect_output=Nul
        #redirect_output={'prot':protocol}
        #for i in range(0, len(concat1)):
            #redirect_output+=f'{concat1[i]}\n'
            #redirect_output[f'rule{i}']=concat1[i]
        
        #redirect_output = f'{protocol}\n{redirect_output}'
        #return redirect_output
        return {'prot':protocol, 'rule':concat1}

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
    return render_template('login.html', proxima=url_for('novo'))

@app.route('/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    return render_template('novo.html', titulo='Novo Redirect')

@app.route('/criar', methods=['POST',])
def criar():
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


@app.route('/autenticar', methods=['POST', ])
def autenticar():
    if request.form['usuario'] in usuarios:
        usuario = usuarios[request.form['usuario']]
        if usuario.senha == request.form['senha']:
            session['usuario_logado'] = usuario.id
            flash(usuario.nome + 'logou com sucesso!')
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
