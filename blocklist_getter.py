import json
import os
import time
try:
    import requests
    from modules.logger import LoggerFactory
except ImportError as err:
    print(err)
    time.sleep(10)

log = LoggerFactory.createLogger(__name__)

class BlocklistGetter(object):
    """ищет конфигурационный файл по пути,
       который задан в переменной config_path,
       после парсит этот файл на наличие логина, пароля и т.д.
    """
    def __init__(self):
        config_path = "C:\\PythonProgs\\BlackListParser\\renew_parser_belgie\\configs"
        try:
            configPath = os.getenv(
                "BLOCKLIST_GETTER",
                os.path.join(
                    config_path,
                    "blocklist_getter.conf"
                )
            )

            # если файл прошел проверку
            if self.__validateConfigPath(configPath):

                # спарсить конфигурационный файл на логин и пароль
                self.__config    = self.__readConfig(configPath)
                self.login       = self.__config['belgia']['login']
                self.passwd      = self.__config['belgia']['passwd']
                self.remote_path = self.__config['belgia']['rmt_path']
                self.local_path  = self.__config['dir']['local_path']
        except KeyError as ke:
            log.exception("Please check your config. {}".format(ke))
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
        try:
            with open(configPath, 'r', encoding='utf-8') as cfg_file:
                if cfg_file.readable():
                    try:
                        json_load = json.load(cfg_file)
                    except Exception:
                        log.error("Exception occurred", exc_info=True)
                        time.sleep(10)
                        raise Exception("Exception occured while loading json file")
                else:
                    raise Exception("{} config file is unreadable!".format(configPath))
        except (OSError, IOError):
            log.error("Exception occurred", exc_info=True)
            time.sleep(10)
        else:
            return json_load

    def get_block_list(self):
        """Загружает xml файлик с сайта по ссылке в конфиге"""
        try:
            log.info("Downloading blocklist")
            datad = {
                'name':self.login,
                'pass':self.passwd
            }
            response = requests.post(url=self.remote_path, data=datad, verify=False)
            if response.status_code == 200:
                with open(self.local_path, 'wb') as fh:
                    fh.write(response.content)
                log.info(response.headers['content-type'])
            else:
                log.exception("The was an error while downloading file. Status code is {}".format(response.status_code))
            if os.path.isfile(self.local_path):
                log.info("File successfully downloaded. File path is {}".format(self.local_path))
                input("Press Enter to Continue")
        except Exception:
            log.error("Exception occurred", exc_info=True)
            time.sleep(10)