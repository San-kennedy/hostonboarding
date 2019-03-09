# hostonboarding
Rudimentary workflow to onboard cloud VM's

## Inventory workflow

The workflow is split into 3 parts
  - Fetch private IP's of all our cloud hosts and generate an ansible inventory file (aws_inventory.py)
  - Fetches the host facts (gather_fact.yml)
  - Ingest the Hostfacts to MongoDB (fact2mongo.py)

#### Dependency
 - Python3
 - boto3 and pymongo python3 library
 - ansible
 - aws access key with "ec2:DescribeInstances","ec2:DescribeTags","ec2:DescribeVpcs" actions
 - ssh user access to VM (used by ansible)
 - MongoDB username and password (MongoDB will act as inventoryDB)

### Script to fetch private IP's of cloud instances
```sh
$ ./aws_inventory.py -k <AWS_ACCESS_KEY> -s <AWS_SECRET_KEY>
```

prints an ansible inventory style output to stdout, which is used for next stages

Use aws_inventory.py --help to find out all the flags

### Ansible Playbook to gather host facts and insert into DB

```sh
$ ansible-playbook -i <inventory file> gather_fact.yml --extra-vars "env=<env> location=<location>" --key-file=<ssh key>
```
make sure you have the fact2mongo.py in the same directory from where ansible-playbook is run

prerequisite for persisting data in mongoDB:
```sh
$ export MONGO_CON='mongodb://localhost:27017/'
$ export MONGO_USER='username'
$ export MONGO_PASSWD='password'
$ export MONGO_AUTHDB='auth_db'
```

a simple cron script host_inventory_cron.sh shows how it can be tied together
