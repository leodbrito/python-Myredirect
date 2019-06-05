import re, subprocess

#p1 = subprocess.Popen(['whoami'], stdout=subprocess.PIPE)
#logname = str(p1.communicate()[0].decode()).strip()

class Myredirect:
    #def __init__(self, protocol=None, source_url=None, dest_url=None, filepath=f'../../home/{logname}/teste/teste.conf'):
    def __init__(self, protocol=None, source_url=None, dest_url=None, filepath=f'show-services.conf'):
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
            if url.rfind('.',-6) != -1:
                rule_list.append(compiled+f'$ {dest_url} permanent;')
            elif url.rfind('/',-1) != -1:
                rule_list.append(compiled+f'?$ {dest_url} permanent;')
            else:
                rule_list.append(compiled+f'/?$ {dest_url} permanent;')
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
    
    # Função rae (redirect_already_exist) para verificar a pré-existência da configuração de um redircet através da URL de origem informada
    def check_redirect_already_exist(self):
        source_url = str(self.source_url).strip().split()
        line_index_redirect_already_exist_list= []
        url_redirect_already_exist_list = []
        line_redirect_already_exist_list = []
        will_comment_line_list = []
        prot_redirect_already_exist_list = []
        line_index_prot_redirect_already_exist_list = []
        conf_file = self.read_conf_file()
        compile1 = re.compile(r'^(http[s]?|www|gshow|ge|globoesporte|g1).*com(.br)?/', flags=re.IGNORECASE)
        for url in source_url:
            rule = str(compile1.sub(r'rewrite ^/',url))
            if url.rfind('.',-6) != -1:
                rule = f'{rule}$'
            elif url.rfind('/',-1) != -1:
                rule = f'{rule}?$'
            else:
                rule = f'{rule}/?$'
            for line in conf_file:
                if line.find(rule) != -1 and line[0] != '#':
                    line_index_redirect_already_exist_list.append(conf_file.index(line))
                    url_redirect_already_exist_list.append(url)
                    line_redirect_already_exist_list.append(line)
                    will_comment_line_list.append(str(conf_file.index(line))+'\t'+line)
        for line_index in line_index_redirect_already_exist_list:
            for i in range(line_index,0,-1):
                if conf_file[i] == '\n':
                    prot_redirect_already_exist_list.append(conf_file[i+1])
                    line_index_prot_redirect_already_exist_list.append(i+1)
                    break
        return {'line_index_list':line_index_redirect_already_exist_list, 'line_list':line_redirect_already_exist_list, 'url_list':url_redirect_already_exist_list, 'will_comment_line_list':will_comment_line_list, 'prot_list':prot_redirect_already_exist_list, 'line_index_prot_list':line_index_prot_redirect_already_exist_list}
    
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
        source_url = str(self.source_url).strip().split()
        chgcurl = []
        for url in source_url:
            p1 = subprocess.Popen(['curl', '-sIL', '--connect-timeout', '3', url], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(['egrep', '-i', '(http|Location)'], stdin=p1.stdout, stdout=subprocess.PIPE)
            p1.stdout.close()
            output = str(p2.communicate()[0].decode()).strip()
            output = output.split('\n')
            chgcurl.append(f'curl -sIL {url} | egrep -i \'(http|location)\'')
            chgcurl += output
            chgcurl.append('-----------------------------------------')
            p2.stdout.close()
        return chgcurl
    
    def chg_pre_build(self):
        protocol = str(self.protocol).strip().upper()
        source_url = str(self.source_url).strip().split()
        dest_url = str(self.dest_url).strip()
        # criar a lista de regras
        rule_list = []
        rule_list = self.create_rule_list()
        # Checa se a URL de destino informada está OK
        dest_url_ok = True
        if dest_url != "":
            dest_url_ok = self.check_dest_url_ok()
            if not dest_url_ok:
                dest_url_ok = [dest_url]
        # Instancia a função check_redirect_already_exist (rae) que verifica e retorna um dicionario com os indces e 
        # suas linhas, bem como as URLs informadas que ja possuem redirect configurado no arquivo
        rae = self.check_redirect_already_exist()
        # Instancia a função chgcurl que testa o redirect na linha de comando
        chgcurl = self.chgcurl()
        return {'prot':protocol, 'rule_list':rule_list, 'dest_url_ok':dest_url_ok, 'rae':rae, 'chgcurl':chgcurl}

    def build_chgs(self):  
        # Carregando o arquivo de configuração
        conf_file = self.read_conf_file()
        # Carregando os dados do pre build
        chg_pre_build = self.chg_pre_build()
        protocol = chg_pre_build['prot']
        rae_dict = chg_pre_build['rae']
        rule_list = chg_pre_build['rule_list']
        # Se a URL de origem informada já possuir redirect configurado no arquivo, sua linha é comentada
        comment_line_list = []
        if rae_dict['line_index_list'] != "":
            for index in rae_dict['line_index_list']:
                comment_line = '#'+conf_file[index]
                self.edit_file_line(index, comment_line)
                comment_line_list.append(str(index)+' '+comment_line)
            for line_index_prot in rae_dict['line_index_prot_list']:
                line_prot = conf_file[line_index_prot]
                prot_line = f'{line_prot.strip()} / {protocol}\n'
                self.edit_file_line(line_index_prot, prot_line)
        # Somente caso exista URL de destino, insere as novas CHGs no arquivo
        line_index = 0
        prot_finded_index = 0
        if self.dest_url != "":
            for line in conf_file:
                if line.find(protocol) != -1 and line[0] == '#': 
                    prot_finded_index = conf_file.index(line)
                    for line_index in range(prot_finded_index,len(conf_file)):
                        if conf_file[line_index] == '\n':
                            break
                if line.find('# EOF') != -1 or line.find('#EOF') != -1:
                    eof_index = conf_file.index(line)
            if line_index != 0:
                # Atribuindo a variavel format_rules propositalmente para obrigar a cair no primeiro if para criar as novas linhas
                format_lines = ""
                for rule in rule_list:
                    if format_lines == "":
                        format_lines = f'{conf_file[line_index-1]}{rule}'
                    else:
                        format_lines = f'{format_lines}\n{rule}'
                new_lines = f'{format_lines}\n'
                self.edit_file_line(line_index-1, new_lines)
            elif eof_index != 0:
                # Atribuindo a variavel format_rules propositalmente para obrigar a cair no primeiro if para criar as novas linhas
                format_rules = ""
                for rule in rule_list:
                    if format_rules == "":
                        format_rules = f'{rule}'
                    else:
                        format_rules = f'{format_rules}\n{rule}'
                new_lines = f'#{protocol}\n{format_rules}\n\n# EOF'
                self.edit_file_line(eof_index, new_lines)
        return {'comment_line_list':comment_line_list}

    def search_by_protocol(self):
        protocol = str(self.protocol).strip().upper()
        prot_finded_index = 0
        if protocol[0:3] != 'CHG' and protocol[4::].isnumeric():
            protocol = 'CHG'+protocol
        conf_file = self.read_conf_file()    
        for line in conf_file:
            if line.find(protocol) != -1 and line[0] == '#':
                prot_finded_index = conf_file.index(line)
        for i in range(prot_finded_index,len(conf_file)):
            if conf_file[i] == '\n':
                break
        search_by_prot_return = conf_file[prot_finded_index:i]
        return {'search_return':search_by_prot_return, 'prot_finded_index':prot_finded_index}


class Usuario:
    def __init__(self, id, nome, senha):
        self.id = id
        self.nome = nome
        self.senha = senha