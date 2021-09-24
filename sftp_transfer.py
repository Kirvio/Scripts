import time
import json
import os
try:
    import paramiko
    from modules.logger import LoggerFactory
except ImportError as exc:
    print(exc)
    time.sleep(10)

log = LoggerFactory.createLogger(__name__)
remotepath = '/home/evandrushenko/zones.blacklisted'
localpath = 'C:\\PythonProgs\\BlackListParser\\renew_parser_belgie\\zones.blacklisted'

class sftp_transer(object):

    def __init__(self):
        config_path = "C:\\PythonProgs\\BlackListParser\\renew_parser_belgie\\configs"
        try:
            configPath = os.getenv(
                "FTP_SESSION",
                os.path.join(config_path, "ftp_session.conf")
            )
            if self.__validateConfigPath(configPath):
                self.__config   = self.__readConfig(configPath)
                self.ftp_host   = self.__config['ftp']['host']
                self.ftp_port   = self.__config['ftp']['port']
                self.ftp_user   = self.__config['ftp']['user']
                self.ftp_pass   = self.__config['ftp']['pass']
        except KeyError as ke:
            log.error("Please check your config. {}".format(ke))
            time.sleep(10)
        except Exception as e:
            log.error(e)
            time.sleep(10)

    def __validateConfigPath(self, configPath):
        if type(configPath) is str \
                            and len(configPath) > 0 \
                            and os.path.exists(configPath) \
                            and os.path.isfile(configPath):
            return True
        else:
            raise Exception("Config path for {} is invalid!".format(self.__class__.__name__))

    def __readConfig(self, configPath):
        with open(configPath, 'r', encoding='utf-8') as cfg_file:
            if cfg_file.readable():
                try:
                    json_load = json.load(cfg_file)
                except Exception:
                    log.error("Exception occurred", exc_info=True)
                    time.sleep(10)
                    raise Exception("Exception occured while loading json file")
                else:
                    return json_load
            else:
                raise Exception("{} config file is unreadable!".format(configPath))

    # Передача zones.blacklisted файла по sftp на сервер
    def TransportData(self, frm, to):
        result = False
        kak = os.path.isfile(localpath)
        if kak:
            try:
                transport = paramiko.Transport((self.ftp_host, self.ftp_port))
                transport.connect(username=self.ftp_user, password=self.ftp_pass)
                sftp = paramiko.SFTPClient.from_transport(transport)

                # Передача файлов
                sftp.put(frm, to)
            except (paramiko.SSHException, OSError) as err:
                log.error(err)
                time.sleep(10)
            else:
                sftp.close()
                transport.close()
                log.info("Файл zones.blacklisted на сервере")
                result = True
            finally:
                return result
        else:
            log.error("xml файл отсутствует!")
            time.sleep(10)

    # Соединение с сервером по ssh и копирование (sudo) с директории в директорию с министрой
    def ConnectToServerViaSSH(self):
        ST = self.TransportData(frm=localpath, to=remotepath)
        if ST:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=self.ftp_host, username=self.ftp_user, \
                            password=self.ftp_pass, port=self.ftp_port)

                chan = ssh.get_transport().open_session()
                chan.get_pty()

                cmd = 'sudo cp -L /home/evandrushenko/zones.blacklisted /etc/bind/zones/'
                chan.exec_command(cmd)
                chan.send(self.ftp_pass + '\n')

                time.sleep(5)
            except (paramiko.SSHException, OSError) as err:
                log.error(err)
                time.sleep(10)
            else:
                ssh.close()
                log.info("Файл перенесён в BIND9")
                input("Press Enter to Continue")
        else:
            log.error("Exception occurred", exc_info=True)
            raise Exception("Problem occurred while connecting to the server")