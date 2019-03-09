#!/usr/bin/python3
import yaml
import argparse
import os
from datetime import datetime
from pymongo import MongoClient

#Make sure to export below variables and then run the script

#export the below before running
#export MONGO_CON='mongodb://<hostname>:<port>/'
#export MONGO_USER='<username>'
#export MONGO_PASSWD='<password>'
#export MONGO_AUTHDB='<authDB>'

#fetch from env varianle
CONNSTR = os.getenv('MONGO_CON')
USERNAME = os.getenv('MONGO_USER')
PASSWORD = os.getenv('MONGO_PASSWD')
AUTH_DB = os.getenv('MONGO_AUTHDB')

CLIENT = MongoClient(CONNSTR, username=USERNAME, password=PASSWORD, authSource=AUTH_DB, maxPoolSize=10)


argParser = argparse.ArgumentParser(description="Script to push data to mongo ")

argParser.add_argument('-d','--data', type=str, help='Stats data', required=True)

args = argParser.parse_args()

data = yaml.load(args.data)

data['last_fact_run'] = datetime.now()

if 'instance_type' not in data:
    data['instance_type'] = "NA"

if 'inventory' not in CLIENT.list_database_names():
    dbs = CLIENT['inventory']
    coll = dbs["defaultthroughansible"]
    coll.insert_one({'db': 'msg', "creationTimeUTC": datetime.utcnow()})
        #naming collection as messages
    dbs.create_collection('host_facts')

dbs = CLIENT['inventory']
facts = dbs['host_facts']
logfile = open("fact2mongo.log","a+")

# see if host entry already exists, if it does just update mounts, uptime and last_fact_run
# else insert the new document

update_set = facts.update_one({"_id":data["_id"]},{'$set': {'mounts': data["mounts"],
                                'last_fact_run': data['last_fact_run'],
                                'uptime': data['uptime'], 'vcpu':data['vcpu'], 'memory': data['memory'], 'swap': int(data['swap']),
                                'instance_type': data['instance_type']}}, upsert=False)

if update_set.modified_count == 0 :

    data['swap'] = int(data['swap'])
    result = facts.insert_one(data)
    logfile.write("inserted doc :"+str(result.inserted_id)+"\n")
else :
    logfile.write("updated: "+str(data["_id"])+"\n")

logfile.close()
CLIENT.close()
