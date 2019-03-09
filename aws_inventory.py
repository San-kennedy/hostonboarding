#!/usr/bin/python3

import boto3
from botocore.exceptions import ClientError
import argparse

argParser = argparse.ArgumentParser(description="Script to fetch all instance ip's in aws account and prints ansible inventory style to stdout ")

argParser.add_argument('-k','--access_key', type=str, help='AWS account access key', required=True)
argParser.add_argument('-s','--secret',type=str, help='Aws secret access key', required=True)
argParser.add_argument('-r','--region', nargs='?', help="AWS region ex : us-east-1", type=str, default='us-east-1')

#assuming instance could have two interfaces one private and another public, with private subnet 10.x.1.0/24 and public 10.x.0.0/24
#script fetches only private ip's and public IP

argParser.add_argument('-o', '--octet', nargs='+', help='List of 3rd Octets to ignore ex: -o 0 1', type=int, default=[0, 2])

args = argParser.parse_args()


def get_instance_name(instance):
    # When given an instance object, return the instance 'Name' from the name tag.
    ec2instance = instance
    instancename = ''
    for tags in ec2instance.tags:
        if tags["Key"] == 'Name':
            instancename = tags["Value"]
    return instancename


try:
    session = boto3.session.Session(aws_access_key_id=args.access_key ,
                        aws_secret_access_key=args.secret,
                        region_name=args.region)

    # creating an EC2 service object
    EC2 = session.resource('ec2')

    vpcs = EC2.vpcs.all()

    for vpc in vpcs:
        if vpc.is_default:
            print("["+vpc.vpc_id+"]")
            instancesInVpc = vpc.instances.all()
            for instance in instancesInVpc:
                if instance.public_ip_address and instance.state["Code"] == 16:
                    print(instance.public_ip_address+"\t\tname='" + get_instance_name(instance)+"'"+
                    "\t\tinstance_id='"+ instance.instance_id + "'"+ "\t\tinstance_type='" + instance.instance_type + "'")

        else:
            print("["+vpc.vpc_id+"]")
            instancesInVpc = vpc.instances.all()
            for instance in instancesInVpc:
                # Fetch details for only running instance
                if instance.state["Code"] == 16:
                    try:

			# private ip could be attached to any interface, hence if else to fetch the appropriate one
                        if int(instance.network_interfaces_attribute[0]["PrivateIpAddress"].split(".")[2]) not in args.octet:
                            print(instance.network_interfaces_attribute[0]["PrivateIpAddress"] +"\t\tname='" + get_instance_name(instance)+"'"+
                            "\t\tinstance_id='"+ instance.instance_id + "'"+ "\t\tinstance_type='" + instance.instance_type + "'")

                        else:
                            print(instance.network_interfaces_attribute[1]["PrivateIpAddress"] +"\t\tname='" + get_instance_name(instance)+"'"+
                            "\t\tinstance_id='"+ instance.instance_id + "'"+ "\t\tinstance_type='" + instance.instance_type + "'")
                    except IndexError:
		    # print public facing IP if private ip could not be found
                        print(instance.public_ip_address +"\t\tname='" + get_instance_name(instance)+"'"+
                        "\t\tinstance_id='"+ instance.instance_id + "'"+ "\t\tinstance_type='" + instance.instance_type + "'")
except ClientError as e:
    print("Oops we have an error "+str(e))
