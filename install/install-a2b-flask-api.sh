#!/bin/bash
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2014 Star2Billing S.L.
#
# The Initial Developer is
# Arezqui Belaid <info@star2billing.com>
#

#
# To download and run the script on your server :
# cd /usr/src/ ; rm install-a2b-flask-api.sh; wget --no-check-certificate https://raw.githubusercontent.com/areski/a2billing-flask-api/master/install/install-a2b-flask-api.sh -O install-a2b-flask-api.sh ; bash install-a2b-flask-api.sh
#

INSTALL_MODE='CLONE'
INSTALL_DIR='/usr/share/a2billing-flask-api'
INSTALL_ENV="a2billing-flask-api"
HTTP_PORT="8008"

export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

#Include general functions
rm bash-common-functions.sh
wget --no-check-certificate https://raw.githubusercontent.com/areski/a2billing-flask-api/master/install/bash-common-functions.sh -O bash-common-functions.sh
source bash-common-functions.sh

#Identify the OS
func_identify_os


#Fuction to create the virtual env
func_setup_virtualenv() {
    echo "This will install virtualenv & virtualenvwrapper"
    echo "and create a new virtualenv : $INSTALL_ENV"

    easy_install virtualenv
    easy_install virtualenvwrapper

    # Enable virtualenvwrapper
    chk=`grep "virtualenvwrapper" ~/.bashrc|wc -l`
    if [ $chk -lt 1 ] ; then
        echo "Set Virtualenvwrapper into bash"
        echo "export WORKON_HOME=/usr/share/virtualenvs" >> ~/.bashrc
        echo "source $SCRIPT_VIRTUALENVWRAPPER" >> ~/.bashrc
    fi

    # Setup virtualenv
    export WORKON_HOME=/usr/share/virtualenvs
    source $SCRIPT_VIRTUALENVWRAPPER

    mkvirtualenv $INSTALL_ENV
    workon $INSTALL_ENV

    echo "Virtualenv $INSTALL_ENV created and activated"
    echo ""
}


#NGINX / SUPERVISOR
func_nginx_supervisor(){
    #Leave virtualenv
    # deactivate
    #Install Supervisor
    # pip install supervisor

    #Nginx
    cp /usr/src/a2billing-flask-api/install/nginx/a2billing_flask_app.conf /etc/nginx/sites-enabled/

    #Configure and Start supervisor
    case $DIST in
        'DEBIAN')
            cp /usr/src/a2billing-flask-api/install/supervisor/supervisord_a2billing_flask_api.conf /etc/supervisor/conf.d/
        ;;
        'CENTOS')
            #TODO: support CentOS

            # cp /usr/src/a2billing-flask-api/install/supervisor/centos/supervisord /etc/init.d/supervisor
            # chmod +x /etc/init.d/supervisor
            # chkconfig --levels 235 supervisor on
            # cp /usr/src/a2billing-flask-api/install/supervisor/centos/supervisord.conf /etc/supervisord.conf
            # mkdir -p /etc/supervisor/conf.d
            # cp /usr/src/a2billing-flask-api/install/supervisor/gunicorn_a2billing_flask_api.conf /etc/supervisor/conf.d/
            # mkdir /var/log/supervisor/
        ;;
    esac
    #Restart
    /etc/init.d/supervisor stop; sleep 2; /etc/init.d/supervisor start
    /etc/init.d/nginx restart
}


