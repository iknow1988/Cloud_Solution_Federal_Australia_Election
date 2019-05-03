#!/bin/bash

source ./openrc/unimelb-comp90024-group-2-openrc.sh
#ansible-playbook -i openstack_prod_inventory.py --private-key ~/.ssh/gild-nectar.pem --ask-become-pass playbook-prod-setup.yml
ansible-playbook -i openstack_prod_inventory.py --private-key ~/.ssh/gild-nectar.pem -u ubuntu -k -b --become-method=sudo -K playbook-prod-dbcluster.yml 