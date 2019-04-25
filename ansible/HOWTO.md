# 1. Setup
- Configure `hosts.yml`file to define all nodes ip's and ssh key
- Use `ansible-playbook -i hosts.yml setup.yml`to push key in authorized keys: 
- Test connection using this command `ansible -m ping all -i hosts.yml ` and `ansible -i hosts.yml -m shell -a 'uname -a' host1` or `ansible -i hosts.yml -m shell -a 'uname -a' all`
- Check facts from host `ansible -i hosts.yml -m setup host0`
- You can send a command directly to a group of hosts `ansible dbservers -m shell -a 'echo $TERM' -i hosts.yml` or `ansible appservers -m yum -a "name=acme state=present`

# 2. Installation
Run `ansible-playbook -i hosts.yml -u ubuntu -k -b --become-method=sudo -K install.yml `

# Configure
- Make sure to have admin and cadmin at the end of `local.ini`
- Make sure you have the ip addreses in `vm.args` host
- To get a node: `curl -X GET "http://115.146.85.179:5986/_nodes/couchdb@115.146.85.220" --user admin`
- To delete a node: `curl -X DELETE "http://115.146.85.179:5986/_nodes/couchdb@127.0.0.1?rev=1-967a00dff5e02add41819138abb3284d" --user admin`
- To add a node: `curl -X PUT "http://115.146.85.179:5986/_nodes/couchdb@127.0.0.1" -d {} --user admin`

# test

- This will create a database with 3 replicas and 8 shards.
`curl -X PUT "http://115.146.85.179:9584/dbtest?n=3&q=8" --user admin`


- Verify installation of cluster
  Verify install:
    `curl http://admin:password@127.0.0.1:5984/_cluster_setup`
  Response:
    `{"state":"cluster_finished"}`

- Check cluster
  `curl -X GET "http://115.146.85.179:9584/_membership" --user admin`