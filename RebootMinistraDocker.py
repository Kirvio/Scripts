import subprocess
import shutil
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
except subprocess.CalledProcessError as err:
    print(err)
    pass
finally:
    try:
        path_to_custom = '/opt/docker_deploys/ministra/config/custom.ini'
        path_to_server = '/opt/docker_deploys/volumes/ministra_web/_data/stalker_portal/server/custom.ini'
        shutil.copyfile(path_to_custom, path_to_server)
    except (shutil.Error, IOError) as err:
        print(err)
    else:
        print('custom.ini copyed')
        try:
            path_to_config = '/opt/docker_deploys/ministra/config/config.php'
            path_to_storage = '/opt/docker_deploys/volumes/ministra_web/_data/stalker_portal/storage/config.php'
            shutil.copyfile(path_to_config, path_to_storage)
        except (shutil.Error, IOError) as err:
            print(err)
        else:
            print('config.php copyed')
