import logging
import time
import sys
import os
try:
    import paramiko
except ImportError as exc:
    print(exc)
    time.sleep(20)

"""
Скрипт закидывает с хоста (сначала на сервер,
потом в министру) готовый xmltv.xml файл
по ssh. Для передачи файлов используется
paramiko.Transport(sftp), для подключения
по ssh paramiko.SSHClient()
"""

remotepath = '/home/evandrushenko/xmltv.xml'
localpath = 'D:/EPG/xmltv.xml'

# Передача xmltv файла по sftp на сервер
def TransportData(frm, to, host='', port=22,\
                  SSHuser='', SSHsecret=''):
    result = False
    kak = os.path.isfile(localpath)
    if kak:
        try:
            transport = paramiko.Transport((host, port))
            transport.connect(username=SSHuser, password=SSHsecret)
            sftp = paramiko.SFTPClient.from_transport(transport)

            # Передача файлов
            sftp.put(frm, to)
        except (paramiko.SSHException, OSError) as err:
            print(err)
            time.sleep(20)
        else:
            sftp.close()
            transport.close()
            log.info("xml файл с EPG на сервере")
            result = True
        finally:
            return result
    else:
        print("xmltv файл отсутствует!")
        time.sleep(10)

# Соединение с сервером по ssh и копирование (sudo) с директории в директорию с министрой
def SSHConnect(SHhost='172.16.100.54', SHport=22,\
               SHuser='evandrushenko', SHpassword='1234567Andr'):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=SHhost, username=SHuser, \
                    password=SHpassword, port=SHport)

        chan = ssh.get_transport().open_session()
        chan.get_pty()

        cmd = 'sudo cp -L /home/evandrushenko/xmltv.xml /opt/docker_deploys/volumes/ministra_epg/_data/'
        chan.exec_command(cmd)
        chan.send(SHpassword + '\n')

        time.sleep(5)
    except (paramiko.SSHException, OSError) as err:
        print(err)
        time.sleep(20)
    else:
        ssh.close()
        log.info("Файл перенесён в докер")

if __name__ == '__main__': 
    try:
        log = logging.getLogger(__name__)
        log.setLevel(logging.INFO)
        f_format = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        handler.setFormatter(f_format)
        log.addHandler(handler)
    except Exception as exc:
        print(exc)
        time.sleep(20)
    else:
        ST = TransportData(frm=localpath, to=remotepath)
        time.sleep(2)
        if ST:
            SH = SSHConnect()
            time.sleep(2)
        else:
            log.info("Скрипт не выполнился")
            time.sleep(2)
