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

#-------------------------------------------
# import json
# import re
# import random
# from pathlib import Path
# from typing import NamedTuple
# from botocore.loaders import Loader
# from tests import mock, create_session

# with mock.patch('os.environ') as environ:
#     environ['AWS_ACCESS_KEY_ID'] = 'access_key'
#     environ['AWS_SECRET_ACCESS_KEY'] = 'secret_key'
#     environ['AWS_CONFIG_FILE'] = 'no-exist-foo'
#     session = create_session()

# def get_services():
#     services = session.get_available_services()
#     return services

# def get_operations(service):
#     data = session.get_service_data(service)
#     client = session.create_client(
#         service, "us-west-2"
#     )

#     operationsList = data["operations"]
#     operationsNameList = []
#     for key in operationsList.items():
#         operationsNameList.append(key)

# get_operations(get_services()[0])

# -------------------------------------------------------------
# class UrlPattern(NamedTuple):
#     service_id: str
#     operation: str
#     url_raw: str

#     def get_params(self):
#         matches = []
#         paramList = re.findall(r"\{([^\{\}]+)\}", self.url_raw)
#         for param in paramList:
#             match = [param, "asdasdasd"]
#             matches.append(match)
#         return matches

#     def get_regex(self):
#         return re.sub(r"\{[^\{\}]+\}", "(.+)", self.url_raw) #.replace("/", "\/")

# BASE_PATH = Path(Loader.BUILTIN_DATA_PATH)

# files_to_look_at = []
# url_patterns = []
# regions_list = ["us-east-1", "us-east-2", "us-west-1", "us-west-2"]

# for service_dir in BASE_PATH.iterdir():
#     if service_dir.is_dir():
#         version_dir = max(vd for vd in service_dir.iterdir())
#         files_to_look_at.append(version_dir / "service-2.json")

# for path in files_to_look_at:
#     with path.open() as f:
#         service_model = json.load(f)
#     for opname, opval in service_model.get("operations", {}).items():
#         uri = opval['http']['requestUri']
#         print(service_model["metadata"])
#         url_patterns.append(UrlPattern(
#             service_id=service_model["metadata"]["signingName"],
#             operation=opname,
#             url_raw=uri,
#         ))

# services = []
# client_params = [['FIPS'], ['DualStack'], ['FIPS', 'DualStack'], []]

# for pat in url_patterns:
#     for region in random.sample(regions_list, 2):
#         for cp in client_params:
#             services.append(
#                 {
#                     "service_name": pat.service_id,
#                     "operation": pat.operation,
#                     "input_params": pat.get_params(),
#                     "region": region,
#                     "client_params": cp,
#                     "expected_endpoint": ""
#                 }
#             )

# serialized_patterns = json.dumps(services, indent=2)
# f = open('input_endpoint_test.json', 'w', encoding='utf-8')
# f.truncate(0)
# f.write(serialized_patterns)
# f.close()
