#!/bin/sh
openstack overcloud node import instackenv.json
for node in esjc-ost2-cn01p esjc-ost2-cn02p esjc-ost2-cn03p; do
  ironic node-update $node add properties/root_device='{"size": 48}'
done
openstack overcloud node introspect --all-manageable --provide
