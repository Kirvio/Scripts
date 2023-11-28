#!/usr/bin/python3.5

import argparse
import os
from switch import Switch
import exceptions as Exc

# SCRIPT SETTINGS
username = None
password = None
start_dir = None
port = None
files_dir = None
files_list = None

# COMMANDS TEMPLATE
HP_BACKUP_COMMAND = "copy running-config tftp {ip} {path}"
DCN_BACKUP_COMMAND = "copy running-config tftp://{ip}/{path}"
CISCO_BACKUP_COMMAND = "copy running-config tftp://{ip}/{path}"

# TFTP_SERVER SETTINGS
tftp_server_ip = None
configs_path = "Configs/"
office_path = configs_path + "Office/"
region1_path = configs_path + "Region1/"
region2_path = configs_path + "Region2/"
region3_path = configs_path + "Region3/"
station_path = configs_path + "CoreStation/"


def get_path(location):
    location = location.strip()
    if location == "O":
        return office_path
    elif location == "R1":
        return region1_path
    elif location == "R2":
        return region2_path
    elif location == "R3":
        return region3_path
    elif location == "CS":
        return station_path
    else:
        raise Exc.LocationException("Wrong switch location!")


def get_parser():
    parser.add_argument('-h', '--help', action='help', help='Справка')
    parser.add_argument('-l', '--login', default='', help="Логин для входа на сетевое устройство")
    parser.add_argument('-p', '--password', default='', help="Пароль для входа на сетевое устройство")
    parser.add_argument('-sd', '--start_dir', required=True, help="Директория со скриптами")
    parser.add_argument('-pt', '--port', default=22, help="Порт для подключения (22 по-умолчанию)")
    parser.add_argument('-ip', '--ip_address', default="", help="ip-адрес TFTP сервера", metavar='TFTP server IP')
    return parser


def get_switch(sub):
    if 3 <= len(sub) < 5:
        ip = sub[0].strip()
        switch_type = sub[1].strip()
        location = sub[2].strip()
        hostname = ""
        if len(sub) > 3 and sub[3]:
            hostname = sub[3].strip()
        if hostname:
            return Switch(ip, switch_type, location, hostname, username, password, port)
        else:
            return Switch(ip, switch_type, location, "", username, password, port)
    else:
        raise ValueError


def main():
    os.chdir(start_dir)
    for file_path in files_list:
        with open(files_dir + file_path, "r") as f:
            for line in f:
                if line[0] == "#":
                    continue
                switch = get_switch(line.split('|'))
                if switch.switch_type == "DCN":
                    command = DCN_BACKUP_COMMAND
                    command = command.replace("{ip}", tftp_server_ip)
                    command = command.replace("{path}", get_path(switch.location))
                    switch.add_command(command)
                    switch.add_command("Y")
                    switch.execute()
                elif switch.switch_type == "HP":
                    command = HP_BACKUP_COMMAND
                    command = command.replace("{ip}", tftp_server_ip)
                    command = command.replace("{path}", get_path(switch.location))
                    switch.add_command(command)
                    switch.execute()
                elif switch.switch_type == "CISCO":
                    command = CISCO_BACKUP_COMMAND
                    command = command.replace("{ip}", tftp_server_ip)
                    command = command.replace("{path}", get_path(switch.location))
                    switch.add_command(command)
                    switch.add_command("\n")
                    switch.add_command("\n")
                    switch.execute()
                else:
                    raise Exc.SwitchTypeException("Wrong switch type!")


if __name__ == "__main__":
    namespace = get_parser().parse_args()

    username = namespace.login
    password = namespace.password
    start_dir = namespace.start_dir
    port = namespace.port
    tftp_server_ip = namespace.ip_address
    files_dir = start_dir + "/Switches/"
    files_list = os.listdir(files_dir)

    main()
