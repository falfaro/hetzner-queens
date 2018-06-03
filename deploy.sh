#!/bin/bash
source $HOME/stackrc
if [[ "$DELETE" == "yes" ]]; then
  openstack stack delete --wait --yes overcloud
  ./clean_ironic.sh
  swift delete overcloud-swift-rings
fi
#openstack overcloud roles generate -o ~/templates/roles_data.yaml Controller ComputeHCI Networker
time openstack overcloud deploy --answers-file ./answers.yaml --roles-file ./roles_data.yaml
