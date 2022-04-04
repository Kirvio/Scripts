#!/bin/bash

none_images=`docker images | grep "^<none>" | awk '{ print $3 }'`
dangling_images=`sudo docker images -f "dangling=true" -q`

if [ ! -z ${dangling_images} ] || [ ! -z ${none_images} ]; then
yes '' | docker system prune
else
	echo "No images for cleanup"
fi
echo "Docker Images cleanup Done"
