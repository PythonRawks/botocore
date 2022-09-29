
from tests import ClientHTTPStubber, FreezeTime, unittest, mock, ContextDecorator
from freezegun import freeze_time
from pathlib import Path
from botocore.config import Config
from botocore.compat import urlsplit
import botocore.session
import json
import datetime

class FreezeToken(ContextDecorator):

    def __init__(self, module, token=None):
        if token is None:
            token = '0bea188d-636d-49e9-9a49-5826105d7b74'
        self.token = token
        self.uuid_patcher = mock.patch.object(
            module, 'uuid4', mock.Mock(return_value=token)
        )

    def __enter__(self, *args, **kwargs):
        mock = self.uuid_patcher.start()
        # mock.uuid4.return_value = self.token

    def __exit__(self, *args, **kwargs):
        self.uuid_patcher.stop()

class TestWriteExpectedEndpoints(unittest.TestCase):
    session = botocore.session.get_session()
    date = datetime.datetime(2021, 8, 27, 0, 0, 0)

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

    @freeze_time(date)
    @FreezeToken(botocore.handlers.uuid)
    def create_endpoints(self, service_instance, **kwargs):
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
            if (len(service_instance['input_params']) == 0):
                try:
                    op()
                except Exception as error:
                    return "", ""
            else:
                try:
                    params = {}
                    for key, value in service_instance['input_params'].items():
                        params[key] = value
                        if (type(value) is str) :
                            if (service_instance['input_params'][key] == "::REPLACE_DATE_TIME::") :
                                params[key] = datetime.datetime(2015, 1, 1)

                    op(**params)
                except Exception as error:
                    return "", ""
            request = self.http_stubber.requests[0]
            try:    
                auth_header = request.headers['Authorization'].decode() # make authorization optional, request.headers.get("Authorization")
            except:
                auth_header = ''

            return request.url, auth_header

        else:
            return "", ""

    def build_endpoint_output_file(self):
        current_file = Path(__file__)
        neighboring_file = current_file.parent / "input_endpoint_test.json"
        output_file = current_file.parent / "output_endpoint_test.json"

        with (neighboring_file).open() as f:
            services = json.load(f)
            for service in services:
                print("service = " + service['service_name'])
                expected_endpoint, signature = self.create_endpoints(service_instance=service)
                service['expected_endpoint'] = expected_endpoint
                service['signature'] = signature

        output_file.unlink(missing_ok=True)
        output_file.touch(exist_ok=True)
        with (output_file).open(mode='w+') as out:
            output_json = json.dumps(services)
            out.write(output_json)

    def test_endpoints_with_test_file(self):
        current_file = Path(__file__)
        output_file = current_file.parent / "output_endpoint_test.json"

        def test_endpoint_equal_expected(self, actual_endpoint, expected_endpoint):
            self.assertEqual(actual_endpoint, expected_endpoint)

        def test_signature_equal_expected(self, actual_signature, expected_signature):
            self.assertEqual(actual_signature, expected_signature)

        with (output_file).open() as f:
            services = json.load(f)
            for service in services:
                expected_endpoint, signature = self.create_endpoints(service_instance=service)
                test_endpoint_equal_expected(self, service['expected_endpoint'], expected_endpoint)
                test_signature_equal_expected(self, service['signature'], signature)



test_endpoints = TestWriteExpectedEndpoints()
test_endpoints.build_endpoint_output_file()