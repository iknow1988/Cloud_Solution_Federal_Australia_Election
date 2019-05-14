#!/bin/bash

# defaults
openrc="./openrc/unimelb-comp90024-group-2-openrc.sh"
key="~/.ssh/gild-nectar.pem"
inventory="./inventory/openstack_prod_inventory.py"

tasks=0
while [ "$1" != "" ]; do
    case $1 in
        -f | --file )           shift
                                openrc=$1
                                echo "$openrc"
                                ;;
        -h | --help )           echo "usage: run-nectar.sh [options] <command> [arg]"
                                echo "-f             : location of file openrc"
                                echo "-r             : Database replication (change vars in playbook)"
                                echo "-a             : Run ansible for create instances and install software"
                                echo "-m             : Run ansible just to create instances"
                                echo "-s             : Run ansible just to install software"
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
                                
                                
    esac
    shift
done


echo "OpenRC file: $openrc"
echo "Task ID: $tasks"
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

