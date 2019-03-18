import re, subprocess
source_url = ['https://gshow.globo.com/receitas-gshow/produto/e-de-casa/noticia/ana-furtado-adota-novo-corte-de-cabelo-foi-um-rito-de-passagem.ghtml','https://globoesporte.globo.com/programas/globo-esporte/noticia/no-tranco-cafezinho-com-escobar-desembarca-em-sao-conrado.ghtml']
uri_redirect_exist_list = []
uri_list = []
i = 0
myfile = []
compile1 = re.compile(r'^http[s]?.*com/', flags=re.IGNORECASE)
conf_file = open('show-services.conf','r')
for url in source_url:
    uri = str(compile1.sub(r'/',url))
    uri_list.append(uri)

for line in conf_file:
    line = str(line).rstrip()
    myfile.append(line)

for line in myfile:
    if line.find(uri_list[0]) > -1 :
        uri_redirect_exist_list.append(uri_list[0])






dest_url = 'http://formulario-colaborativo.globo.com/campaign/571'
p1 = subprocess.Popen(['curl', '-sIL' , dest_url], stdout=subprocess.PIPE)
p2 = subprocess.Popen(['grep', ' 200'], stdin=p1.stdout, stdout=subprocess.PIPE)
p1.stdout.close()
output = str(p2.communicate()[0].decode()).strip()
if output.find(' 200') != -1 :
    print('True')
else:
    print('False')