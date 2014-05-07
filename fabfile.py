# -*- coding: utf-8 -*-
import os

from fabric.api import *
from fabric.contrib.files import upload_template

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------
# ALTERAR CONFIGURAÇÕES BASEADAS NO SEUS SERVIDOR E MAQUINA LOCAL
# ----------------------------------------------------------------

# SERVIDOR
user = 'root'
host = '192.168.0.119'
key_filename = '' # caminho da chave nome_arquivo.pem usado na amazon

# diretório de downloads
dir_download = '/usr/local/src/'

# diretório do conf.d do supervisor
env.supervisor_conf_d_path = '/etc/supervisor/conf.d'

# nome da account
env.account = ''

# dominio da account
env.domain = ''

# linguagem (1 = python, 2 = php)
env.language = ''

# senha do root do mysql
env.mysql_password = ''

# porta para rodar o projeto
env.port = ''

# diretório do sites-enable do nginx
env.nginx_sites_enable_path = '/etc/nginx/sites-enabled'

# copiar as variaveis de cima e jogar no local_settings para substituir
try:
    from local_settings import *
except ImportError:
    pass

# --------------------------------------------------------

prod_server = '{0}@{1}'.format(user, host)
project_path = '/home/'

env.hosts = [prod_server]

# --------------------------------------------------------
# SERVIDOR
# --------------------------------------------------------

def updateserver():

    """Atualiza o servidor"""
    log('Atualiza o servidor')

    update_server()
    upgrade_server()
    update_server()

    resp = raw_input('Deseja atualizar o /etc/nginx/nginx.conf do servidor? [y/n]: ')
    if resp == 'y':
        write_file('nginx_server.conf', '/etc/nginx/nginx.conf')


def newserver():

    """Configurar e instalar todos pacotes necessários para servidor"""
    log('Configurar e instalar todos pacotes necessários para servidor')

    # gera uma chave no servidor para utilizar o comando upload_public_key
    run('ssh-keygen')

    update_server()
    upgrade_server()
    update_server()

    build()
    python()
    nginx()
    uwsgi()

    write_file('nginx_server.conf', '/etc/nginx/nginx.conf')

    log('Reiniciando a máquina')
    reboot()


# --------------------------------------------------------
# INSTALL
# --------------------------------------------------------

def build():
    sudo('yum -y install wget')

def python():
    """Instalando e configurando python"""
    log('Instalando e configurando python')

    with cd(dir_download):
        run('wget http://dl.fedoraproject.org/pub/epel/6Server/x86_64/epel-release-6-8.noarch.rpm')
        run('rpm -Uvh epel-release*rpm')
        run('yum -y groupinstall \'Development Tools\'')
        run('yum -y install zlib-devel libjpeg-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel')
        run('wget https://www.python.org/ftp/python/2.7.6/Python-2.7.6rc1.tar.bz2 --no-check-certificate')
        run('tar xf Python-2.7.6rc1.tar.bz2')
        with cd("Python-2.7.6rc1"):
            run('./configure --prefix=/usr/local')
            run('make && make altinstall')
        run('wget https://pypi.python.org/packages/source/d/distribute/distribute-0.6.49.tar.gz --no-check-certificate')
        run('tar xf distribute-0.6.49.tar.gz')
        with cd('distribute-0.6.49'):
            run('python2.7 setup.py build')
            run('python2.7 setup.py install')
        run('easy_install-2.7 pip')
        run('pip install virtualenv')
    with cd('/usr/lib/'):
        run('ln -s ../../lib64/libz.so.1.2.3 libz.so')
        run('ln -s ../lib64/libjpeg.so libjpeg.so')

def nginx():
    run('yum -y install nginx')
    run('chkconfig --level 2345 nginx on')
    write_file('iptables', '/etc/sysconfig/')
    sudo('/etc/init.d/iptables reload')

def uwsgi():
    run('pip2.7 install uwsgi')


# --------------------------------------------------------
# ACCOUNT
# --------------------------------------------------------

# cria uma account no servidor
def newaccount():
    """Criar uma nova conta do usuário no servidor"""
    log('Criar uma nova conta do usuário no servidor')

    # criando usuario
    if not env.account:
        env.account = raw_input('Digite o nome da conta: ')
    if not env.domain:
        env.domain = raw_input('Digite o domínio do site (sem www): ')
    if not env.language:
        env.language = raw_input('Linguagens disponíveis\n\n1) PYTHON\n2) PHP\n\nEscolha a linguagem [1/2]: ')
        if not env.port and int(env.language) == 1:
            env.port = raw_input('Digite o número da porta: ')
    if not env.mysql_password:
        env.mysql_password = raw_input('Digite a senha do ROOT do MySQL: ')

    # cria usuario no linux
    user_password = create_password(12)
    adduser(env.account, user_password)

    # criar diretório de logs
    with cd('/home/{0}/'.format(env.account)):
        run('mkdir logs')
        run('touch access.log')
        run('touch error.log')

        if int(env.language) == 1:
            run('virtualenv env --no-site-packages')
            write_file('nginx_python.conf', 'nginx.conf')
            write_file('bash_login', '.bash_login')
        else:
            write_file('nginx_php.conf', 'nginx.conf')
            run('mkdir www')

    # cria banco e usuario no banco
    db_password = create_password(12)
    newbase(env.account, db_password)

    # da permissao para o usuario no diretorio
    sudo('chown -R {0}:{0} /home/{0}'.format(env.account))

    nginx_restart()
    nginx_reload()

    # log para salvar no docs
    log('Anotar dados da conta')
    print '\n{0} \nUSUÁRIO senha: {1} \nBANCO senha: {2}'.format(env.account, user_password, db_password)
    print '\n================================================================================'

