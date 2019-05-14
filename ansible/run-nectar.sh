#!/bin/bash

source ./openrc/unimelb-comp90024-group-2-openrc.sh
#source ./openrc/pt-34689-openrc.sh 
export PYTHONWARNINGS=ignore::UserWarning

#ansible-playbook -i ./inventory/openstack_dev_inventory.py --private-key  ~/.ssh/gild-nectar.pem --ask-become-pass playbook-setup.yml -e '{"all": 1}'
#ansible-playbook -i ./inventory/openstack_dev_inventory.py --private-key ~/.ssh/gild-nectar.pem -u ubuntu -k -b --become-method=sudo -K playbook-mq.yml

#ansible-playbook -i ./inventory/openstack_prod_inventory.py --private-key  ~/.ssh/gild-nectar.pem playbook-setup.yml -e '{"db": 1 }'
#ansible-playbook -i ./inventory/openstack_prod_inventory.py --private-key ~/.ssh/gild-nectar.pem -u ubuntu -k -b --become-method=sudo -K playbook-dbcluster.yml --limit "db-dragonstone-3"
#ansible-playbook -i ./inventory/openstack_prod_inventory.py --private-key ~/.ssh/gild-nectar.pem -u ubuntu -k -b --become-method=sudo -K playbook-addnode.yml

#ansible-playbook -i ./inventory/openstack_prod_inventory.py --private-key ~/.ssh/gild-nectar.pem -u ubuntu -k -b --become-method=sudo -K playbook-prod-monitor.yml
#ansible-playbook -i ./inventory/openstack_prod_inventory.py --private-key ~/.ssh/gild-nectar.pem -u ubuntu -k -b --become-method=sudo -K playbook-prod-analytics.yml


# FINAL RUN
# Setup cloud
#ansible-playbook -i ./inventory/openstack_prod_inventory.py --private-key  ~/.ssh/gild-nectar.pem playbook-instances.yml

# Setup databases
#ansible-playbook -i ./inventory/openstack_prod_inventory.py --private-key ~/.ssh/gild-nectar.pem -u ubuntu -k -b --become-method=sudo -K playbook-dbcluster.yml

# Setup RabbitMQ
#ansible-playbook -i ./inventory/openstack_dev_inventory.py --private-key ~/.ssh/gild-nectar.pem -u ubuntu -k -b --become-method=sudo -K playbook-rabbitmq.yml

# setup harvester
#ansible-playbook -i ./inventory/openstack_prod_inventory.py --private-key ~/.ssh/gild-nectar.pem -u ubuntu -k -b --become-method=sudo -K playbook-harvester.yml

# app server
#ansible-playbook -i ./inventory/openstack_prod_inventory.py --private-key ~/.ssh/gild-nectar.pem -u ubuntu -k -b --become-method=sudo -K playbook-appserver.yml

##################

# INTIAL SETUP
ansible-playbook -i ./inventory/openstack_prod_inventory.py --private-key  ~/.ssh/gild-nectar.pem playbook-instances.yml

ansible-playbook -i ./inventory/openstack_prod_inventory.py --private-key ~/.ssh/gild-nectar.pem -u ubuntu -k -b --become-method=sudo -K playbook-setup.yml

# ADD NEW NODE
