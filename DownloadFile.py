import webbrowser
import patoolib
import time
import os

"""
Скрипт скачивает ЕПГ по ссылке с сайта(ссылка открывается в браузере)
и разархивирует его в указанную директорию
"""

url = 'https://iptvx.one/EPG'
DirPath = 'D:\\EPG\\'
IncPath = 'C:\\Users\\evandrushenko\\Downloads\\epg.xml.gz'
WebBrwser = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'

def RMFunct(EnterPath, EnterFile):
    path = os.path.join(os.path.abspath(os.path.dirname(EnterPath)), EnterFile)
    os.remove(path)

def WebFunction(WebBrowser, Nurl):
    webbrowser.register('Chrome', None, webbrowser.BackgroundBrowser(WebBrowser))
    webbrowser.get('Chrome').open(Nurl)
    time.sleep(4)

def MeinLeben():
    WebFunction(WebBrwser, url)
    time.sleep(4)
    patoolib.extract_archive(IncPath, outdir = DirPath)

def MainFunction():     
    try:
        kek = os.path.isfile(IncPath)
        FilePath = '\\'.join([DirPath, 'epg.xml'])
        kak = os.path.isfile(FilePath)
        if kak and kek:   
            RMFunct(IncPath, EnterFile = 'epg.xml.gz')
            [os.remove(file.path) for file in os.scandir(DirPath)]
            time.sleep(0.3)
            MeinLeben()
            return True
        elif kek and not kak:
            RMFunct(IncPath, EnterFile = 'epg.xml.gz')
            time.sleep(0.3)
            MeinLeben()
            return True
        elif kak and not kek:

            # os.scandir метод для сканирование файлов в директории и os.remove для их удаления        
            [os.remove(file.path) for file in os.scandir(DirPath)]
            time.sleep(0.3)
            MeinLeben()          
            return True
        else:
            MeinLeben()
            return True
    except (webbrowser.Error, Exception, OSError) as err:
        print(err)
    else:
        return True

if __name__ == '__main__':
    MF = MainFunction()
    os.startfile(r'D:\\Network\\КИТ Интернет телепрограмма\\КИТ Интернет телепрограмма.exe') if MF else print('Ошибка')