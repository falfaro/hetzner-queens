#!/bin/bash
set -x
export DIB_YUM_REPO_CONF="/etc/yum.repos.d/delorean-queens*.repo /etc/yum.repos.d//tripleo-centos-ceph-*.repo"
export STABLE_RELEASE="queens"
openstack overcloud image build --all
