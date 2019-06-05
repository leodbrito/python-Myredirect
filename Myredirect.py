from flask import Flask, render_template, request, redirect, session, flash, url_for
from models import Myredirect, Usuario

app = Flask(__name__)
app.secret_key = 'bolsominion'

usuario1 = Usuario('leo', 'Leonardo Brito', '123')
usuario2 = Usuario('Nico', 'Nico Steppat', '123')

usuarios = {usuario1.id: usuario1,
            usuario2.id: usuario2}

# Lista global de CHGs a serem configuradas
chg_input_list = []
# Lista global de objetos do tipo Myredirect
myredirect_list = []
# Variavel global para carregar o arquivo de configuração
changed_conf_file = ""
# Variavel global para indicar se existem ou não redirects de destino. Caso não exista
dest_url = ""
# Lista global de testes curl para as urls de origem informadas
chgcurl_list = []
# Lista global das novas regras
new_rule_list = []

@app.route('/')
def index():
    return render_template('login.html', proxima=url_for('welcome'))

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

@app.route('/welcome')
def welcome():
    # Limpando as listas de CHGs e testando se o usurário logado está na sessão
    global chg_input_list
    global myredirect_list
    chg_input_list = []
    myredirect_list = []
    if 'logged_user' not in session or session['logged_user'] == None:
        return redirect(url_for('login', proxima=url_for('welcome')))
    return render_template('welcome.html', titulo='Bem Vindo!')

@app.route('/logout')
def logout():
    session['logged_user'] = None
    flash('Nenhum usuário logado!')
    return redirect(url_for('index'))

@app.route('/new')
def new():
    return render_template('new.html', titulo='Novo Redirect')

@app.route('/undo')
def undo():
    return render_template('new.html', titulo='Desfazer Redirect')

@app.route('/pre_build', methods=['POST',])
def pre_build():
    global dest_url
    protocol = request.form['protocol']
    source_url = request.form['source_url']
    dest_url = request.form['dest_url']
    myredirect = Myredirect(protocol, source_url, dest_url)
    myredirect_list.append(myredirect)
    chg_input = myredirect.chg_pre_build()
    chg_input_list.append(chg_input)
    for chg_input_item in chg_input_list:
        next_chg_input_item_index = chg_input_list.index(chg_input_item)+1
        for i in range(next_chg_input_item_index,len(chg_input_list)):
            if  chg_input_item['prot'] == chg_input_list[i]['prot']:
                for item in chg_input_list[i]['rule_list']:
                    chg_input_item['rule_list'].append(item)
                for item in chg_input_list[i]['rae']['will_comment_line_list']:
                    chg_input_item['rae']['will_comment_line_list'].append(item)
                for item in chg_input_list[i]['chgcurl']:
                    chg_input_item['chgcurl'].append(item)
                if chg_input_list[i]['dest_url_ok'] != True:
                    if chg_input_item['dest_url_ok'] == True:
                        chg_input_item['dest_url_ok'] = chg_input_list[i]['dest_url_ok']
                    else:
                        for item in chg_input_list[i]['dest_url_ok']:
                            chg_input_item['dest_url_ok'].append(item)
                chg_input_list.remove(chg_input_list[i])
    return redirect(url_for('show_pre_build'))

@app.route('/show_pre_build')
def show_pre_build():
    if dest_url != "":
        return render_template('show_pre_build.html', titulo='Novos Redirects', myredirect_list=myredirect_list, chg_input_list=chg_input_list)
    else:
        return render_template('show_pre_build.html', titulo='Desfazer Redirects', myredirect_list=myredirect_list, chg_input_list=chg_input_list)

@app.route('/build_chg')
def build_chg():
    for myredirect in myredirect_list:
        myredirect.build_chgs()
    global changed_conf_file
    changed_conf_file = Myredirect().read_conf_file()
    global new_rule_list
    for chg_input in chg_input_list:
        for rule in chg_input['rule_list']:
            new_rule_list.append(rule)
    return redirect(url_for('verbose'))

@app.route('/clean_all')
def clean_all():
    global chg_input_list
    global myredirect_list
    chg_input_list = []
    myredirect_list = []
    return redirect(url_for('show_pre_build'))

@app.route('/new_rule_in_some_chg/<chg_input_prot>/<titulo>')
def new_rule_in_some_chg(chg_input_prot, titulo):
    if titulo == "Novos Redirects":
        return render_template('new.html', titulo='Nova Regra', chg_input_prot=chg_input_prot)
    else:
        return render_template('new.html', titulo='Nova Regra a Desfazer', chg_input_prot=chg_input_prot)
            
@app.route('/clean_chg_input', defaults={'chg_input_prot': None})
@app.route('/clean_chg_input/<chg_input_prot>')
def clean_chg_input(chg_input_prot):
    global chg_input_list
    global myredirect_list
    for chg_input in chg_input_list:
        if chg_input['prot'] == chg_input_prot:
            chg_input_list.remove(chg_input)
    my_object_list = myredirect_list[:]
    for myredirect in my_object_list:
        protocol = myredirect.protocol.upper()
        if protocol == chg_input_prot:
            myredirect_list.remove(myredirect)
    return redirect(url_for('show_pre_build'))

@app.route('/verbose')
def verbose():
    global chgcurl_list
    chgcurl_list = []
    i = 0
    nprot = ""
    for myredirect in myredirect_list:
        prot = myredirect.protocol.upper()
        if i > 0:
            nprot = myredirect_list[i-1].protocol.upper()
        i += 1
        if prot != nprot:
            chgcurl_list.append(prot)
        chgcurl_list.append(myredirect.chgcurl())
    #for item in chgcurl_list:
    #    if item[0:3] == "CHG":
    #        itemprot = item
    #    for i in range(1,len(chgcurl_list)):
    #        nextitem = chgcurl_list[i]
    #        if itemprot == nextitem:
    #            chgcurl_list.remove(nextitem)
    return render_template('verbose.html', titulo='Meus Redirects', changed_conf_file=changed_conf_file, myredirect_list=myredirect_list, chg_input_list=chg_input_list, chgcurl_list=chgcurl_list, new_rule_list=new_rule_list)

app.run(debug=True, host='0.0.0.0', port=8080)
