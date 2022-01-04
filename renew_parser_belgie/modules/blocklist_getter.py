import json
import os
import time
import sys
try:
    import requests
    from modules.logger import LoggerFactory
except ImportError as err:
    sys.exit(1)

log = LoggerFactory.createLogger(__name__)

class BlocklistGetter(object):

    """ищет конфигурационный файл по пути,
       который задан в переменной config_path,
       после парсит этот файл на наличие логина,
       пароля и т.д.
    """

    def __init__(self):
        config_path = "/home/belgie/new_parser_belgie/configs"
        try:
            main_config_path = os.getenv(
                "BLOCKLIST_GETTER",
                os.path.join(
                    config_path,
                    "blocklist_getter.conf"
                )
            )
            # если файл прошел проверку
            if self.__validate_config_path(main_config_path):
                # спарсить конфигурационный(json) файл на логин и пароль
                self.__config    = self.__read_config(main_config_path)
                self.login       = self.__config['belgia']['login']
                self.passwd      = self.__config['belgia']['passwd']
                self.remote_path = self.__config['belgia']['rmt_path']
                self.local_path  = self.__config['dir']['local_path']
        except KeyError as err:
            log.exception("Please check your config. {}".format(err))
        except Exception:
            log.error("Exception occurred", exc_info=True)

    def __validate_config_path(self, config_path):
        if type(config_path) is str \
                            and len(config_path) > 0 \
                            and os.path.exists(config_path) \
                            and os.path.isfile(config_path):
            return True
        else:
            raise Exception("Config path for {} is invalid!".format(self.__class__.__name__))

    def __read_config(self, config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as cfg_file:
                if cfg_file.readable():
                    try:
                        json_load = json.load(cfg_file)
                    except Exception:
                        log.error("Exception occurred", exc_info=True)
                        raise Exception("Exception occured while loading json file")
                else:
                    raise Exception("{} config file is unreadable!".format(config_path))
        except (OSError, IOError):
            log.error("Exception occurred", exc_info=True)
        else:
            return json_load

    def get_block_list(self):

        """Загружает xml файлик с сайта по ссылке в конфиге"""

        try:
            log.info("Загружаем список заблокированных сайтов")
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
                log.exception("Ошибка во время загрузки файла. Код ошибки {}".format(response.status_code))
            if os.path.isfile(self.local_path):
                log.info("Файл успешно загружен. Путь к файлу {}".format(self.local_path))
        except Exception:
            log.error("Exception occurred", exc_info=True)
