source ~/stackrc
neutron subnet-update ctlplane-subnet --dns-nameserver 192.0.2.254
neutron subnet-update ctlplane-subnet --gateway_ip 192.0.2.254
openstack overcloud roles generate --roles-path /home/stack/templates/roles --output-file /home/stack/templates/roles_data.yaml Controller Compute BlockStorage ObjectStorage CephStorage ComputeHCI
