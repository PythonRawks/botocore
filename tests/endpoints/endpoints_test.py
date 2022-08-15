
from tests import ClientHTTPStubber
from botocore.config import Config
import json

def create_stubbed_client(self, service_name, region, client_params, **kwargs):
    use_fips_endpoint = False
    use_dualstack_endpoint  = False

    if ('FIPS' in client_params):
        use_fips_endpoint = True
    if ('DualStack' in client_params):
        use_dualstack_endpoint = True
    config = Config(use_fips_endpoint=use_fips_endpoint, use_dualstack_endpoint=use_dualstack_endpoint)

    client = self.session.create_client(
        service_name, region, config=config, **kwargs
    )
    http_stubber = ClientHTTPStubber(client)
    http_stubber.start()
    return client, http_stubber

def test_action_with_client_use_arn(self, service_instance):
        service_name = service_instance.service_name
        params = service_instance.input_params
        operation = service_instance.operation
        client_params = service_instance.client_params
        region = service_instance.region
        
        self.client, self.http_stubber = self.create_stubbed_client(
            service_name,
            region,
            client_params
        )
        self.http_stubber.add_response()
        operation_instance = getattr(self.client, operation)
        operation_instance(params)

        # resulting endpoint 
        return self.http_stubber.requests[1]

# def test_action_with_client_use_arn(self, service_instance):
#         service_name = service_instance.service_name
#         params = service_instance.input_params
#         method = service_instance.method_to_execute
#         fips = service_instance.fips
#         dual_stack = service_instance.dual_stack
#         region = service_instance.region
        
#         self.client, self.http_stubber = self.create_stubbed_client(
#             region,
#             service_name,
#             fips,
#             dual_stack
#         )
#         self.http_stubber.add_response()
#         self.client.method(params)
#         // when testing after data structure filled
#         self.assert_signature( self.http_stubber.requests[0])
#         self.assert_endpoint( self.http_stubber.requests[0].endpoint_url, 
#                                     service_instance.expected_endpoint)

with open('input_endpoint_test') as f:
    services = json.load(f)
    for service in services:
        service.endpoint = test_action_with_client_use_arn(service_instance=service)

services_with_endpoints = json.dumps(services)
f = open('output_endpoint_test.json', 'w', encoding='utf-8')
f.truncate(0)
f.write(services_with_endpoints)
f.close()
