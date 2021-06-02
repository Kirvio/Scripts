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
epg_path = 'D:/EPG/'
archive_path = 'C:/Users/evandrushenko/Downloads/epg.xml.gz'

def Remove(EnterPath, EnterFile):
    path = os.path.join(os.path.abspath(\
                        os.path.dirname(EnterPath)), EnterFile)
    os.remove(path)

def Download(url_, path_):
    http = PoolManager()
    r = http.request('GET', url_, preload_content=False)

    with open(path_, 'wb') as out:
        while True:
            data = r.read(1024)
            if not data:
                break
            out.write(data)
    print('EPG Downloaded')
    r.release_conn()

def Extract_archive(url_, download_path, file_path):
    Download(url_, download_path)
    with gzip.open(download_path, 'rb') as archive_:
        with open(file_path, 'wb') as file_:
            shutil.copyfileobj(archive_, file_)
            print('all done')

def MainFunction():     
    try:
        exist_file = os.path.isfile(archive_path)
        full_path = '/'.join([epg_path, 'epg.xml'])
        exist_archive = os.path.isfile(full_path)
        result = False
        if exist_archive and exist_file:   
            Remove(archive_path, EnterFile = 'epg.xml.gz')
            (os.remove(file.path) for file in os.scandir(epg_path))
            time.sleep(0.3)
            Extract_archive(url, archive_path, full_path)
            result = True
        elif exist_file and not exist_archive:
            Remove(archive_path, EnterFile = 'epg.xml.gz')
            time.sleep(0.3)
            Extract_archive(url, archive_path, full_path)
            result = True
        elif exist_archive and not exist_file:     
            (os.remove(file.path) for file in os.scandir(epg_path))
            time.sleep(0.3)
            Extract_archive(url, archive_path, full_path)
            result = True       
        else:
            Extract_archive(url, archive_path, full_path)
            result = True
    except (Exception, OSError) as err:
        print(err)
        result = False
        raise
    finally:
        return result

if __name__ == '__main__':
    MF = MainFunction()
    if MF:
        os.startfile('D:/Network/КИТ Интернет телепрограмма/КИТ Интернет телепрограмма.exe')
    else: 
        print('Ошибка')
