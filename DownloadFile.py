import requests
import logging
import shutil
import time
import gzip
import sys
import os

"""
Скрипт скачивает ЕПГ по ссылке с сайта(ссылка открывается в браузере)
и разархивирует его в указанную директорию
"""

url = 'https://iptvx.one/EPG'
epg_path = 'D:\\EPG'
archive_path = 'C:\\Users\\evandrushenko\\Downloads\\epg.xml.gz'

def Remove(EnterPath, EnterFile):
    path = os.path.join(os.path.abspath(\
                        os.path.dirname(EnterPath)), EnterFile)
    os.remove(path)

def Download(url_, path_):
    try:
        r = requests.get(url_)
        if r.status_code != 200:
            result = False
        else:
            with open(path_, 'wb') as out:
                try:
                    out.write(r.content)
                except (Exception, IOError):
                    log.error("Exception occurred", exc_info=True)
                    time.sleep(20)
                else:
                    log.info('Архив с EPG загружен')
                    result = True
    except (Exception, OSError):
        log.error("Exception occurred", exc_info=True)
        time.sleep(20)
    finally:
        yield result

def Extract_archive(url_, download_path, file_path):
    if next(Download(url_, download_path)):
        try:
            with gzip.open(download_path, 'rb') as archive_,\
                      open(file_path, 'wb') as file_:
                          shutil.copyfileobj(archive_, file_)
        except (Exception, OSError):
            log.error("Exception occurred", exc_info=True)
            time.sleep(20)
        else:
            log.info('Файл с EPG извлечён из архива')
    else:
        log.info('Ошибка при загрузке файла с ЕПГ')

def MainFunction():
    try:
        exist_archive = os.path.isfile(archive_path)
        full_path = '\\'.join([epg_path, 'epg.xml'])
        exist_file = os.path.isfile(full_path)
        result = False
    except (Exception, OSError):
        log.error("Exception occurred", exc_info=True)
        time.sleep(20)
    else:
        if exist_archive and exist_file:
            try:
                Remove(archive_path, EnterFile = 'epg.xml.gz')
                [os.remove(file.path) for file in os.scandir(epg_path)]
                time.sleep(1)
                Extract_archive(url, archive_path, full_path)
            except (Exception, OSError):
                log.error("Exception occurred", exc_info=True)
                time.sleep(20)
            else:
                result = True
        elif exist_file and not exist_archive:
            try:
                [os.remove(file.path) for file in os.scandir(epg_path)]
                Extract_archive(url, archive_path, full_path)
                time.sleep(1)
            except (Exception, OSError):
                log.error("Exception occurred", exc_info=True)
                time.sleep(20)
            else:
                result = True
        elif exist_archive and not exist_file:
            try:
                Remove(archive_path, EnterFile = 'epg.xml.gz')
                time.sleep(1)
                Extract_archive(url, archive_path, full_path)
            except (Exception, OSError):
                log.error("Exception occurred", exc_info=True)
                time.sleep(20)
            else:
                result = True
        else:
            Extract_archive(url, archive_path, full_path)
            result = True
    finally:
        yield result

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
        MF = MainFunction()
        if next(MF):
            os.startfile('D:/Network/КИТ Интернет телепрограмма/КИТ Интернет телепрограмма.exe')
            input("Нажмите Enter для выхода.")
        else:
            log.info('Ошибка')
            time.sleep(20)
