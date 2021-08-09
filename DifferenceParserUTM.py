import xml.dom.minidom as minidom
import logging
import time
import sys
try:
    from xlsxwriter.workbook import Workbook
except ImportError as err:
    print(err)
    time.sleep(20)

PATH_ = 'C:\\PythonProgs\\ForReports\\Difference\\'

def get_all_text(node) -> str:
    if node.nodeType == node.TEXT_NODE:
        value = node.data
    else:
        value = ''.join(get_all_text(child_node) for child_node in node.childNodes)

    return value

def get_closing_balance(xml):
    try:
        with minidom.parse(xml) as doc:

            xml_tuple = ("row_id", "col_account_id", "col_login",
                         "col_full_name", "col_charges_total", "col_payments",
                         "col_closing_balance")
            y = []
            for row_el in doc.getElementsByTagName("row"):
                row = []
                for tag_name in xml_tuple:
                    child_el = row_el.getElementsByTagName(tag_name)[0]
                    child_text = get_all_text(child_el) or "No data"
                    row.append(child_text)

                y.append(row)
    except (Exception, TypeError, AttributeError):
        log.error("Exception occurred", exc_info=True)
        time.sleep(20)
    else:
        log.info("Исходящий баланс на позапрошлый месяц проверен")
        yield tuple(y)

def get_initial_balance(xml):
    try:
        with minidom.parse(xml) as doc:

            x = []
            for row_el in doc.getElementsByTagName("row"):
                child_el = row_el.getElementsByTagName("col_initial_balance")[0]
                child_text = get_all_text(child_el)

                x.append(child_text)
    except (Exception, TypeError, AttributeError):
        log.error("Exception occurred", exc_info=True)
        time.sleep(20)
    else:
        log.info("Входящий баланс на прошлый месяц проверен")
        yield tuple(x)

def result(xml1, xml2):
    try:
        y_ = next(get_closing_balance(xml1))
        x_ = next(get_initial_balance(xml2))
        c = [(*close_value, init_value) \
                                        for close_value, init_value in zip(y_, x_) \
                                                                                   if init_value != close_value[6]]
    except (TypeError, AttributeError):
        log.error("Exception occurred", exc_info=True)
        time.sleep(20)
    else:
        log.info(f"Всего записей с разницей найдено: {len(c)}")
        try:
            with Workbook('C:\\PythonProgs\\ForReports\\Difference\\Result.xlsx',\
                         {'strings_to_numbers': True}) as workbook:
                worksheet = workbook.add_worksheet()
                for row_num, row_data in enumerate(c[:-1]):
                    for col_num, col_data in enumerate(row_data):
                        worksheet.set_column(col_num, 5, 20)
                        worksheet.write(row_num+1, col_num, col_data)
        except (TypeError, AttributeError):
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
        document1 = ''.join([PATH_, sys.argv[1]])
        document2 = ''.join([PATH_, sys.argv[2]])
        result(document1, document2)
