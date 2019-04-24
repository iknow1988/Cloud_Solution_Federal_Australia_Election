# 1. Setup
- Configure `hosts.yml`file to define all nodes ip's and ssh key
- Use `ansible-playbook -i hosts.yml setup.yml`to push key in authorized keys: 
- Test connection using this command `ansible -m ping all -i hosts.yml ` and `ansible -i hosts.yml -m shell -a 'uname -a' host1` or `ansible -i hosts.yml -m shell -a 'uname -a' all`
- Check facts from host `ansible -i hosts.yml -m setup host0`
- You can send a command directly to a group of hosts `ansible dbservers -m shell -a 'echo $TERM' -i hosts.yml` or `ansible appservers -m yum -a "name=acme state=present`

# 2. Installation
