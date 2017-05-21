import os
import urllib2
import sys
import subprocess
import commands
import shlex
from tempfile import mkstemp
from shutil import move
from getpass import getuser
from pwd import getpwnam

"""This is the installer script for dependencies of Prerequisites for
Apache Airavata.The neccessary components such as PHP Mcrypt,Apache Server
and PGA"""


def internet_on():
    """ This function checks for a working internet connection """
    try:
        urllib2.urlopen("http://www.google.com/")
        return True
    except Exception as e:
        print "Internet connection cannot be eshtablished", e
        sys.exit()




def check_or_install_homebrew():
    current_user = os.getenv("SUDO_USER")
    curr_uid = getpwnam(current_user)[2]
    os.setuid(curr_uid)
    brew_flag = os.system("brew")
    if brew_flag != 256:
        print "Home Brew Not Installed! Installing homebrew"
        hb_call = '/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"'
        os.system(hb_call)
        return 1
    else:
        print '''Homebrew already installed.Continuing with the installation
                of other components'''
        return 0


def mysql_installation():
    """This function installs MySQL through homebrew and sets no-root passwd"""

    os.system("brew install mysql")
    os.system("export PATH=/usr/local/mysql/bin: $PATH")


def php_installation():
    print "Hitting php installation!"
    """This function installs all the required dependencies for the php
    installation"""
    php_version_call = subprocess.check_output('php -v', shell=True)
    if not php_version_call:
        sys.exit("Aborting Installation since PHP Version not found")
    phph_v = int(php_version_call[4]+php_version_call[6])
    os.system("brew tap homebrew/homebrew-php")
    os.system(("brew install php{0}-mcrypt".format(phph_v)))
    print "Finished Installation of PHP and Mcrypt Extension!"
    print "*"*50
    return 1


def apache_configuration():
    current_user = os.getenv("SUDO_USER")
    # os.system("sudo")
    # raw_input("Enter Sudo pw")
    # os.system('sudo su')
    try:
        # apache_user_loc = os.path.join('/etc/apache2/users')
        with open(os.path.join("user_test.conf"), 'w') as user_file:
            dir_text = """<Directory "/Users/username/Sites/">
                            AllowOverride All
                            Options Indexes MultiViews FollowSymLinks
                            Require all granted
                            </Directory>
                        """
            user_file.write(dir_text)
            # os.system("chmod 644 {0}".format("user_test.conf"))
            user_file.close()
        print "Done changing apache user files"
        os.system("exit")
    except Exception as e:
        print e,
        return False
        sys.exit()
    try:
        httpd_file_new = open('temp_config.conf', 'w')
        with open('temp.conf', "r") as httpd_file_old:
            httpd_file_loaders_list = ['LoadModule authz_core_module libexec/apache2/mod_authz_core.so',
            'LoadModule authz_host_module libexec/apache2/mod_authz_host.so',
            'LoadModule userdir_module libexec/apache2/mod_userdir.so',
            'LoadModule include_module libexec/apache2/mod_include.so',
            'LoadModule rewrite_module libexec/apache2/mod_rewrite.so',
            'LoadModule php5_module libexec/apache2/libphp5.so',
            'Include /private/etc/apache2/extra/httpd-userdir.conf']
            for line in httpd_file_old:
                # print line
                if line.startswith("#"):
                    for loader in httpd_file_loaders_list:
                        if loader in line:
                            temp = line[1:]
                            line = temp
                            print line
                httpd_file_new.write(line)
        httpd_file_old.close()
        httpd_file_new.close()
        os.rename('temp_config.conf', current_user+".conf")
    except Exception as e:
        print "Error handling Apache httpd file issues.Please check!"
        print e
        sys.exit()
    print "Finished changing httpd file configurations."
    try:
        temp_httpd_dir = open('temp_httpd_dir.conf', 'w')
        with open('temp_userdir.conf', 'r+') as httpd_user_dir_old:
            for line2 in httpd_user_dir_old:
                if ("Include /private/etc/apache2/users/*.conf")in line2 and line2.startswith("#"):
                    temp2 = line2[1:]
                    line2 = temp2
                    print line2
                temp_httpd_dir.write(line2)
        temp_httpd_dir.close()
        httpd_user_dir_old.close()
        os.rename('temp_httpd_dir.conf', "httpd-userdir.conf")
    except Exception as e:
        print "Unable to fetch httpd_user_dir with the following error", e
        sys.exit()


def install_php_composer():
    state_1 = """php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" """
    if os.system(state_1) == 0:
        state_2 = """ php -r "if (hash_file('SHA384', 'composer-setup.php') === '669656bab3166a7aff8a7506b8cb2d1c292f042046c5a994c43155c0be6190fa0355160742ab2e1c88d40d5be660b410') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;" """
        if os.system(state_2) == 0:
            state_3 = "php composer-setup.php"
            os.system(state_3)
            if os.system(state_3) == 0:
                os.system(''' php -r "unlink('composer-setup.php');" ''')
                os.system("mv composer.phar /usr/local/bin/composer")
                print "The installation of composer is successful."

                return 1
            else:
                print "Third step in composer installation failed"
                sys.exit()
        else:
            print "Unable to install composer.Failed in second step"
            sys.exit()
    else:
        print "The first step in composer installation failed"
        sys.exit()


if __name__ == "__main__":
    install_php_composer()
    apache_configuration()
    mysql_installation()
    check_or_install_homebrew()
    php_installation()
