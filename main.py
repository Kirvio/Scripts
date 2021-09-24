import time
try:
    from modules.blocklist_getter import BlocklistGetter
    from modules.blocklist_parser import BlocklistParser
    from modules.sftp_transfer import sftp_transer
except ImportError as err:
    print(err)
    time.sleep(10)

class Program(object):
    @staticmethod
    def main():
        try:
            blg = BlocklistGetter()
            blg.get_block_list()
            bp = BlocklistParser()
            bp.blocklist_parser()
            sftp = sftp_transer()
            sftp.ConnectToServerViaSSH()
        except Exception as e:
            print(e)
            time.sleep(10)

if __name__ == "__main__":
    Program.main()