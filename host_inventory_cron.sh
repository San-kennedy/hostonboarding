#!/bin/bash

cd <path to the cloned repo>

#######################################################################################################
#
# Setup aws inventory
#
#######################################################################################################
./aws_inventory.py -k {} -s {} > aws_prod_inv.txt

# please set env and location var eg:env=dev location=aws
# Pass in key file of the user that has access to cloud machines
/usr/bin/ansible-playbook -i aws_prod_inv.txt gather_fact.yml --extra-vars "env= location=" --key-file= > ansible_aws_prod_run.log

cp gather_fact.retry gather_fact_prod_aws.retry
