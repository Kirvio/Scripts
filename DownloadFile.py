from urllib3 import PoolManager
import shutil
import time
import gzip
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
    http = PoolManager()
    r = http.request('POST', url_, preload_content=False)

    _recv_buffer = b''
    result = False
    try:
        with open(path_, 'wb') as out:
            while True:
                try:
                    data = r.read(2048)
                    if not data:
                        break
                except (Exception, IOError) as exc:
                    print(exc)
                    time.sleep(20)
                    break
                else:
                    out.write(_recv_buffer)
    except (Exception, OSError) as exc:
        print(exc)
        time.sleep(20)
    else:
        print('Архив с EPG загружен')
        result = True
    finally:
        r.release_conn()
        yield result

def Extract_archive(url_, download_path, file_path):
    if next(Download(url_, download_path)) is True:
        try:
            with gzip.open(download_path, 'rb') as archive_,\
                    open(file_path, 'wb') as file_:
                        shutil.copyfileobj(archive_, file_)
        except (Exception, OSError) as exc:
            print(exc)
            time.sleep(20)
        else:
            print('Файл с EPG извлечён из архива')
    else:
        print('Ошибка при загрузке файла с ЕПГ')

def MainFunction():
    try:
        exist_archive = os.path.isfile(archive_path)
        full_path = '\\'.join([epg_path, 'epg.xml'])
        exist_file = os.path.isfile(full_path)
        result = False
    except (Exception, OSError) as exc:
        print(exc)
        time.sleep(20)
    else:
        if exist_archive and exist_file:
            try:
                Remove(archive_path, EnterFile = 'epg.xml.gz')
                [os.remove(file.path) for file in os.scandir(epg_path)]
                time.sleep(1)
                Extract_archive(url, archive_path, full_path)
            except (Exception, OSError) as exc:
                print(exc)
                time.sleep(20)
            else:
                result = True
        elif exist_file and not exist_archive:
            try:
                [os.remove(file.path) for file in os.scandir(epg_path)]
                Extract_archive(url, archive_path, full_path)
                time.sleep(1)
            except (Exception, OSError) as exc:
                print(exc)
                time.sleep(20)
            else:
                result = True
        elif exist_archive and not exist_file:
            try:
                Remove(archive_path, EnterFile = 'epg.xml.gz')
                time.sleep(1)
                Extract_archive(url, archive_path, full_path)
            except (Exception, OSError) as exc:
                print(exc)
                time.sleep(20)
            else:
                result = True
        else:
            Extract_archive(url, archive_path, full_path)
            result = True
    finally:
        yield result

if __name__ == '__main__':
    MF = MainFunction()
    if next(MF) is True:
        os.startfile('D:/Network/КИТ Интернет телепрограмма/КИТ Интернет телепрограмма.exe')
    else:
        print('Ошибка')