# deleta uma account no servidor
def delaccount():
    """Deletar conta no servidor"""
    account = raw_input('Digite o nome da conta: ')
    if account:
        if not env.mysql_password:
            env.mysql_password = raw_input('Digite a senha do ROOT do MySQL: ')
        log('Deletando conta {0}'.format(account))
        deluser(account)
        dropbase(account)

# cria usuario no servidor
def adduser(account=None, user_password=None):
    """Criar um usuário no servidor"""

    if not user_password:
        user_password = create_password(12)

    if not account:
        account = raw_input('Digite o nome do usuário: ')

    log('Criando usuário {0}'.format(account))
    sudo('useradd -p $(perl -e \'print crypt($ARGV[0], "password")\' {0}) {1}'.format(user_password, account))
    print '\nSenha usuário: {0}'.format(user_password)
    print '\n================================================================================'

# LINUX - deleta o usuario
def deluser(account=None):
    """Deletar usuário no servidor"""
    if not account:
        account = raw_input('Digite o nome do usuario: ')
    log('Deletando usuário {0}'.format(account))
    sudo('userdel -r {0}'.format(account))

# --------------------------------------------------------
# BANCO DE DADOS
# --------------------------------------------------------

# MYSQL - cria usuario e banco de dados
def newbase(account=None, db_password=None):
    """Criar banco de dados e usuário no servidor"""
    log('Criar banco de dados e usuário no servidor')

    if not db_password:
        db_password = create_password(12)

    if not account:
        account = raw_input('Digite o nome do banco: ')
    log('NEW DATABASE {0}'.format(account))

    # cria acesso para o banco local
    sudo("echo CREATE DATABASE {0} | mysql -u root -p{1}".format(account, env.mysql_password))
    sudo("echo \"CREATE USER '{0}'@'localhost' IDENTIFIED BY '{1}'\" | mysql -u root -p{2}".format(account, db_password, env.mysql_password))
    sudo("echo \"GRANT ALL PRIVILEGES ON {0} . * TO '{0}'@'localhost'\" | mysql -u root -p{1}".format(account, env.mysql_password))

    # cria acesso para o banco remoto
    sudo("echo \"CREATE USER '{0}'@'%' IDENTIFIED BY '{1}'\" | mysql -u root -p{2}".format(account, db_password, env.mysql_password))
    sudo("echo \"GRANT ALL PRIVILEGES ON {0} . * TO '{0}'@'%'\" | mysql -u root -p{1}".format(account, env.mysql_password))

    print '\nSenha gerada para o banco: {0}'.format(db_password)
    print '\n================================================================================'


# MYSQL - deleta o usuario e o banco de dados
def dropbase(account=None):
    """Deletar banco de dados e usuário no servidor"""
    log('Deletando banco de dados e usuário no servidor')
    if not account:
        account = raw_input('Digite o nome do banco: ')
    if not env.mysql_password:
        env.mysql_password = raw_input('Digite a senha do ROOT do MySQL: ')
    sudo("echo DROP DATABASE {0} | mysql -u root -p{1}".format(account, env.mysql_password))
    sudo("echo \"DROP USER '{0}'@'localhost'\" | mysql -u root -p{1}".format(account, env.mysql_password))
    sudo("echo \"DROP USER '{0}'@'%'\" | mysql -u root -p{1}".format(account, env.mysql_password))

# --------------------------------------------------------
# SERVIÇOS - LINUX
# --------------------------------------------------------

# update no servidor
def update_server():
    """Atualizando pacotes no servidor"""
    log('Atualizando pacotes')
    sudo('yum -y update')

# upgrade no servidor
def upgrade_server():
    """Atualizar programas no servidor"""
    log('Atualizando programas')
    sudo('yum -y upgrade')

def reboot():
    """Reinicia o servidor"""
    sudo('reboot')

# NGINX
def nginx_start():
    """Start nginx no servidor"""
    log('start nginx')
    sudo('/etc/init.d/nginx start')


def nginx_stop():
    """Stop nginx no servidor"""
    log('stop nginx')
    sudo('/etc/init.d/nginx stop')


def nginx_restart():
    """Restart nginx no servidor"""
    log('restart nginx')
    sudo('/etc/init.d/nginx restart')


def nginx_reload():
    """Reload nginx no servidor"""
    log('reload nginx')
    sudo('/etc/init.d/nginx reload')

# --------------------------------------------------------
# GLOBAL
# --------------------------------------------------------

def login():
    """Acessa o servidor"""
    if key_filename:
        local("ssh %s -i %s" % (prod_server, key_filename))
    else:
        local("ssh %s" % prod_server)

def upload_public_key():
    """Faz o upload da chave ssh para o servidor"""
    log('Adicionando chave publica no servidor')
    ssh_file = '~/.ssh/id_rsa.pub'
    target_path = '~/.ssh/uploaded_key.pub'
    put(ssh_file, target_path)
    run('echo `cat ~/.ssh/uploaded_key.pub` >> ~/.ssh/authorized_keys && rm -f ~/.ssh/uploaded_key.pub')

def write_file(filename, destination):

    upload_template(
            filename=filename,
            destination=destination,
            template_dir=os.path.join(CURRENT_PATH, 'includes'),
            context=env,
            use_jinja=True,
            use_sudo=True,
            backup=True
        )

# gera senha
def create_password(tamanho=12):
    """Gera uma senha - parametro tamanho"""
    from random import choice
    caracters = '0123456789abcdefghijlmnopqrstuwvxzkABCDEFGHIJLMNOPQRSTUWVXZK_#'
    senha = ''
    for char in xrange(tamanho):
        senha += choice(caracters)
    return senha


def log(message):
    print """
================================================================================
%s
================================================================================
    """ % message
