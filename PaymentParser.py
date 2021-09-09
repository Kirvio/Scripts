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

PATH_ = 'C:\\PythonProgs\\ForReports\\Payments\\'

def dt_convert(dt):
    return parser.parse(dt).strftime("%d.%m.%Y")

def get_all_text(node) -> str:
    if node.nodeType == node.TEXT_NODE:
        value = node.data
    else:
        value = ''.join(get_all_text(child_node) for child_node in node.childNodes)

    return value

def convert_items(lst):
    try:
        for item in lst:
            if "MSK" not in item[0]:
                log.info("Wrong date format")
                raise Exception("Wrong date format")
            elif "MSK" not in item[1]:
                log.info("Wrong date format")
                raise Exception("Wrong date format")
            else:
                item[0] = dt_convert(item[0])
                item[1] = dt_convert(item[1])
    except (TypeError, parser.ParserError):
        log.error("Exception occurred", exc_info=True)
        time.sleep(20)

def transform_data(workbook_, data, sheet_name):
    try:
        worksheet = workbook_.add_worksheet(name=sheet_name)
        for row_num, row_data in enumerate(data):
            for col_num, col_data in enumerate(row_data):
                worksheet.set_column(col_num, 5, 20)
                worksheet.write(row_num+1, col_num, col_data)
    except (Exception, TypeError, AttributeError):
        log.error("Exception occurred", exc_info=True)
        time.sleep(20)

def parsingxml(xml):
    try:
        with minidom.parse(xml) as doc:
            xml_tuple = (
                "col_date_of_payment", "col_actual_payment_date", "col_account_id",
                "col_full_name", "col_volume", "col_comment", "col_payment_method"
            )

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
        log.info("Считаем количество платежей")
        yield tuple(y)

def check_type(xml):
    try:
        data = next(parsingxml(xml))
        log.info(f"Суммарно: {len(data)}")

        x = [
            list(item[:-1]) for item in data \
                                             if item[6] == "Перерасчет (103)"\
                                             and item[2] != "Суммарно"
        ]
        y = [
            list(item[:-1]) for item in data \
                                             if item[6] == "Перенос денежных средств (106)"\
                                             and item[2] != "Суммарно"
        ]
        z = [
            list(item[:-1]) for item in data \
                                             if item[6] == "Оплата наличными (возврат средств) (109)"\
                                             and item[2] != "Суммарно"
        ]
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
            with Workbook('C:\\PythonProgs\\ForReports\\Payments\\Платежи.xlsx',\
                         {'strings_to_numbers': True, 'default_date_format': '%d.%m.%Y'}) as workbook:
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
        document = ''.join([PATH_, sys.argv[1]])
        check_type(document)
