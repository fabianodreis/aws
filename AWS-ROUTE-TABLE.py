## Company : PBSC Inc ##
## Author : Fabiano Reis <freis@pbsc.com> ##
## Team : Sysadmin
## Date : Jan 2018 ##

import os
import json
import boto3
import argparse

parse = argparse.ArgumentParser()
parse.add_argument('file', help='Cache file name')
args = parse.parse_args()

ec2_client = boto3.client('ec2')
ec2 = boto3.resource('ec2')

online_routes = {}
try:
    stored_routes = json.load(open(args.file))
except:
    stored_routes = {}

for vpcs in ec2_client.describe_vpcs()['Vpcs']:

    vpcid = vpcs['VpcId']
    vpc = ec2.Vpc(vpcid)
    online_routes[vpcid] = {}

    for route in vpc.route_tables.all():

        rt_id = route.route_table_id

        online_routes[vpcid][rt_id] = []
        for r in route.routes:
            online_routes[vpcid][rt_id].append(r.destination_cidr_block)
        try:
            if online_routes[vpcid][rt_id] != stored_routes[vpcid][rt_id]:
                print("Route table '{}' inside the VPC '{}' was changed".format(rt_id, vpcid))
            #else:
            #    print("{} ({}) OK".format(vpcid, rt_id))
        except KeyError, exc:
            print("Route table '{}' inside the VPC '{}' was not found in the Routes file".format(rt_id, vpcid))

with open(args.file, 'w') as route_files:
    json.dump(online_routes, route_files, indent=4)
