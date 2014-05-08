django-fab-server-centos
=================

Como funciona?

<p>É um fabric que acessa o servidor e instala todas dependencias no seu linux CentOS.</p>

requirements:

    servidor linux CentOS > 6.5
    pip
    fabric==1.6.0
    jinja2==2.7


Clone o projeto na máquina na sua pasta de projetos:

    git clone git@github.com:willemallan/django-fab-server-centos.git


Instalando na máquina o pip em distribuições linux badeadas no debian:

    sudo apt-get install python-pip


Não precisa criar um env pode até instalar o fabric e o jinja2 no sistema caso prefira crie um env:

    mkvirtualenv djangofabservercentos

Entrar no diretório do django fab server:

    cd django-fab-server-centos
    setvirtualenvproject


Instale os requirements do django fab server:

    pip install -r requirements.txt


Configurando uma máquina para rodar python/django e MySQL:

<ul>
    <li>
        <a href="html/NEWSERVER.md"><b>Servidor</b></a> é para configurar um servidor linux para rodar sites em python/django.
    </li>
</ul>

Listando os comandos:

    fab list

Comandos disponíveis:

    adduser            Criar um usuário no servidor
    build              Instala dependencias no servidor
    create_password    Gera uma senha - parametro tamanho
    delaccount         Deletar conta no servidor
    deluser            Deletar usuário no servidor
    dropbase           Deletar banco de dados e usuário no servidor
    log                Mensagens de acerta dos comandos executados no servidor
    login              Acessa o servidor
    newaccount         Criar uma nova conta do usuário no servidor
    newbase            Criar banco de dados e usuário no servidor
    newserver          Configurar e instalar todos pacotes necessários para servidor
    nginx              Instala e configura nginx no servidor
    nginx_reload       Reload nginx no servidor
    nginx_restart      Restart nginx no servidor
    nginx_start        Start nginx no servidor
    nginx_stop         Stop nginx no servidor
    python             Instalando e configurando python
    reboot             Reinicia o servidor
    update_server      Atualizando pacotes no servidor
    updateserver       Atualiza o servidor
    upgrade_server     Atualizar programas no servidor
    upload_public_key  Faz o upload da chave ssh para o servidor
    uwsgi              Instala uwsgi no servidor
    write_file         Função que utiliza o jinja2 para escrever arquivo no servidor