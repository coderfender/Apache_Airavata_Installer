import os
import urllib2
import sys
import subprocess
import commands
import shlex
from tempfile import TemporaryFile
from shutil import move
from getpass import getuser
from pwd import getpwnam
import json
from pprint import pprint


"""This is the installer script for dependencies of Prerequisites for
Apache Airavata.The neccessary components such as PHP Mcrypt,Apache Server
and PGA"""

def check_sudo():
    if not os.getenv('SUDO_USER'):
        print "Run the Installation in sudo mode.\n Exiting installation"
        print "*"*50
        sys.exit()

def internet_on():
    """ This function checks for a working internet connection """
    try:
        urllib2.urlopen("http://www.google.com/")
        return True
    except Exception as e:
        print "Internet connection cannot be eshtablished", e
        sys.exit()


def check_or_install_homebrew(resource):
    current_user = os.getenv("SUDO_USER")
    curr_uid = getpwnam(current_user)[2]
    os.setuid(curr_uid)
    print resource["mac"]["homebrew"]
    print resource["mac"]["homebrew"]["brew_call"]
    brew_flag = os.system(resource["mac"]["homebrew"]["brew_call"])
    if brew_flag != 256:
        print "Home Brew Not Installed! Installing homebrew"
        os.system(resource["mac"]["homebrew"]["brew_install"])

    else:
        print '''Homebrew already installed.Continuing with the installation
                of other components'''


def mysql_installation(resource):
    """This function installs MySQL through homebrew and sets no-root passwd"""
    my_sql_call = resource["mac"]["mysql"]["install_command"]
    os.system(my_sql_call)
    my_sql_path_add = resource["mac"]["mysql"]["export_command"]
    os.system(my_sql_path_add)


def php_installation(resource):
    print "Hitting php installation!"
    """This function installs all the required dependencies for the php
    installation"""
    php_version_check = resource["mac"]["php_install"]["php_v"]
    print (php_version_check)
    php_version_call = subprocess.check_output(php_version_check, shell=True)
    if not php_version_call:
        sys.exit("Aborting Installation since PHP Version not found")
    phph_v = int(php_version_call[4]+php_version_call[6])
    print (phph_v)
    os.system("brew tap homebrew/homebrew-php")
    os.system(("brew install php{0}-mcrypt".format(phph_v)))
    print "Finished Installation of PHP and Mcrypt Extension!"


def apache_configuration(resource):
    current_user = os.getenv("SUDO_USER")
    current_user_conf_file_name = current_user+".conf"
    apache_user_conf = os.path.join(
                    resource["mac"]["apache_config"]["apache_user_location"],
                    current_user_conf_file_name)
    directory_config = resource["mac"]["apache_config"]["dir_text"]
    directory_config_text = directory_config.format(current_user)
    if os.path.exists(apache_user_conf):
        try:
            with open(apache_user_conf, 'r+') as user_file:
                print "The user config file already exists.Updating it!"
                user_file.seek(0)
                user_file.truncate()
                user_file.write(directory_config_text)
                user_file.close()
            print "Changed config for the user {0}".format(current_user)
            os.system("chmod 644 {0}.conf".format(current_user))
        except Exception as e:
            print "Error to opening existing user config file"
            sys.exit()
    else:
        print "File not found.Creating one"
        with open(apache_user_conf, 'w') as user_file:
            print "The user config file does not exist.Creating it!"
            user_file.write(directory_config_text)
            user_file.close()
            os.system("chmod 644 {0}.conf".format(current_user))
        sys.exit()
    print "Updating the config files for the file httpd.conf"
    try:
        httpd_file_old_path = resource["mac"]["apache_config"]["httpd.conf"]
        httpd_temp_file_path = resource["mac"]["apache_config"]["temp_httpd_conf"]
        httpd_file_new = open(httpd_temp_file_path,'w')
        httpd_file_new.truncate()
        httpd_file_new = open(httpd_temp_file_path, 'w')
        with open(httpd_file_old_path, 'r') as httpd_file_old:
            httpd_file_loaders_list = resource["mac"]["apache_config"]["httpd_file_loaders_list"]
            print " updating loaders"         
            for line in httpd_file_old:
                if line.startswith("#"):
                    for loader in httpd_file_loaders_list:
                        if loader in line:
                            temp = line[1:]
                            line = temp
                            print line
                httpd_file_new.writel(line)
        httpd_file_old.close()
        httpd_file_new.close()
        os.remove(httpd_file_old)
        print 1
        os.rename(httpd_file_old.name, "httpd.conf")
    except Exception as e:
        # print "Error handling Apache httpd file issues.Exiting installation!"
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


def install_php_composer(resource):
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
    check_sudo()
    with open("resource.json", 'r') as json_file:
        file_val = json.load(json_file, strict=False)
    print type(file_val)
    # check_or_install_homebrew(file_val)
    # install_php_composer(file_val)
    apache_configuration(file_val)
    # mysql_installation(file_val)
    # php_installation(file_val)
