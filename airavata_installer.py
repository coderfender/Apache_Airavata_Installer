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
import zipfile


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
                print "The user config file already exists.Updating it!\n"
                user_file.seek(0)
                user_file.truncate()
                user_file.write(directory_config_text)
                user_file.close()
            print "Changed config for the user {0}\n".format(current_user),
            os.system("chmod 644 {0}.conf".format(current_user))
        except Exception as e:
            print "Error to opening existing user config file\n"
            sys.exit()
    else:
        print "File not found.Creating one"
        with open(apache_user_conf, 'w') as user_file:
            print "The user config file does not exist.Creating it!\n",
            user_file.write(directory_config_text)
            user_file.close()
            os.system("chmod 644 {0}.conf".format(current_user))
        sys.exit()
    print "Updating the config for the file httpd.conf\n",
    try:
        httpd_file_folder = resource["mac"]["apache_config"]["httpd.conf_folder"]
        httpd_file_old_path = os.path.join(httpd_file_folder,
                                            "httpd.conf")
        print httpd_file_old_path
        httpd_temp_file_path = os.path.join(httpd_file_folder,
                                            "temp_httpd_conf")
        print httpd_temp_file_path
        httpd_file_new = open(httpd_temp_file_path, 'w')
        httpd_file_new.truncate()
        with open(httpd_file_old_path, 'r') as httpd_file_old:
            httpd_file_loaders_list = resource["mac"]["apache_config"]["httpd_file_loaders_list"]
            for line in httpd_file_old.readlines():
                if line.startswith("#"):
                    for loader in httpd_file_loaders_list:
                        if loader in line:
                            print line
                            temp = line[1:]
                            line = temp
                            print line
                httpd_file_new.write(line)
        httpd_file_old.close()
        httpd_file_new.close()
        os.rename(httpd_file_old.name,
                os.path.join(httpd_file_folder, "httpd_default.conf"))
        os.rename(httpd_file_new.name,
                os.path.join(httpd_file_folder, "httpd.conf"))
    except Exception as e:
        print "Error handling Apache httpd file issues.Exiting installation!"
        print e
        sys.exit()
    print "Finished changing httpd file configurations."
    try:
        print "Changing httpd_userdir"
        config_statement = resource["mac"]["apache_config"]["httpd_userdir_conf"]
        httpd_userdir_folder_path = resource["mac"]["apache_config"]["httpd_userdir_conf_path"]
        httpd_userdir_conf_new = os.path.join(httpd_userdir_folder_path,
                                             "httpd-userdir_temp.conf")
        print httpd_userdir_conf_new
        temp_httpd_dir = open(httpd_userdir_conf_new, 'w')
        with open(os.path.join(httpd_userdir_folder_path,"httpd-userdir.conf"),
                    'r+') as httpd_user_dir_old:
            for line2 in httpd_user_dir_old.readlines():
                config_statement = resource["mac"]["apache_config"]["httpd_userdir_conf"]
                if config_statement in line2 and line2.startswith("#"):
                    print line2
                    temp2 = line2[1:]
                    line2 = temp2
                    print line2
                temp_httpd_dir.write(line2)
        temp_httpd_dir.close()
        httpd_user_dir_old.close()
        default_config = os.path.join(httpd_userdir_folder_path,
                                      "httpd_user_dir_default.conf")
        os.rename(httpd_user_dir_old.name, default_config)
        os.rename(temp_httpd_dir.name, httpd_user_dir_old.name)
    except Exception as e:
        print "Unable to fetch httpd_user_dir with the following error", e
        sys.exit()


def install_php_composer(resource):
    php_composer_install_commands = resource["mac"]["composer_installer"]
    for command in php_composer_install_commands:
        os.system(command)
    composer_global_path_add = resource["mac"]["composer_global"]
    os.system(composer_global_path_add)


def php_my_admininstall(resource):
    php_install_curl_command = resource["mac"]["php_myadmin_install"]
    current_user = os.getenv("SUDO_USER")
    url = urllib2.urlopen(php_install_curl_command)
    dir_location_php_myadmin = "/Users/{0}/Sites".format(current_user)
    php_name_zip = os.path.basename(url.geturl())
    with open(php_name_zip, "wb+") as temp_file:
        temp_file.write(url.read())
        php_unzipped = zipfile.ZipFile(temp_file, 'r')
        p = php_unzipped.extractall(path=dir_location_php_myadmin)
        temp_file.close()
        php_unzipped.close()

    php_config_directory = os.path.join(dir_location_php_myadmin,
                                        php_name_zip[:-4], "config")
    config_path = os.path.join(dir_location_php_myadmin, php_name_zip[:-4],
                               'config')
    if not os.path.exists(config_path):
        os.mkdir(os.path.join(dir_location_php_myadmin, php_name_zip[:-4],
                              'config'))


def airavata_repo(resource):
    apache_airavata_def_path = resource["mac"]["airavata"]["default_path"]
    airavata_git_repo_url = resource["mac"]["airavata"]["git_repo"]
    os.chdir(apache_airavata_def_path)
    print "Cloning from the Git repo URL + \n" + airavata_git_repo_url
    url_respo = urllib2.urlopen(airavata_git_repo_url)
    airavata_repo_name = (url_respo.geturl())
    print airavata_repo_name.split("/")[4]
    airavata_loc = os.path.join(apache_airavata_def_path, airavata_repo_name)
    with open(airavata_repo_name.split("/")[4]+".zip", "wb+") as temp_file2:
        temp_file2.write(url_respo.read())
        airavata_unzipped = zipfile.ZipFile(temp_file2, 'r')
        unzip_file = airavata_unzipped.extractall(path=apache_airavata_def_path)
        temp_file2.close()
        airavata_unzipped.close()


if __name__ == "__main__":
    try:
        with open("resource.json", 'r') as json_file:
            file_val = json.load(json_file, strict=False)
    except IOError as e:
        print "Unable to fetch resources.json file.Aborting installation"
        sys.exit()
    except Exception as e:
        print "Unknown exception occured.Exiting the installation \n ", e
        sys.exit()
    check_sudo()
    php_my_admininstall(file_val)
    airavata_repo(file_val)
    apache_configuration(file_val)
    check_or_install_homebrew(file_val)
    install_php_composer(file_val)
    php_installation(file_val)
    mysql_installation(file_val)
