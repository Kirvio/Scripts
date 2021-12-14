import time
import json
import os
import sys
try:
    import paramiko
    from modules.logger import LoggerFactory
except ImportError as exc:
    print(exc)
    time.sleep(10)

log = LoggerFactory.createLogger(__name__)

class sftp_transer(object):

    def __init__(self):
        config_path = "/home/belgie/new_parser_belgie/configs"
        try:
            path_to_config = os.getenv(
                "SSH_SESSION",
                os.path.join(config_path, "ssh_session.conf")
            )
            if self.__validate_config_path(path_to_config):
                self.__config   = self.__read_config(path_to_config)
                self.ftp_host   = self.__config['ssh']['host']
                self.ftp_port   = self.__config['ssh']['port']
                self.ftp_user   = self.__config['ssh']['user']
                self.ftp_pass   = self.__config['ssh']['pass']
        except KeyError as ke:
            log.error("Please check your config. {}".format(ke))
        except Exception as e:
            log.error(e)

    def __validate_config_path(self, path_to_config):
        if type(path_to_config) is str \
                            and len(path_to_config) > 0 \
                            and os.path.exists(path_to_config) \
                            and os.path.isfile(path_to_config):
            return True
        else:
            raise Exception("Config path for {} is invalid!".format(self.__class__.__name__))

    def __read_config(self, path_to_config):
        with open(path_to_config, 'r', encoding='utf-8') as cfg_file:
            if cfg_file.readable():
                try:
                    json_load = json.load(cfg_file)
                except Exception:
                    log.error("Exception occurred", exc_info=True)
                    raise Exception("Exception occured while loading json file")
                else:
                    return json_load
            else:
                raise Exception("{} config file is unreadable!".format(path_to_config))

    def get_ssh_connection(self, ssh_machine, ssh_username, ssh_password, ssh_port):

        """Устанавливает соединение по ssh"""

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ssh_machine, username=ssh_username,
                       password=ssh_password, port=ssh_port, timeout=10)
        return client

    def filter_parameters(self, conn, cmd):

        """Посылает команды на выполнение и делает проверку на вывод"""

        time.sleep(1)
        try:
            stdin, stdout, stderr = conn.exec_command(command=cmd)
            stdin.flush()
            err  = ''
            for line in stderr:
                err = line.strip('\n')
            if len(err) > 0:
                log.error(err)
                conn.close()
                sys.exit(0)
        except Exception:
            log.error("Exception occurred", exc_info=True)

    def connect_to_server(self):

        """Для соединения с Vyatta и выполнения команд на блокировку"""

        config_prefix = "/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper"
        password      = self.ftp_pass
        host          = self.ftp_host
        user          = self.ftp_user
        port          = self.ftp_port
        conn          = self.get_ssh_connection(ssh_machine=host, ssh_username=user, \
                                                ssh_password=password, ssh_port=port)
        if conn:
            with open("/home/belgie/new_parser_belgie/ipadresses.csv", 'r') as file:
                array = [row.strip() for row in file]
            try:
                # Establish connection to server over current
                for cmd in array:
                    self.filter_parameters(conn=conn, cmd="{} {}".format(config_prefix, cmd))
            except (paramiko.SSHException, OSError) as err:
                log.error(err)
            finally:
                conn.close()
        else:
            log.error("Exception occurred", exc_info=True)
            raise Exception("Problem occurred while connecting to the server")
