import paramiko 
import time
import os

"""This script is used to transport ready EPG.xmltv file
   to ministra in our server
"""

host = ''
user = ''
secret = ''
port = 22
remotepath = '/home/evandrushenko/xmltv.xml'
localpath = 'D:\\EPG\\xmltv.xml'

# Передача xmltv файла по sftp на сервер
def TransportData(frm, to):
    kak = os.path.isfile(localpath)
    if kak:
        try:
            transport = paramiko.Transport((host, port))
            transport.connect(username = user, password = secret)
            sftp = paramiko.SFTPClient.from_transport(transport)
            # Передача файлов
            sftp.put(frm, to)
            return True
        except (paramiko.SSHException, OSError) as err:
            print(err)
            return err
        finally:
            sftp.close()
            transport.close()
    else:
        print("xmltv файл отсутствует!")
        time.sleep(10)
        return False

# Соединение с сервером по ssh и копирование (sudo) с директории в директорию с министрой
def SSHConnect(SHhost, SHuser, SHpassword, SHport):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname = SHhost, username = SHuser, password = SHpassword, port = SHport)

        chan = ssh.get_transport().open_session()
        chan.get_pty()

        # channel.settimeout(5)
        cmd = 'sudo cp -L /home/evandrushenko/xmltv.xml /opt/docker_deploys/volumes/ministra_epg/_data/'
        chan.exec_command(cmd)
        chan.send(secret + '\n')
        
        time.sleep(3)
        return chan.recv(1024)
    except (paramiko.SSHException, OSError) as err:
        print(err)
        return err
    finally:
        #chan.close()
        ssh.close()

if __name__ == '__main__': 
    ST = TransportData(frm = localpath, to = remotepath)
    print(ST)
    time.sleep(2)
    if ST:
        SH = SSHConnect(SHhost = host, SHuser = user, SHpassword = secret, SHport = port)    
        print(SH)
    else:
        print("Скрипт не выполнился")
