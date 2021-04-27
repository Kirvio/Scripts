import paramiko
import time
import sys
import argparse

def dump_cisco_config(ip, username, ssh_password, quiet=False):
    client = paramiko.SSHClient()  # create an SSH client
    # Set the policy to auto-connect to hosts not in known-hosts file
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if not quiet:
        print(f"Connecting to switch {ip}", file=sys.stderr)
    client.connect(ip, username=username, password=ssh_password, look_for_keys=False, allow_agent=False)

    print(f"Connected. Enabling...", file=sys.stderr)
    channel = client.invoke_shell(); time.sleep(5)
    #channel.send('enable\n'); time.sleep(5)
    #channel.send(f"{enable_password}\n"); time.sleep(5)
    # Set the terminal length to 0 so it doesn't try to pageinate the output
    channel.send("terminal length 0\n"); time.sleep(1)
    _ = channel.recv(99999)  # get back all the output up to this point
    print(f"Now dumping running-config...", file=sys.stderr)
    channel.send("show running-config\n"); time.sleep(30)

    config = channel.recv(999999).decode('utf-8')  # now get back the running config and decode to string\
    config = "\n".join(config.split('\n')[0:-1])  # remove the last line of the config, which will be the prompt again
    client.close()  # close ssh connection
    return(config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Connect to a switch over SSH and dump the running-config',
        epilog='''You will need the paramiko SSH library installed to run this. On Ubuntu this can be installed with: sudo apt-get install python3-paramiko''', 
    )
    parser.add_argument("--address", help="IP or Hostname of the switch", required=True)
    #parser.add_argument("--username", help="Switch username", required=True)
    #parser.add_argument("--ssh-password", help="Switch SSH password", required=True)
    #parser.add_argument("--enable-password", help="Switch enable password", required=True)
    parser.add_argument("--quiet", help="Don't show interactive info on stderr", action="store_true")
    args = parser.parse_args()
    print(dump_cisco_config(ip=args.address, username='', ssh_password='', quiet=args.quiet))
