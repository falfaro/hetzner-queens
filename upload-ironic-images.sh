#!/bin/sh
source ~/stackrc
cd /home/stack/images
openstack overcloud image upload --update-existing
