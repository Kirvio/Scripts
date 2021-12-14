import json
import logging
import logging.handlers
import os

class LoggerConfig(object):
    def __init__(self, config_path):
        try:
            if not config_path \
               or type(config_path) \
               is not str:
                raise Exception("No path to logger config file!")
            else:
                with open(config_path, 'r', encoding='utf-8') as cfg_file:
                    self.__config = json.load(cfg_file)

                self.ch_isEnabled       = self.__config['handlers']['console']['enabled']
                self.ch_level           = self.__config['handlers']['console']['level']
                self.ch_formatter       = self.__config['handlers']['console']['formatter']

                self.fh_isEnabled       = self.__config['handlers']['file']['enabled']
                self.fh_level           = self.__config['handlers']['file']['level']
                self.fh_dir             = self.__config['handlers']['file']['dir']
                self.fh_file            = self.__config['handlers']['file']['file']
                self.fh_formatter       = self.__config['handlers']['file']['formatter']

                if not os.path.exists(self.fh_dir):
                    os.mkdir(self.fh_dir)

        except PermissionError as pe:
            print("You have no permissions to create {} dir. {}".format(self.fh_dir, pe))
        except FileNotFoundError as fnfe:
            print("Config file not found! {}".format(fnfe))
        except Exception as e:
            print(e)

class LoggerFactory(object):
    @staticmethod
    def createLogger(loggerName):
        try:
            loggerConfig = LoggerConfig("/home/belgie/new_parser_belgie/configs/logger.conf")
            logger = logging.getLogger(loggerName)
            logger.setLevel("INFO")
            if not len(logger.handlers):
                if loggerConfig.ch_isEnabled:
                    ch = logging.StreamHandler()
                    ch.setLevel(loggerConfig.ch_level)
                    ch.setFormatter(logging.Formatter(loggerConfig.ch_formatter))
                    logger.addHandler(ch)

                if loggerConfig.fh_isEnabled:
                    fh = logging.FileHandler(os.path.join(loggerConfig.fh_dir, loggerConfig.fh_file))
                    fh.setLevel(loggerConfig.fh_level)
                    fh.setFormatter(logging.Formatter(loggerConfig.fh_formatter))
                    logger.addHandler(fh)

        except PermissionError as pe:
            print("You have no permissions to create {} directory. {}".format(loggerConfig.fh_dir, pe))
        except Exception as e:
            print(e)
        else:
            return logger
