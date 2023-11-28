import paramiko
import sys
import time
import logging


class Switch:
    _ssh_client = paramiko.SSHClient()
    _ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def __init__(self, ip, switch_type, location, hostname, username, password, port):
        logging.basicConfig(format=u'%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO,
                            filename=u'/var/log/configs_sync.log')
        self._ip = ip
        self._hostname = hostname
        self._switch_type = switch_type
        self._location = location
        self._username = username
        self._password = password
        self._port = port
        self._commands = list()

    @property
    def ip(self):
        return self._ip

    @property
    def switch_type(self):
        return self._switch_type

    @property
    def hostname(self):
        return self._hostname

    @property
    def location(self):
        return self._location

    def add_command(self, command):
        if command:
            self._commands.append(command.strip())
        else:
            raise ValueError

    def _gen_conf_file_name(self, text):
        result = ""
        text = text.strip()
        for ch in text:
            if ch == '#':
                break
            else:
                result += ch
        return result + ".cfg"

    def _get_command_number(self, cmd):
        if len(self._commands) > 0:
            i = 0
            while i < len(self._commands):
                if self._commands[i].find(cmd.strip()) > -1:
                    return i
            return -1
        else:
            return -1

    def _print_and_log(self, text, is_next_line):
        if text:
            if is_next_line:
                print(text, flush=True)
                logging.info(text)
            else:
                print(text, end='', flush=True)
                logging.info(text)
        else:
            raise ValueError

    def print_info(self):
        print("Host: " + self._ip)
        print(self.switch_type)
        print(self._hostname)
        print(self._username)

    def execute(self):
        try:
            logging.info("\n")
            self._print_and_log("Connecting to " + self._ip + "(" + self._switch_type + ")... ", False)
            self._ssh_client.connect(hostname=self._ip, username=self._username,
                                      password=self._password, port=self._port,
                                      look_for_keys=False, allow_agent=False, timeout=30)
            logging.info("Connected to " + self._ip)
            self._print_and_log("done!", True)

            with self._ssh_client.invoke_shell() as ssh:
                ssh.send('\n')
                ssh.send('\n')
                time.sleep(.5)
                ssh.recv(10000).decode('utf-8')

                if not self._hostname:
                    self._print_and_log("Detecting hostname for " + self._ip + "... ", False)
                    ssh.send('\n')
                    time.sleep(.5)
                    self._hostname = self._gen_conf_file_name(ssh.recv(500).decode('utf-8'))
                    self._print_and_log("done!", True)
                else:
                    self._print_and_log("Using hostname " + self._hostname + " for host " + self._ip, True)
                    self._hostname += ".cfg"

                number = self._get_command_number("copy")
                if number > -1:
                    self._commands[number] += self._hostname

                self._print_and_log("Copying running-config from " + self._ip + "... ", False)
                for i in range(len(self._commands)):
                    #print(self._commands[i])
                    logging.debug(self._commands[i])
                    if i == len(self._commands)-1:
                        ssh.send(self._commands[i] + '\n')
                        time.sleep(8)
                    else:
                        ssh.send(self._commands[i] + '\n')
                        time.sleep(.5)
                    cmd_result = ssh.recv(5000).decode('utf-8')
                    logging.debug(cmd_result)
                self._print_and_log("done!", True)

        except TimeoutError as ex:
            logging.error(ex)
        except KeyboardInterrupt:
            print("Ctrl+C interruption detected!")
            sys.exit(0)
        except Exception as ex:
            logging.critical(ex)
        finally:
            self._ssh_client.close()
            logging.info("Connection to " + self._ip + " has been closed")
