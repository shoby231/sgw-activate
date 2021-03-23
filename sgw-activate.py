import sys
import requests
import boto3
import botocore.exceptions
import urllib, json
import time
def Public_Endpoint(ip, sgwtype, sgw_region):
    # ip = input("IP Address of the Gateway appliance: ")
    # sgwtype = input("Enter Gateway Type e.g. FILE_S3 for file gateway: ")
    # sgw_region = input("Region: ")
    key = 'http://' + ip + '/?gatewayType=' + sgwtype + '&activationRegion=' + sgw_region + '&no_redirect'
    response = requests.get(key)
    # key = response.headers
    gateway_is_active = False
    key = (response.content.decode('utf-8'))
    client = boto3.client('storagegateway')
    sgw = client.activate_gateway(
        ActivationKey=(key),
        GatewayName='My_Gateway',
        GatewayRegion=(sgw_region),
        GatewayTimezone='GMT-12:00',
        GatewayType=(sgwtype),
    )
    gateway_arn = sgw['GatewayARN']
    '''
        Block of code below does the following:
            - While gateway_is_active is set to False it will continuously loop
            - If it encounters either exception it will do one of two things:
                1: InvalidGatewayRequestException
                    - Sleep the application for 5 seconds
                    - Restart the while loop
                2: InternalServerError
                    - Break the loop and continue the code
            - When list_local_disks is called successfully we can print it and change the value of gateway_is_active to True
            - As gateway_is_active is True the loop breaks and the code continues
    '''
    while not gateway_is_active:
        try:
            disk = client.list_local_disks(
                GatewayARN=(gateway_arn)
            )
            disk_list1 = disk['Disks'][0]['DiskPath']
            disk_list2 = disk['Disks'][1]['DiskPath']
            print(disk_list1, disk_list2)

            allocate_disk = client.add_cache(
                GatewayARN=(gateway_arn),
                DiskIds=[
                    (disk_list1, disk_list2)
                ]
            )
            print(allocate_disk)
            gateway_is_active = True
        except client.exceptions.InvalidGatewayRequestException as e:
            print("Received error:\n", e)
            time.sleep(5)
            continue
        except client.exceptions.InternalServerError as e:
            print("Received non retryable error\n", e)
            break

def Private_Endpoint(ip, sgwtype, sgw_region):
    sgw_endpoint = input("VPC Endpoint_DNS_Name: ")
    key = 'http://' + ip + '/?gatewayType=' + sgwtype + '&activationRegion=' + sgw_region + '&vpcEndpoint=' + sgw_endpoint + '&no_redirect'
    response = requests.get(key)
    # key = response.headers
    key = (response.content.decode('utf-8'))
    print(key)
    client = boto3.client('storagegateway')
    sgw = client.activate_gateway(
        ActivationKey=(key),
        GatewayName='My_Gateway',
        GatewayRegion=(sgw_region),
        GatewayTimezone='GMT-12:00',
        GatewayType=(sgwtype),
    )
    print(sgw)
'''
    Initialize and get endpoint type 
'''
endpoint_type = input("Public or Private Endpoint: ")
ip = input("IP Address of the Gateway appliance: ")
sgwtype = input("Enter Gateway Type e.g. FILE_S3 for file gateway: ")
sgw_region = input("Region: ")
if endpoint_type == "Public":
    Public_Endpoint(ip, sgwtype, sgw_region)
elif endpoint_type == "Private":
    Private_Endpoint(ip, sgwtype, sgw_region) 
