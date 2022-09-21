import json
import os
import random
import boto3
from botocore.loaders import Loader
from botocore import xform_name

session = boto3.Session()
loader = Loader()
services = session.get_available_services()
base_dir = "botocore/data"

def generate():

    output_dict =  []
    for service in services:
        versions = sorted(loader.list_api_versions(service, 'service-2'))
        fpath = os.sep.join([base_dir, service, versions[-1], 'service-2.json'])    
        regions_list = ["us-east-1", "us-east-2", "us-west-1", "us-west-2"]
        client_params = [['FIPS'], ['DualStack'], ['FIPS', 'DualStack'], []]

        with open(fpath, 'r') as f:
            jval = json.loads(f.read())
            ops = jval['operations']
            operationList = []
            for name, op in ops.items():
                if "input" in op:
                    inp_name = op["input"]["shape"]
                    inp_shape = jval["shapes"][inp_name]
                    if "required" not in inp_shape or len(inp_shape["required"]) == 0:
                        operationList.append(xform_name(name))
            
            for region in random.sample(regions_list, 2):
                for cp in client_params:
                    serviceData = {}
                    serviceData["service_name"] = service
                    serviceData["operations"] = operationList
                    serviceData["input_params"] = ""
                    serviceData["region"] = region
                    serviceData["client_params"] = cp
                    serviceData["expected_endpoint"] = ""
                    output_dict.append(serviceData)

        if len(operationList) == 0:
            print(f"Unable to find operation for service {service}")
    return output_dict

service_to_operation_map = generate()

with open('input_endpoint_test.json', 'w') as f:
    f.write(json.dumps(service_to_operation_map))


