import xml.dom.minidom as minidom
from xlsxwriter.workbook import Workbook
import logging
import sys
import time
import argparse

document = 'C:\\PythonProgs\\ForReports\\Write-offs\\DeptFor3Years27072021.xml'

def ParseXML(xml):
    try:
        with minidom.parse(xml) as doc:
            books = doc.getElementsByTagName("row")

            xml_tuple = ("col_login", "col_account_id", "col_start_time")
            titles = []
            [[titles.append(book.getElementsByTagName(i)[0]) for i in xml_tuple] \
                                                             for book in books]
            """Поля не должны быть пустыми"""
            y = []
            [[y.append(node.data) for node in title.childNodes \
                                                                if node.nodeType == node.TEXT_NODE]\
                                  for title in titles]
    except (Exception, TypeError, AttributeError):
        log.error("Exception occurred", exc_info=True)
        time.sleep(20)
    else:
        log.info("Ищем должников за текущий месяц")
        y = zip(*[iter(y)] * 3)
        yield tuple(y)
    pass

def ParseForMonth(xml, month, year):
    try:
        data = next(ParseXML(xml))
        __month_dict = {'01': 'Jan', '02': 'Feb',
                        '03': 'Mar', '04': 'Apr',
                        '05': 'May', '06': 'Jun',
                        '07': 'Jul', '08': 'Aug',
                        '09': 'Sep', '10': 'Oct',
                        '11': 'Nov', '12': 'Dec'}

        x = [item for item in data if __month_dict[month] in item[2] and year in item[2]]

        log.info(f"Количество должников за {'.'.join([month, year])}: {len(x)}")
    except (Exception, TypeError, AttributeError):
        log.error("Exception occurred", exc_info=True)
        time.sleep(20)
    else:
        try:
            with Workbook('C:\\PythonProgs\\ForReports\\Write-offs\\Списания.xlsx') as workbook:
                worksheet = workbook.add_worksheet()
                [[worksheet.write(row_num+1, col_num, col_data), \
                worksheet.set_column(col_num, 5, 20)] \
                                                        for row_num, row_data in enumerate(x)\
                                                        for col_num, col_data in enumerate(row_data)]
        except (Exception, TypeError, AttributeError):
            log.error("Exception occurred", exc_info=True)
            time.sleep(20)
        else:
            log.info("Экспортировано в xlsx успешно")
            input("Нажмите Enter для выхода.")

if __name__ == "__main__":
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
        try:
            parser = argparse.ArgumentParser(
                description='Скрипт для поиска должников в xml файлике',
            )
            parser.add_argument("--month", help="Введите дату(месяц)", required=True)
            parser.add_argument("--year", help="Введите дату(год)", required=True)
        except Exception as exc:
            print(exc)
            time.sleep(20)
        else:
            args = parser.parse_args()
            ParseForMonth(xml=document, month=args.month, year=args.year)