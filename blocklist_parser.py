import json
import os
import time
try:
    import xml.etree.ElementTree as ET
    from modules.logger import LoggerFactory
except ImportError as err:
    print(err)
    time.sleep(10)

log = LoggerFactory.createLogger(__name__)

class BlocklistParser(object):

    """Парсит конфигурационный файл с 
       расположением файлов для запрещённых IP адресов"""

    def __init__(self):
        config_path = "C:\\PythonProgs\\BlackListParser\\renew_parser_belgie\\configs"
        try:
            configPath = os.getenv(
                "BLOCKLIST_PARSER",
                os.path.join(config_path, "blocklist_parser.conf")
            )
            if self.__validateConfigPath(configPath):
                self.__config    = self.__readConfig(configPath)
                self.local_path  = self.__config['dir']['local_path']
                self.ip_list     = self.__config['dir']['IPs_file']
                self.dns_list    = self.__config['dir']['DNS_file']
        except KeyError as ke:
            log.error("Please check your config. {}".format(ke))
            time.sleep(10)
        except Exception:
            log.error("Exception occurred", exc_info=True)
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

    def remove_point(self, input):
        try:
            for index, string in enumerate(input):
                if string.endswith('.'):
                    input[index] = string[0:len(string) - 1]
        except Exception:
            log.error("Exception occured while removing points in the end of strings")
        else:
            log.info("All points in the end of strings succesfully removed")

    def duplicate_check(self, input):
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
            time.sleep(10)
        else:
            log.info("All duplicates removed")
            return input

    def blocklist_parser(self):
        """парсит xml файлик на наличие запрещённых IP, DNS и URL"""
        try:
            iplist = []
            dnslist = []
            log.info(os.path.isfile(self.local_path))
            tree = ET.parse(self.local_path)
            root = tree.getroot()
            log.info('Parsing blocklist file')
            for res in root.findall('resource'):
                ip = res.find('ip').text
                dns = res.find('dns').text
                if dns != "-":
                    dnslist.append(dns)
                if ip != "-":
                    iplist.append(str(ip).strip())
            self._writeIPs(iplist, self.ip_list)
            self._writeIPs(dnslist, self.dns_list, ip=0)
        except Exception:
            log.error("Exception occurred", exc_info=True)
            time.sleep(10)
        else:
            input("Press Enter to Continue")

    def _writeIPs(self, input, output, ip=1):
        try:
            log.info("Check for duplicates")
            self.duplicate_check(input)
            log.info('Writing IP or DNS list')
            if os.path.isfile(output):
                os.remove(output)
            with open(output, 'w') as fh:
                if ip == 1:
                    for elem in input:
                        fh.write("{}\n".format(elem))
                    log.info("blocked IP is written")
                else:
                    for elem in input:
                        fh.write(
                            (
                             " ".join(["zone", "\"{}\"".format(elem), \
                             "{ type master; file \"/etc/bind/zones/db.blacklist\"; };\n"])
                            )
                        )
                    log.info("blocked DNS is written")
        except Exception:
            log.error("Exception occurred", exc_info=True)
            time.sleep(10)
