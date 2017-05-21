import os
import sys


def apache_configuration():
    current_user = getuser()
    # os.system("sudo")
    # raw_input("Enter Sudo pw")
    current_user = os.getenv("SUDO_USER")
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


apache_configuration()