#Configure Logs files and logrotate
func_prepare_logger() {
    echo ""
    echo "Prepare logger..."

    mkdir /var/log/a2billing-flask-api/
    touch /var/log/a2billing-flask-api/err-apache-a2billing_flask_api.log
    touch /var/log/a2billing-flask-api/a2billing_flask_api.log
    chown -R $APACHE_USER:$APACHE_USER /var/log/a2billing-flask-api

    rm /etc/logrotate.d/a2billing_flask_api
    touch /etc/logrotate.d/a2billing_flask_api
    echo '
/var/log/a2billing-flask-api/*.log {
        daily
        rotate 10
        size = 50M
        missingok
        compress
    }
'  > /etc/logrotate.d/a2billing_flask_api

    logrotate /etc/logrotate.d/a2billing_flask_api
}


#Function to install Frontend
func_install() {
    echo ""
    echo "We will now install a2billing-flask-api on your server"
    echo "======================================================"
    echo ""

    #python setup tools
    echo "Install dependencies and Python modules..."
    echo ""
    apt-get -y install python-setuptools python-dev build-essential git-core mercurial gawk
    easy_install pip
    apt-get -y install libapache2-mod-python libapache2-mod-wsgi
    apt-get -y install libmysqld-dev
    apt-get -y install nginx supervisor
    
    case $DIST in
        'DEBIAN')
            apt-get -y install python-setuptools python-dev build-essential git-core mercurial gawk
            easy_install pip
            apt-get -y install libapache2-mod-python libapache2-mod-wsgi
            apt-get -y install libmysqld-dev
            apt-get -y install nginx supervisor
        ;;
        'CENTOS')
            if [ "$INSTALLMODE" = "FULL" ]; then
                yum -y update
            fi
            yum -y install autoconf automake bzip2 cpio curl curl-devel curl-devel expat-devel fileutils gcc-c++ gettext-devel gnutls-devel libjpeg-devel libogg-devel libtiff-devel libtool libvorbis-devel make ncurses-devel nmap openssl openssl-devel openssl-devel perl patch unzip wget zip zlib zlib-devel policycoreutils-python

            if [ ! -f /etc/yum.repos.d/rpmforge.repo ];
                then
                    # Install RPMFORGE Repo
                    if [ $KERNELARCH = "x86_64" ]; then
                        rpm -ivh http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.2-2.el6.rf.x86_64.rpm
                    else
                        rpm -ivh http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.2-2.el6.rf.i686.rpm
                    fi
            fi

            yum -y --enablerepo=rpmforge install git-core

            #Install epel repo for pip and mod_python
            if [ $KERNELARCH = "x86_64" ]; then
                rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-7.noarch.rpm
            else
                rpm -ivh http://dl.fedoraproject.org/pub/epel/6/i386/epel-release-6-7.noarch.rpm
            fi

            # disable epel repository since by default it is enabled.
            sed -i "s/enabled=1/enable=0/" /etc/yum.repos.d/epel.repo
            yum -y --enablerepo=epel install python-pip mod_python python-setuptools python-tools python-devel mercurial mod_wsgi libevent libevent-devel
        ;;
    esac

    #Create and enable virtualenv
    func_setup_virtualenv

    echo "Install a2billing-flask-api..."
    cd /usr/src/
    rm -rf a2billing-flask-api

    #Configure Logs files and logrotate
    func_prepare_logger

    case $INSTALL_MODE in
        'CLONE')
            git clone git://github.com/areski/a2billing-flask-api.git
        ;;
    esac

    # Copy files
    cp -rf /usr/src/a2billing-flask-api/a2billing_flask_api $INSTALL_DIR

    # Update Secret key
    echo "Update Secret Key..."
    RANDPASSW=`</dev/urandom tr -dc A-Za-z0-9| (head -c $1 > /dev/null 2>&1 || head -c 50)`
    sed -i "s/THE_SECRET_KEY/$RANDPASSW/g" /usr/share/a2billing-flask-api//usr/share/a2billing_flask_api.py

    #Install depencencies
    easy_install -U distribute
    echo "Install requirements..."
    for line in $(cat /usr/src/a2billing-flask-api/requirements.txt)
    do
        pip install $line
    done

    #Fix permission on python-egg
    mkdir $INSTALL_DIR/.python-eggs

    #Create admin user
    python /usr/share/a2billing-flask-api/a2billing_flask_api.py

    #Configure Supervisor and Nginx
    func_nginx_supervisor

    echo ""
    echo "*************************************************************"
    echo "Congratulations, A2Billing-Flask-API Server is now installed!"
    echo "*************************************************************"
    echo ""
    echo ""
    echo "You should now edit /usr/share/a2billing-flask-api/a2billing_flask_api.py"
    echo "and enter the right DB settings to connect to your A2Billing Database"
    echo "See the file /etc/a2billing.conf"
    echo ""
    echo "Example of common settings:"
    echo ""
    echo "DATABASE = {"
    echo "    'name': 'a2billing14',"
    echo "    'engine': 'peewee.MySQLDatabase',"
    echo "    'user': 'a2bdbuser',"
    echo "    'passwd': 'a2bdbpassw',"
    echo "}"
    echo ""
    echo "Restart Apache:"
    echo "/etc/init.d/apache2 restart"
    echo ""
    echo "Admin Panel is provided which can be accessed at http://<ip_address>:8008/admin/"
    echo "Now you can access the admin site and log-in with: admin / admin"
    echo ""
    echo "To create a new admin user refer to the README.rst:"
    echo "https://github.com/areski/a2billing-flask-api/blob/master/README.rst#create-an-admin-user"
    echo ""
    echo ""
}

#Run install
func_install
