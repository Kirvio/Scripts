import xml.dom.minidom as minidom
import argparse
import logging
import time
import sys
try:
    from xlsxwriter.workbook import Workbook
except ImportError as err:
    print(err)
    time.sleep(20)

location = 'C:\\PythonProgs\\ForReports\\Big Report\\'

def get_all_text(node) -> str:
    if node.nodeType == node.TEXT_NODE:
        value = node.data
    else:
        value = ''.join(get_all_text(child_node) \
                                                 for child_node in node.childNodes)

    return value

def transform_data(workbook_, data, sheet_name):
    try:
        worksheet = workbook_.add_worksheet(name=sheet_name)
        for row_num, row_data in enumerate(data):
            for col_num, col_data in enumerate(row_data):
                worksheet.set_column(col_num, 5, 40)
                worksheet.write(row_num+1, col_num, col_data)
    except (Exception, TypeError, AttributeError):
        log.error("Exception occurred", exc_info=True)
        time.sleep(20)

def get_summary(serv_list, condition, report_type, usual=True):
    summary = 0
    try:
        if usual:
            for c in serv_list:
                if c[2] in condition:
                    summary += float(c[4])
        else:
            for c in serv_list:
                if report_type in 'Услуги':
                    if condition in c[1] and c[3] in "Передача IP трафика":
                        summary += float(c[4])
                elif report_type in 'Основной(Вход. ост.)':
                    if condition in c[1]:
                        summary += float(c[2])
                elif report_type in 'Основной(Исход. ост.)':
                    if condition in c[1]:
                        summary += float(c[5])
    except Exception:
        log.error("Exception occured:", exc_info=True)
        time.sleep(20)
    else:
        return round(summary, 1)

