#!/usr/bin/python3

import time
import sys
try:
    from modules.logger import LoggerFactory 
    from modules.blocklist_getter import BlocklistGetter
    from modules.blocklist_parser import BlocklistParser
    from modules.sftp_transfer import sftp_transer
except ImportError as err:
    print(err)
    time.sleep(10)

log = LoggerFactory.createLogger(__name__)

class Program(object):
    @staticmethod
    def main():
        try:
            blg = BlocklistGetter()
            blg.get_block_list()
            bp = BlocklistParser()
            if bp.check_dns():
                log.info("Были добавлены новые DNS")
            if bp.check_IPs():
                sftp = sftp_transer()
                sftp.connect_to_server()
            else:
                log.info("Новые IP добавлены не были")
        except Exception as err:
            sys.exit(0)

if __name__ == "__main__":
    Program.main()
