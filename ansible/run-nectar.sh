#!/bin/bash

# env variables
export ANSIBLE_PERSISTENT_CONNECT_TIMEOUT=1200
export ANSIBLE_PERSISTENT_COMMAND_TIMEOUT=1200
export ANSIBLE_PERSISTENT_CONNECT_RETRY_TIMEOUT=900
export ANSIBLE_PARAMIKO_HOST_KEY_AUTO_ADD=True

# defaults
openrc="./openrc/unimelb-comp90024-group-2-openrc.sh"
key="~/.ssh/gild-nectar.pem"
inventory="./inventory/openstack_prod_inventory.py"

tasks=0
while [ "$1" != "" ]; do
    case $1 in
        -f | --file )           shift
                                openrc=$1
                                ;;
        -h | --help )           echo "usage: run-nectar.sh [options] <command> [arg]"
                                echo "e.g. $./run-nectar.sh -i ./inventory/openstack_prod_inventory.py -k ~/.ssh/gild-nectar.pem -f openrc/pt-34689-openrc.sh"
                                echo "-f  : Path of location of file openrc"
                                echo "-r  : Database replication (change vars in playbook)"
                                echo "-a  : Run ansible for create instances and install software"
                                echo "-m  : Run ansible just to create instances"
                                echo "-s  : Run ansible just to install software"
                                echo "-k  : Path to private key file"
                                echo "-i  : Path to inventory. Usually on folder inventory. E.g. ansible/inventory/openstack_[ENV]_inventory.py"
                                exit
                                ;;
        -r | --replicate)       echo "Database replication"
                                tasks=3                             
                                ;;       

        -a | --all )            shift
                                echo "Setting up cloud  - Instances and software setup"
                                tasks=0
                                ;;
        
        -m )                    echo "Setting up cloud  - Instances"
                                tasks=1
                                ;;
        
        -s )                    echo "Setting up cloud  - Software setup"
                                tasks=2
                                ;;
        -i )                    inventory=$2
                                echo "Setting up inventory to: $inventory"
                                ;;
        -k )                    key=$2
                                echo "Setting key file to: $key"
                                
    esac
    shift
done


echo "Using OpenRC file: $openrc"

source $openrc
export PYTHONWARNINGS=ignore::UserWarning


if [ "$tasks" = "0" ]; then
    
    ansible-playbook -i $inventory --private-key  $key playbook-instances.yml

    ansible-playbook -i $inventory --private-key $key -u ubuntu -k -b --become-method=sudo -K playbook-setup.yml
fi

if [ "$tasks" = "1" ]; then
    
    ansible-playbook -i $inventory --private-key  $key playbook-instances.yml

fi

if [ "$tasks" = "2" ]; then
    
    ansible-playbook -i $inventory --private-key $key -u ubuntu -k -b --become-method=sudo -K playbook-setup.yml

fi

if [ "$tasks" = "3" ]; then
    
    ansible-playbook -i $inventory --private-key $key -u ubuntu -k -b --become-method=sudo -K playbook-replicate.yml -e "db: $database_replicate source: $source_replicate"

fi