# Данные по всем типам услуг(суммарно)
def services_parser(xml):
    try:
        with minidom.parse(xml) as doc:
            xml_tuple = (
                "col_account_id", "col_full_name", \
                "col_service_name", "col_service_type", "col_amount"
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
        log.info("Готово\n")
        yield tuple(y)

# Данные по основному отчету
def main_report_parser(xml):
    try:
        with minidom.parse(xml) as doc:
            xml_tuple = (
                "col_account_id", "col_full_name", \
                "col_initial_balance", "col_charges_total", \
                "col_payments", "col_closing_balance"
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
        log.info("Готово\n")
        yield tuple(y)

# Данные с отчета по платежам
def payments_parser(xml):
    try:
        with minidom.parse(xml) as doc:
            xml_tuple = (
                "col_payment_method", "col_volume"
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
        log.info("Готово\n")
        yield tuple(y)

def service_function(location_, files_):

    log.info("Парсим данные по услугам за текущий месяц")
    services_xml = ''.join([location_, files_[0]])
    data = next(services_parser(services_xml))

    summary_ = [
                item for item in data if item[0] in "Суммарно"
            ]
    one_time_service_ = [
                         item for item in data if item[3] in "Разовая услуга"
                    ]
    periodic_service = [
                        float(a[4]) for a in summary_ if a[3] in "Периодическая услуга"
                    ]
    ip_traffic = [
                  float(b[4]) for b in summary_ if b[3] in "Передача IP трафика"
              ]

    veche_lighting_serv = get_summary(serv_list=data, condition="ТП ООО", \
                                      report_type="Услуги", usual=False)
    small_retail_serv = get_summary(serv_list=data, condition="ЧТУП", \
                                    report_type="Услуги", usual=False)

    reconnect_service_summ = get_summary(serv_list=one_time_service_, \
                                         condition="Повторное подключение", report_type="Услуги")
    disconnect_service = get_summary(serv_list=one_time_service_, \
                                     condition="Отключение от СПД", report_type="Услуги")
    block_service = get_summary(serv_list=one_time_service_, \
                                condition="Добровольная блокировка", report_type="Услуги")
    change_of_tariff_service = get_summary(serv_list=one_time_service_, \
                                           condition="Изменение тарифного плана", report_type="Услуги")

    log.info(f"ТП ООО Вече-светотехника(Услуги): {veche_lighting_serv}")
    log.info(f"ЧТУП Мелкая розница(Услуги): {small_retail_serv}\n")

    legal_entity_summary_serv = sum([veche_lighting_serv, small_retail_serv])

    log.info(f"Периодические услуги: {periodic_service[0]}")
    log.info(f"Передача IP трафика: {ip_traffic[0]}")
    log.info(f"Повторное подключение: {reconnect_service_summ}")
    log.info(f"Отключение от СПД: {disconnect_service}")
    log.info(f"Добровольная блокировка: {block_service}")
    log.info(f"Изменение тарифного плана: {change_of_tariff_service}\n")

    one_time_service_summary_ = \
                                sum([reconnect_service_summ, disconnect_service,\
                                     block_service, change_of_tariff_service])

    log.info(f"Итого по разовым услугам: {one_time_service_summary_}")
    log.info(f"Итого по юр. лицам: {legal_entity_summary_serv}")

    services_summary = sum([periodic_service[0], ip_traffic[0], \
                            one_time_service_summary_])

    log.info(f"Итого по услугам: {services_summary}\n")

    balance_serv = ip_traffic[0]-legal_entity_summary_serv

    log.info(f"Сальдо по услугам(передача IP траффика): {balance_serv}")

    service_data = (

        ("ТП ООО Вече-светотехника(Услуги)", "ЧТУП Мелкая розница(Услуги)", "Итого по юр. лицам"),
        (veche_lighting_serv, small_retail_serv, legal_entity_summary_serv),
        ("Периодические услуги", "Передача IP трафика"),
        (periodic_service[0], ip_traffic[0]),
        ("Повторное подключение", "Добровольная блокировка",
         "Изменение тарифного плана", "Отключение от СПД"),
        (reconnect_service_summ, block_service,\
         change_of_tariff_service, disconnect_service),
        (),
        (),
        ("Итого по разовым услугам", "Итого по всем услугам", "Сальдо по услугам(передача IP траффика)"),
        (one_time_service_summary_, services_summary, balance_serv),

    )

    yield service_data

def main_report_funct(location_, files_):

    log.info("Парсим данные по основному отчету за текущий месяц")
    services_xml = ''.join([location_, files_[1]])
    data = next(main_report_parser(services_xml))

    for item in data:
        if item[0] in "Суммарно":
            summary_ = item

    log.info(f"Входящий остаток(сумма): {summary_[2]}")
    log.info(f"Сумма с налогами: {summary_[3]}")
    log.info(f"Платежи(сумма): {summary_[4]}")
    log.info(f"Исходящий остаток(сумма): {summary_[5]}")

    veche_lighting_main_in = get_summary(serv_list=data, condition="ТП ООО", \
                                         report_type="Основной(Вход. ост.)", usual=False)
    small_retail_main_in = get_summary(serv_list=data, condition="ЧТУП", \
                                       report_type="Основной(Вход. ост.)", usual=False)

    veche_lighting_main_out = get_summary(serv_list=data, condition="ТП ООО", \
                                          report_type="Основной(Исход. ост.)", usual=False)
    small_retail_main_out = get_summary(serv_list=data, condition="ЧТУП", \
                                        report_type="Основной(Исход. ост.)", usual=False)

    log.info(f"ТП ООО Вече-светотехника(Вход. ост.): {veche_lighting_main_in}")
    log.info(f"ЧТУП Мелкая розница(Вход. ост.): {small_retail_main_in}\n")

    log.info(f"ТП ООО Вече-светотехника(Исход. ост.): {veche_lighting_main_out}")
    log.info(f"ЧТУП Мелкая розница(Исход. ост.): {small_retail_main_out}\n")

    legal_entity_summary_main_in = sum([veche_lighting_main_in, \
                                        small_retail_main_in])
    legal_entity_summary_main_out = sum([veche_lighting_main_out, \
                                         small_retail_main_out])

    log.info(f"Суммарно по юр. лицам(Вход. ост.): {legal_entity_summary_main_in}\n")
    log.info(f"Суммарно по юр. лицам(Исход. ост.): {legal_entity_summary_main_out}\n")

    balance_main_in = float(summary_[2]) - legal_entity_summary_main_in
    balance_main_out = float(summary_[5]) - legal_entity_summary_main_out

    log.info(f"Сальдо по основному отчету(Вход. ост.): {balance_main_in}")
    log.info(f"Сальдо по основному отчету(Исход. ост.): {balance_main_out}")

    main_report_data = (
        ("Входящий остаток(сумма)", "Сумма с налогами", "Платежи(сумма)", "Исходящий остаток(сумма)"),
        (summary_[2], summary_[3], summary_[4], summary_[5]),
        ("ТП ООО Вече-светотехника(Вход. ост.)", "ЧТУП Мелкая розница(Вход. ост.)"),
        (veche_lighting_main_in, small_retail_main_in),
        ("ТП ООО Вече-светотехника(Исход. ост.)", "ЧТУП Мелкая розница(Исход. ост.)"),
        (veche_lighting_main_out, small_retail_main_out),
        ("Суммарно по юр. лицам(Вход. ост.)", "Суммарно по юр. лицам(Исход. ост.)"),
        (legal_entity_summary_main_in, legal_entity_summary_main_out),
        ("Сальдо по основному отчету(Вход. ост.)", "Сальдо по основному отчету(Исход. ост.)"),
        (balance_main_in, balance_main_out)
    )

    yield main_report_data

def payments_report_function(location_, files_):

    log.info("Парсим данные в отчете по платежам за текущий месяц")
    services_xml = ''.join([location_, files_[2]])
    data = next(payments_parser(services_xml))

    summary_ = [float(item[1]) for item in data]

    log.info(f"Кредит: {summary_[-10]}")
    log.info(f"Банковский перевод: {summary_[-9]}")
    log.info(f"Перенос денежных средств: {summary_[-8]}")
    log.info(f"Оплата наличными (возврат средств): {summary_[-7]}")
    log.info(f"Оплата через банк (юр. лица): {summary_[-6]}")
    log.info(f"Оплата наличными (абон плата при подкл): {summary_[-5]}")
    log.info(f"Перерасчет: {summary_[-4]}")
    log.info(f"Списание свыше 3-х лет: {summary_[-3]}")
    log.info(f"Оплата наличными (пауза): {summary_[-2]}")
    log.info(f"Суммарно по всем платежам: {summary_[-1]}")

    payments_report_data = (
        ("Кредит", "Банковский перевод", "Перенос денежных средств"),
        (summary_[-10], summary_[-9], summary_[-8]),
        ("Оплата наличными (возврат средств)", "Оплата через банк (юр. лица)",
         "Оплата наличными (абон плата при подкл)"),
        (summary_[-7], summary_[-6], summary_[-5]),
        ("Перерасчет", "Списание свыше 3-х лет", "Оплата наличными (пауза)"),
        (summary_[-4], summary_[-3], summary_[-2]),
        (),
        (),
        ("Суммарно по всем платежам", ""),
        (summary_[-1], "")
    )

    yield payments_report_data

def to_xlsx(location_loc, files_loc):
    service_report_data = next(service_function(location_loc, files_loc))
    main_report_data = next(main_report_funct(location_loc, files_loc))
    payments_report_data = next(payments_report_function(location_loc, files_loc))
    try:
        with Workbook('C:\\PythonProgs\\ForReports\\Big Report\\BigReportData.xlsx') as workbook:
                transform_data(workbook, service_report_data, sheet_name="Отчет по услугам")
                transform_data(workbook, main_report_data, sheet_name="Основной отчет")
                transform_data(workbook, payments_report_data, sheet_name="Отчет по платежам")
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
        parser = argparse.ArgumentParser(
        description='xml parser for mothly report'
        )
        parser.add_argument("--services_report",
                            help="Enter file name of services report(xml)", required=True)
        parser.add_argument("--main_report",
                            help="Enter file name of services report(xml)", required=True)
        parser.add_argument("--payments_report",
                            help="Enter file name of payments report(xml)", required=True)
        parser.add_argument("--other_charges_report",
                            help="Enter other charges report(xml)", action="store_true")
        parser.add_argument("--traffic_report",
                            help="Enter traffic report(xml)", action="store_true")
        args = parser.parse_args()
        files = (
            args.services_report, args.main_report, args.payments_report,
            args.other_charges_report, args.traffic_report
        )
        to_xlsx(location, files)
