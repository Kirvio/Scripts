#!/bin/bash

UTM5_MOUNT_PATH="/mnt/utm5_raw_backup/"
CMD="./get_nf_direct -D ${UTM5_MOUNT_PATH}"
IP=('104.21.28.197' '172.67.217.211' '104.21.88.24'\
    '104.21.40.79' '31.31.73.13' '119.28.133.225'\
    '65.21.188.92' '151.139.240.14' '47.243.103.215'\
    '185.53.178.11' '193.56.146.160' '104.21.28.127'\
    '104.21.42.40' '104.21.6.37' '37.1.219.50'\
    '8.209.69.22' '104.21.45.148' '172.67.73.48'\
    '172.67.130.152' '172.67.152.88' '104.21.56.235'\
    '104.26.13.151' '47.243.100.75' '92.119.113.184'\
    '62.112.10.28' '188.165.90.184')

function GetListOfRawFiles {
    files=($(/bin/ls -1 ${UTM5_MOUNT_PATH}))
    unset files[5]
    unset files[6]
    for file in ${files[@]}; do
        if [[ ! $(/bin/fuser ${UTM5_MOUNT_PATH}${file} 2>/dev/null) ]]; then
	    /bin/echo "${file}" | /bin/sed 's/$/\n/'
        fi
    done
}

function MainFunction {
    raw_files_list=$(GetListOfRawFiles)
    if [[ -z "${raw_files_list}" ]]; then
        /bin/echo "No directories detected. Abort..."
        exit 1
    fi
    for file in ${raw_files_list}; do
	for ip in ${IP[*]}; do
	      # $CMD$file' -s '$ip
              /bin/echo $UTM5_MOUNT_PATH$file' -s '$ip
        done
    done
}
# Надо сделать проверку на вывод данных, если есть данные - то копировать их в файл с названием АЙПИШНИКА
MainFunction
#/usr/bin/tr -cd '[:print:]' 
