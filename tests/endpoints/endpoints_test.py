
from tests import ClientHTTPStubber
from pathlib import Path
from botocore.config import Config
from botocore.compat import urlsplit
import botocore.session
import json

class TestWriteExpectedEndpoints():
    session = botocore.session.get_session()

    def setUp(self):
        super().setUp()

    def create_client(self, **kwargs):
        client_kwargs = {
                            'region_name': kwargs['region_name'],
                            'aws_access_key_id': 'foo',
                            'aws_secret_access_key': 'bar',
                            'config': kwargs['config']
                        }
        client_kwargs.update(kwargs)
        client = self.session.create_client(**client_kwargs)
        http_stubber = ClientHTTPStubber(client)
        http_stubber.start()
        return client, http_stubber

    def test_endpoint_redirection(self, service_instance, **kwargs):
        use_fips_endpoint = False
        use_dualstack_endpoint  = False

        if ('FIPS' in service_instance['client_params']):
            use_fips_endpoint = True
        if ('DualStack' in service_instance['client_params']):
            use_dualstack_endpoint = True
        config = Config(use_fips_endpoint=use_fips_endpoint, use_dualstack_endpoint=use_dualstack_endpoint)

        self.client, self.http_stubber = self.create_client(
            region_name=service_instance['region'],
            service_name=service_instance['service_name'], 
            config=config, 
            **kwargs
        )
        self.http_stubber.add_response(status=200)
        if (len(service_instance['operations'])):                
            op = getattr(self.client, service_instance['operations'][0])
            try:
                op()
            except:
                return ""
            request = self.http_stubber.requests[0]
            # endpoint = urlsplit(request.url).netloc
            # print(endpoint)
            return request.url
        else:
            return ""

    def build_endpoint_output_file(self):
        current_file = Path(__file__)
        neighboring_file = current_file.parent / "input_endpoint_test.json"
        output_file = current_file.parent / "output_endpoint_test.json"

        with (neighboring_file).open() as f:
            services = json.load(f)
            for service in services:
                service['endpoint'] = self.test_endpoint_redirection(service_instance=service)
                print(service['endpoint'])

        output_file.unlink(missing_ok=True)
        output_file.touch(exist_ok=True)
        with (output_file).open(mode='w+') as out:
            output_json = json.dumps(services)
            out.write(output_json)
  

test_endpoints = TestWriteExpectedEndpoints()
test_endpoints.build_endpoint_output_file()

# from tests import ClientHTTPStubber, mock, create_session
# from botocore.config import Config
# import json
# import datetime
# from pathlib import Path
# # todo:
# #   1) add randome value to every param before creation of input_endpoint_test.json
# #   2) after operation request, add authorization signature along with endpoint to validation result output file. 

# def _get_patched_session():
#     time_to_freeze = datetime.datetime.now(datetime.timezone.utc).isoformat()
#     with mock.patch('os.environ') as environ:
#         environ['AWS_ACCESS_KEY_ID'] = 'access_key'
#         environ['AWS_SECRET_ACCESS_KEY'] = 'secret_key'
#         environ['AWS_CONFIG_FILE'] = 'no-exist-foo'
#         environ['EP20_TESTING_FREEZER_TIME'] = time_to_freeze
#         environ.update(environ)
#         session = create_session()
#         return session

# def create_stubbed_client(service_name, region, client_params, **kwargs):
#     use_fips_endpoint = False
#     use_dualstack_endpoint  = False
#     session = _get_patched_session()

#     if ('FIPS' in client_params):
#         use_fips_endpoint = True
#     if ('DualStack' in client_params):
#         use_dualstack_endpoint = True
#     config = Config(use_fips_endpoint=use_fips_endpoint, use_dualstack_endpoint=use_dualstack_endpoint)

#     time_to_freeze = datetime.datetime.now(datetime.timezone.utc).isoformat()
#     client = session.create_client(
#         service_name, 
#         region,
#         aws_access_key_id='foo',
#         aws_secret_access_key='bar',
#         config=config, 
#         **kwargs
#     )
#     http_stubber = ClientHTTPStubber(client)
#     http_stubber.start()
#     return client, http_stubber

# def test_action_with_client_use_arn(service_instance):
#         print(service_instance)
#         service_name = service_instance["service_name"]
#         params = service_instance["input_params"]
#         operations = service_instance["operations"]
#         client_params = service_instance["client_params"]
#         region = service_instance["region"]
        
#         client, http_stubber = create_stubbed_client(
#             service_name,
#             region,
#             client_params
#         )
#         http_stubber.add_response()
#         operation_instance = getattr(client, operations[0])
#         if (len(params)):
#             operation_instance(params)
#         else:
#             operation_instance()

#         # resulting endpoint 
#         stubUrl = __getitem__(http_stubber.requests[0], "url")
#         print(stubUrl)
#         # print(http_stubber.requests[0])
#         return http_stubber.requests[0]

# # def test_action_with_client_use_arn(self, service_instance):
# #         service_name = service_instance.service_name
# #         params = service_instance.input_params
# #         method = service_instance.method_to_execute
# #         fips = service_instance.fips
# #         dual_stack = service_instance.dual_stack
# #         region = service_instance.region
        
# #         self.client, self.http_stubber = self.create_stubbed_client(
# #             region,
# #             service_name,
# #             fips,
# #             dual_stack
# #         )
# #         self.http_stubber.add_response()
# #         self.client.method(params)
# #         // when testing after data structure filled
# #         self.assert_signature( self.http_stubber.requests[0])
# #         self.assert_endpoint( self.http_stubber.requests[0].endpoint_url, 
# #                                     service_instance.expected_endpoint)

# current_file = Path(__file__)
# neighboring_file = current_file.parent / "input_endpoint_test.json"

# with (neighboring_file).open() as f:
#     services = json.load(f)
#     for service in services:
#         service.endpoint = test_action_with_client_use_arn(service_instance=service)

# services_with_endpoints = json.dumps(services)
# f = open('output_endpoint_test.json', 'w', encoding='utf-8')
# f.truncate(0)
# f.write(services_with_endpoints)
# f.close()
