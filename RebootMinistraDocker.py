import subprocess
import time

try:
    docker_down = subprocess.run(\
                                 ['docker-compose down'], shell=True, \
                                 stdout=subprocess.PIPE, universal_newlines=True)
    print(docker_down.stdout)
    time.sleep(2)
    docker_up = subprocess.run(\
                               ['docker-compose up -d'], check=True, shell=True, \
                               stdout=subprocess.PIPE, universal_newlines=True)
    print(docker_up.stdout)
    time.sleep(2)
except subprocess.CalledProcessError as err:
    print(err)
    pass
custom = subprocess.run(\
                        ['sudo cp -L /opt/docker_deploys/ministra/config/custom.ini /opt/docker_deploys/volumes/ministra_web/_data/stalker_portal/server/'], \
                        check=True, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
if custom.returncode == 0:
    print('custom.ini copyed')
    config = subprocess.run(\
                            ['sudo cp -L /opt/docker_deploys/ministra/config/config.php /opt/docker_deploys/volumes/ministra_web/_data/stalker_portal/storage/'], \
                            check=True, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    if config.returncode == 0:
        print('config.php copyed')
    else:
        print(config.stderr)
else:
    print(custom.stderr)
