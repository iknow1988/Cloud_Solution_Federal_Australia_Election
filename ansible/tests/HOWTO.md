# 1. Setup
- Configure `hosts.yml`file to define all nodes ip's and ssh key
- Use `ansible-playbook -i hosts.yml setup.yml`to push key in authorized keys: 
- Test connection using this command `ansible -m ping all -i hosts.yml ` and `ansible -i hosts.yml -m shell -a 'uname -a' host1` or `ansible -i hosts.yml -m shell -a 'uname -a' all`
- Check facts from host `ansible -i hosts.yml -m setup host0`
- You can send a command directly to a group of hosts `ansible dbservers -m shell -a 'echo $TERM' -i hosts.yml` or `ansible appservers -m yum -a "name=acme state=present`

# 2. Installation
- Run `ansible-playbook -i hosts.yml -u ubuntu -k -b --become-method=sudo -K install.yml `
- To check which hosts will be affected by playbook `ansible-playbook playbook.yml --list-hosts`

# Configure
http://docs.couchdb.com/en/latest/setup/cluster.html?highlight=test
- Make sure to have admin and cadmin at the end of `local.ini`
- Make sure you have the ip addreses in `vm.args` host
- To get a node: `curl -X GET "http://115.146.85.179:5986/_nodes/couchdb@115.146.85.220" --user admin`
- To delete a node: `curl -X DELETE "http://115.146.85.179:5986/_nodes/couchdb@127.0.0.1?rev=1-967a00dff5e02add41819138abb3284d" --user admin`
- To add a node: `curl -X PUT "http://115.146.85.179:5986/_nodes/couchdb@127.0.0.1" -d {} --user admin`

# 3. test

- This will create a database with 3 replicas and 8 shards.
`curl -X PUT "http://115.146.85.179:9584/dbtest?n=3&q=8" --user admin`


- Verify installation of cluster
  Verify install:
    `curl http://admin:password@127.0.0.1:9584/_cluster_setup`
  Response:
    `{"state":"cluster_finished"}`

- Check cluster
  `curl -X GET "http://115.146.85.179:9584/_membership" --user admin`

   
# 4. Scaling
  - Download openstack rc file and execute `wget https://raw.githubusercontent.com/ansible/ansible/devel/contrib/inventory/openstack.py`, `chmod +x openstack.py` and `source openstack.rc`
  - Install openstack sdk `pip3 install python-openstackclient` and `pip3 install python-novaclient`
  - Get diynamic inventory `./openstack_inventory.py --list > inventory.json`
  - Ping new inventory `ansible -i openstack_inventory.py --private-key ~/.ssh/gild-nectar.pem all -u ubuntu -m ping`
  

# Replication

curl -X PUT "http://admin:p01ss0n@172.26.37.251:9584/tweeter_test?n=2&q=8" 

curl -H 'Content-Type: application/json' -X POST http://admin:p01ss0n@172.26.37.251:9584/_replicate -d ' {"source": "http://admin:p01ss0n@103.6.254.59:9584/tweeter_test/", "target": "http://admin:p01ss0n@172.26.37.251:9584/tweeter_test/"}' 



# 5. References
    - https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html 




curl -X PUT "http://admin:p01ss0n@172.26.37.251:9584/tweeter_test?n=2&q=8" 

ip netns exec 0d1b399a-e61e-4afd-9353-e16bd507fc1f ssh -i ~/.ssh/gild-nectar.pem ubuntu@172.26.37.251

  ip netns exec ssh USER@SERVER




curl -X POST -H "Content-Type:application/json" http://admin:p01ss0n@localhost:5984/_cluster_setup  -d '{"action":"enable_cluster", "bind_address":"0.0.0.0", "username":"admin", "password":"p01ss0n", "node_count":"2"}'

curl -X POST -H "Content-Type:application/json" http://{{ www_user }}:{{ www_password }}@localhost:5984/_cluster_setup -d '{"action":"enable_cluster", "bind_address":"0.0.0.0", "username":"{{ www_user }}", "password":"{{ www_password }}", "node_count":"2"}'