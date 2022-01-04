#!/bin/bash

DIR="/home/belgie/new_parser_belgie/zones.blacklisted /etc/bind/zones/"
RELOAD="service bind9 reload"

function main_function {
    /bin/cp $DIR 2> /home/belgie/new_parser_belgie/belgie_logs/rel_bind.log
    if [ $? -eq 0 ]; then
        /usr/sbin/named-checkconf 2> /home/belgie/new_parser_belgie/belgie_logs/rel_bind.log
        if [ $? -eq 0 ]; then
	    ${RELOAD} 2> /home/belgie/new_parser_belgie/belgie_logs/rel_bind.log
	    if [ $? -eq 0 ]; then
                exit 0
            else
		exit 1
            fi
        else
	    exit 1
        fi
    else
        exit 1
    fi
}
main_function
