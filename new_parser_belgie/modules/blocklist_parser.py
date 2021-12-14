import json
import os
import time
import hashlib
import sys
from collections import deque
import subprocess
try:
    import xml.etree.ElementTree as ET
    from modules.logger import LoggerFactory
except ImportError as err:
    sys.exit(0)

log = LoggerFactory.createLogger(__name__)

class BlocklistParser(object):

    """Парсит конфигурационный файл с 
       расположением файлов для запрещённых IP адресов"""

    def __init__(self):
        config_path = "/home/belgie/new_parser_belgie/configs"
        try:
            configPath = os.getenv(
                "BLOCKLIST_PARSER",
                os.path.join(config_path, "blocklist_parser.conf")
            )
            if self.__validateConfigPath(configPath):
                self.__config     = self.__readConfig(configPath)
                self.password     = self.__config['dir']['pass']
                self.local_path   = self.__config['dir']['local_path']
                self.old_ip_list  = self.__config['dir']['old_IPs_file']
                self.ip_list      = self.__config['dir']['IPs_file']
                self.old_dns_list = self.__config['dir']['old_DNS_file']
                self.new_dns_list = self.__config['dir']['new_DNS_file']
        except KeyError as ke:
            log.error("Please check your config. {}".format(ke))
        except Exception:
            log.error("Exception occurred", exc_info=True)

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
                    raise Exception("Exception occured while loading json file")
                else:
                    return json_load
            else:
                raise Exception("{} config file is unreadable!".format(configPath))

    def remove_point(self, input):

        """Удаляет ошибочную точку или пробел в конце/начале домена"""

        try:
            for index, string in enumerate(input):
                input[index] = string.strip('. ').replace(" ", "")
        except Exception:
            log.error("Exception occured", exc_info=True)
        else:
            log.info("Все лишние точки и пробелы в конце каждого сайта убраны.")

    def duplicate_check(self, input):

        """Проверка на повторяющиеся элементы"""

        try:
            self.remove_point(input)
            index = 1
            while index < len(input):
                if input[index] in input[:index]:
                    input.pop(index)
                else:
                    index += 1
        except Exception:
            log.error("Exception occured while checking for duplicates", exc_info=True)
        else:
            log.info("Все повторяющиеся копии сайтов удалены.")
            return input

    def parse_files(self):
        try:
            iplist = []
            dnslist = []
            tree = ET.parse(self.local_path)
            root = tree.getroot()
            log.info('Начинаем парсить файл с заблокированными сайтами')
            try:
                for res in root.findall('resource'):
                    ip = res.find('ip').text
                    dns = res.find('dns').text
                    if dns != "-":
                        dnslist.append(dns)
                    ip = str(ip)
                    if ip != "-" and ':' not in ip:
                        iplist.append(ip.strip())
            except ValueError:
                pass
            self._writeIPs(iplist, self.ip_list)
            self._writeIPs(dnslist, self.new_dns_list, ip=0)
        except Exception:
            log.error("Exception occured", exc_info=True)

    def check_hash(self, file):

        """Вычисляет MD5 хэш файла"""

        with open(file, "rb") as f:
            file = f.read()
            file_hash = hashlib.md5(file)
            hash = file_hash.hexdigest()
        return hash

    def check_count(self, file):

        """Считает кол-во строк в файле"""

        with open(file, "rb") as f:
            count = sum(1 for _ in f)
        return count

    def check_dns(self):
        self.parse_files()
        check_DNS = False
        try:
            if os.path.isfile(self.old_dns_list):
                # Вычисляем хэш содержимого старого файла
                old_hash = self.check_hash(self.old_dns_list)
                log.info("Хэш старого файла dns MD5: {}".format(old_hash))
                if os.path.isfile(self.new_dns_list):
                    # Вычисляем хэш содержимого нового файла
                    new_hash = self.check_hash(self.new_dns_list)
                    log.info("Хэш нового файла dns MD5: {}".format(new_hash))
                    try:
                        #if old_hash == new_hash:
                            # Если они идентичны, переходим к следующему этапу 
                            log.info("Новые сайты в список добавлены не были")
                        #else:
                            input("Okay")
                            try:
                                password = self.password+'\n'
                                password = password.encode()
                                # Если нет, копируем файл, проверяем на ошибки, и перезапускаем bind
                                stdout, stderr= subprocess.Popen(['sudo', '-S', 'cp',\
                                                                  '/home/belgie/new_parser_belgie/zones.blacklisted', '/etc/bind/zones/'],\
                                                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,\
                                                                   stderr=subprocess.PIPE).communicate(input=bytes(password))
                                if stderr:
                                    log.error(stderr)
                                    sys.exit(1)
                                else:
                                    input("Копирование файла завершено успешно")
                                    log.info("Копирование завершено")
                                    stdout, stderr = subprocess.Popen(['sudo', '-S', 'named-checkconf'],\
                                                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,\
                                                                        stderr=subprocess.PIPE).communicate(input=bytes(password))
                                    if stderr or stdout:
                                        log.error(stderr, stdout)
                                        sys.exit(1)
                                    else:
                                        input("В файле ошибок не обнаружено")
                                        log.info("Проверка прошла успешно")
                                        stdout, stderr = subprocess.Popen(['sudo', '-S', 'service', 'bind9', 'reload'],\
                                                                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,\
                                                                            stderr=subprocess.PIPE).communicate(input=bytes(password))
                                        if stderr:
                                            log.error(stderr)
                                            sys.exit(1)
                                        else:
                                            input("Перезапуск bind9 прошел успешно")
                                            # log.info("Операция по блокировке днс завершена")
                                            check_DNS = True
                            except subprocess.CalledProcessError as err:
                                log.error('Code: {}, STDERR: {}, STDOUT: {}'.format(err.returncode, err.stderr, err.stdout))
                    except Exception:
                        log.error("Exception occured", exc_info=True)
                    else:
                        # Убираем старый файл и переименовываем новый, после окончания всех операций
                        try:
                            os.remove(self.old_dns_list)
                            os.rename(self.new_dns_list, self.old_dns_list)
                        except OSError:
                            log.error("Exception occured", exc_info=True)
                else:
                    log.error("Не могу найти новый DNS файл, прекращаю выполнение")
                    sys.exit(1)
            else:
                # Если старый файл обнаружен не был, продолжаем выполнение и переименовываем файл
                log.info("Старый днс файл обнаружен не был")
                os.rename(self.new_dns_list, self.old_dns_list)
        except Exception:
            log.error("Exception occured", exc_info=True)
            sys.exit(1)
        else:
            return check_DNS

    def check_IPs(self):
        check_IP = False
        try:
            if os.path.isfile(self.old_ip_list):
                # Подсчет строк в старом файле 
                count_old = self.check_count(self.old_ip_list)
                log.info("Количество строк в старом файле: {}".format(count_old)) # вывести результат
                if os.path.isfile(self.ip_list):
                    # Подсчет строк в новом файле
                    count_new = self.check_count(self.ip_list)
                    log.info("Количество строк в новом файле: {}".format(count_new))
                    try:
                        if count_old == count_new:
                            log.info("Количество строк одинаково")
                            input("Continue")
                        # Если в новом файле больше строк,
                        # Вычисляем разницу n, и находим последние n строк
                        elif count_old > count_new:
                            log.error("Wrong old IP file")
                            sys.exit(1)
                        else:
                            # Если нет парсим новый файл и продолжаем выполнение
                            log.info("Были добавлены новые IP адреса")
                            result = count_new - count_old
                            with open(self.ip_list, "r") as f:
                                ip_adresses = list(deque(f, result))
                            with open('ipadresses.csv', 'w') as fh:
                                log.info('Записываем список новых IP адресов')
                                fh.write("conf\n")
                                for elem in ip_adresses:
                                    fh.write("set firewall group address-group belgie-list address '{}'\n".format(elem.rstrip()))
                                fh.write("commit\nsave\nexit\n")
                            log.info("IP-адреса сайтов записаны")
                            input("Continue")
                            check_IP = True
                    except Exception:
                        log.error("Exception occured", exc_info=True)
                    else:
                        # Убираем старый файл и переименовываем новый, после окончания всех операций
                        try:
                            os.remove(self.old_ip_list)
                            os.rename(self.ip_list, self.old_ip_list)
                        except OSError:
                            log.error("Exception occured", exc_info=True)
                else:
                    log.error("Не могу найти новый IP файл, прекращаю выполнение")
                    sys.exit(1)
            else:
                # Если старый файл обнаружен не был, продолжаем выполнение и переименовываем файл
                log.info("Старый IP файл обнаружен не был")
                os.rename(self.ip_list, self.old_ip_list)
        except Exception:
            log.error("Exception occured", exc_info=True)
            sys.exit(1)
        else:
            return check_IP

    def _writeIPs(self, input, output, ip=1):

        """Записывает полученные данные в файл"""

        try:
            log.info("Проверяем файл на повторяющиеся сайты")
            self.duplicate_check(input)
            with open(output, 'w') as fh:
                if ip == 1:
                    log.info('Записываем IP список')
                    for elem in input:
                        fh.write("{}\n".format(elem))
                    log.info("IP-адреса сайтов записаны")
                else:
                    log.info('Записываем DNS список')
                    for elem in input:
                        fh.write(
                            (
                             " ".join(["zone", "\"{}\"".format(elem), \
                             "{ type master; file \"/etc/bind/zones/db.blacklist\"; check-names ignore; };\n"])
                            )
                        )
                    log.info("Доменные имена сайтов записаны")
        except Exception:
            log.error("Exception occurred", exc_info=True)
