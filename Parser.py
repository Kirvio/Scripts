import xml.dom.minidom as minidom
from xlsxwriter.workbook import Workbook
import logging
import sys

document1 = 'C:\\PythonProgs\\Парсер для отчета\\Разница\\2021_05.xml'
document2 = 'C:\\PythonProgs\\Парсер для отчета\\Разница\\2021_06.xml'

def get_closing_balance(xml):
    """
    Выводим все заголовки из xml.
    """
    try:
        with minidom.parse(xml) as doc:
            books = doc.getElementsByTagName("row")

            xml_tuple = ("row_id", "col_account_id", "col_login",
                         "col_full_name", "col_charges_total", "col_payments",
                         "col_closing_balance")
            titles = []
            [[titles.append(book.getElementsByTagName(i)[0]) for i in xml_tuple] \
                                                             for book in books]
            y = []
            [[y.append(node.data) for node in title.childNodes \
                                                               if node.nodeType == node.TEXT_NODE] \
                                  for title in titles]
    except (TypeError, AttributeError):
        log.error("Exception occurred", exc_info=True)
    else:
        log.info("Исходящий баланс на позапрошлый месяц проверен")
        y = zip(*[iter(y)] * 7)
        yield list(y)

def get_initial_balance(xml):
    """
    Выводим все заголовки из xml.
    """
    try:
        with minidom.parse(xml) as doc:
            books = doc.getElementsByTagName("row")

            titles = []
            [titles.append(book.getElementsByTagName("col_initial_balance")[0]) for book in books]

            x = []
            [[x.append(node.data) for node in title.childNodes \
                                                               if node.nodeType == node.TEXT_NODE] \
                                  for title in titles]
    except (TypeError, AttributeError):
        log.error("Exception occurred", exc_info=True)
    else:
        log.info("Входящий баланс на прошлый месяц проверен")
        yield list(x)

def result(xml1, xml2):
    try:
        y_ = next(get_closing_balance(xml1))
        x_ = next(get_initial_balance(xml2))
        c = [(*close_value, init_value) \
                                        for close_value, init_value in zip(y_, x_) \
                                                                                if init_value != close_value[6]]
    except (TypeError, AttributeError):
        log.error("Exception occurred", exc_info=True)
    else:
        log.info("Разница найдена")
        try:
            with Workbook('C:\\PythonProgs\\Парсер для отчета\\Разница\\Results.xlsx') as workbook:
                worksheet = workbook.add_worksheet()
                [[worksheet.write(row_num+1, col_num, col_data), \
                worksheet.set_column(col_num, 5, 20)] \
                                                        for row_num, row_data in enumerate(c)\
                                                        for col_num, col_data in enumerate(row_data)]
        except (TypeError, AttributeError):
            log.error("Exception occurred", exc_info=True)
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
    result(document1, document2)