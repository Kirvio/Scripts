import xml.dom.minidom as minidom
from xlsxwriter.workbook import Workbook
import logging
import sys
import time

document1 = 'C:\\PythonProgs\\Для отчета\\Платежи(Перерасчет)\\Payment report.xml'

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
    data = next(parsingxml(xml))
    log.info(f"Суммарно: {len(data)}")
    x = [item for item in data if item[6] == "Перерасчет (103)"]
    y = [item for item in data if item[6] == "Перенос денежных средств (106)"]
    z = [item for item in data if item[6] == "Оплата наличными (возврат средств) (109)"]

    log.info(f"Количество перерасчетов за Июнь: {len(x)}")
    log.info(f"Количество переносов за Июнь: {len(y)}")
    log.info(f"Количество возвратов за Июнь: {len(z)}")
    try:
        with Workbook('C:\\PythonProgs\\Для отчета\\Платежи(Перерасчет)\\Платежи.xlsx') as workbook:
            worksheet = workbook.add_worksheet()
            [[worksheet.write(row_num+1, col_num, col_data), \
              worksheet.set_column(col_num, 5, 20)] \
                                                    for row_num, row_data in enumerate(x)\
                                                    for col_num, col_data in enumerate(row_data)]
            worksheet = workbook.add_worksheet()
            [[worksheet.write(row_num+1, col_num, col_data), \
              worksheet.set_column(col_num, 5, 20)] \
                                                    for row_num, row_data in enumerate(y)\
                                                    for col_num, col_data in enumerate(row_data)]
            worksheet = workbook.add_worksheet()
            [[worksheet.write(row_num+1, col_num, col_data), \
              worksheet.set_column(col_num, 5, 20)] \
                                                    for row_num, row_data in enumerate(z)\
                                                    for col_num, col_data in enumerate(row_data)]
    except (TypeError, AttributeError):
        log.error("Exception occurred", exc_info=True)
        time.sleep(20)
    else:
        log.info("Экспортировано в xlsx успешно")
        input("Нажмите Enter для выхода.")

if __name__ == "__main__":
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    f_format = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(f_format)
    log.addHandler(handler)
    check_type(document1)