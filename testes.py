##############################################################################################
##############################################################################################
import re, subprocess
source_url = ['https://gshow.globo.com/realities/bbb/bbb19/episodio/2019/02/25/videos-de-bbb-de-segunda-feira-25-de-fevereiro', 'https://globoesporte.globo.com/naoexiste', 'https://gshow.globo.com/realities/bbb/bbb19/noticia/prova-do-anjo-no-bbb19-relembre-quem-ja-ganhou-nesta-edicao.ghtml', 'https://gshow.globo.com/Famosos/noticia/juliana-paes-faz-sucesso-na-internet-com-foto-ousada-de-carnaval.ghtml']
i = 1
index_line_list= []
url_redirect_exist_list = []
line_redirect_exist_list = []
uri_list = []
conf_file = []
conf_file_openned = open('show-services.conf','r')
for line in conf_file_openned:
            line = str(line).rstrip()
            conf_file.append(line)

conf_file_openned.close()
compile1 = re.compile(r'^http[s]?.*com/', flags=re.IGNORECASE)
for url in source_url:
    uri = str(compile1.sub(r'/',url))
    uri_list.append(uri)
    for line in conf_file:
        if line.find(uri) != -1 and line[0] != '#' :
            index_line_list.append(i)
            url_redirect_exist_list.append(url)
            line_redirect_exist_list.append(line)
        i += 1

##############################################################################################
##############################################################################################
line_index = 1617
new_line = '#rewrite ^/realities/bbb/bbb19/votacao/playlistbbb-que-musica-voce-quer-ouvir-na-proxima-festa-vote-c4fc6280-2b63-43ab-9050-00055d8491c8.ghtml$ https://gshow.globo.com/realities/bbb/ permanent;'
def edit_file_line(line_index, new_line):
    conf_file = 'show-services.conf'
    with open(conf_file,'r') as f:
        file=f.readlines()
    with open(conf_file,'w') as f:
        for line in file:
            if file.index(line) == line_index:
                f.write(new_line+'\n')
            else:
                f.write(line)

edit_file_line(line_index, new_line)


##############################################################################################
##############################################################################################

dest_url = 'http://formulario-colaborativo.globo.com/campaign/571'
p1 = subprocess.Popen(['curl', '-sIL' , dest_url], stdout=subprocess.PIPE)
p2 = subprocess.Popen(['grep', ' 200'], stdin=p1.stdout, stdout=subprocess.PIPE)
p1.stdout.close()
output = str(p2.communicate()[0].decode()).strip()
if output.find(' 200') != -1 :
    print('True')
else:
    print('False')