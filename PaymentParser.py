import xml.dom.minidom as minidom
import logging
import time
import sys
try:
    from xlsxwriter.workbook import Workbook
    from dateutil import parser
except ImportError as err:
    print(err)
    time.sleep(20)

document = 'C:\\PythonProgs\\ForReports\\Payments\\Payment report.xml'

def dt_convert(dt):
    return parser.parse(dt).strftime("%d.%m.%Y")

def convert_items(lst):
    try:
        for item in lst:
            item[0] = dt_convert(item[0])
            item[1] = dt_convert(item[1])
    except (TypeError, parser.ParserError):
        log.error("Exception occurred", exc_info=True)
        time.sleep(20)

def transform_data(workbook_, data, sheet_name):
    try:
        worksheet = workbook_.add_worksheet(name=sheet_name)
        [[worksheet.write(row_num+1, col_num, col_data), \
          worksheet.set_column(col_num, 5, 20)] \
                                                for row_num, row_data in enumerate(data)\
                                                for col_num, col_data in enumerate(row_data)]
    except (Exception, TypeError, AttributeError):
        log.error("Exception occurred", exc_info=True)
        time.sleep(20)

def parsingxml(xml):
    try:
        with minidom.parse(xml) as doc:
            books = doc.getElementsByTagName("row")

            xml_tuple = ("col_date_of_payment", "col_actual_payment_date", "col_account_id",\
                         "col_full_name", "col_volume", "col_comment", "col_payment_method")
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
        log.info("Считаем количество платежей")
        y = zip(*[iter(y)] * 7)
        yield tuple(y)

def check_type(xml):
    try:
        data = next(parsingxml(xml))
        log.info(f"Суммарно: {len(data)}")

        x = [list(item) for item in data if item[6] == "Перерасчет (103)"]
        y = [list(item) for item in data if item[6] == "Перенос денежных средств (106)"]
        z = [list(item) for item in data if item[6] == "Оплата наличными (возврат средств) (109)"]
        convert_items(x)
        convert_items(y)
        convert_items(z)

        log.info(f"Количество перерасчетов за Июнь: {len(x)}")
        log.info(f"Количество переносов за Июнь: {len(y)}")
        log.info(f"Количество возвратов за Июнь: {len(z)}")
    except (Exception, TypeError, AttributeError):
        log.error("Exception occurred", exc_info=True)
        time.sleep(20)
    else:
        try:
            with Workbook('C:\\PythonProgs\\ForReports\\Payments\\Платежи.xlsx') as workbook:
                transform_data(workbook, x, sheet_name="Перерасчеты")
                transform_data(workbook, y, sheet_name="Переносы")
                transform_data(workbook, z, sheet_name="Возвраты")
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
        check_type(document)
