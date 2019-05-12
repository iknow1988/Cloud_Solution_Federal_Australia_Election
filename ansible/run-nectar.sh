#!/bin/bash

source ./openrc/unimelb-comp90024-group-2-openrc.sh
#source ./openrc/pt-34689-openrc.sh 
export PYTHONWARNINGS=ignore::UserWarning

#ansible-playbook -i ./inventory/openstack_dev_inventory.py --private-key  ~/.ssh/gild-nectar.pem --ask-become-pass playbook-prod-setup.yml -e '{"db": 1}'
#ansible-playbook -i ./inventory/openstack_dev_inventory.py --private-key ~/.ssh/gild-nectar.pem -u ubuntu -k -b --become-method=sudo -K playbook-prod-dbcluster.yml

#ansible-playbook -i ./inventory/openstack_prod_inventory.py --private-key  ~/.ssh/gild-nectar.pem playbook-setup.yml -e '{"db": 2 }'
#ansible-playbook -i ./inventory/openstack_prod_inventory.py --private-key ~/.ssh/gild-nectar.pem -u ubuntu -k -b --become-method=sudo -K playbook-dbcluster.yml
ansible-playbook -i ./inventory/openstack_prod_inventory.py --private-key ~/.ssh/gild-nectar.pem playbook-databases.yml

#ansible-playbook -i ./inventory/openstack_prod_inventory.py --private-key ~/.ssh/gild-nectar.pem -u ubuntu -k -b --become-method=sudo -K playbook-prod-monitor.yml
#ansible-playbook -i ./inventory/openstack_prod_inventory.py --private-key ~/.ssh/gild-nectar.pem -u ubuntu -k -b --become-method=sudo -K playbook-prod-analytics.yml

