# run this script in the root of the botocore repo (or change the BASE_PATH variable)

import json
import re
import random
from pathlib import Path
from typing import NamedTuple
from botocore.loaders import Loader


class UrlPattern(NamedTuple):
    service_id: str
    operation: str
    url_raw: str

    def get_params(self):
        matches = re.findall(r"\{([^\{\}]+)\}", self.url_raw)
        return matches

    def get_regex(self):
        return re.sub(r"\{[^\{\}]+\}", "(.+)", self.url_raw) #.replace("/", "\/")

BASE_PATH = Path(Loader.BUILTIN_DATA_PATH)

files_to_look_at = []
url_patterns = []
regions_list = ["us-east-1", "us-east-2", "us-west-1", "us-west-2"]

for service_dir in BASE_PATH.iterdir():
    if service_dir.is_dir():
        version_dir = max(vd for vd in service_dir.iterdir())
        files_to_look_at.append(version_dir / "service-2.json")

for path in files_to_look_at:
    with path.open() as f:
        service_model = json.load(f)
    for opname, opval in service_model.get("operations", {}).items():
        uri = opval['http']['requestUri']
        url_patterns.append(UrlPattern(
            service_id=service_model["metadata"]["serviceId"],
            operation=opname,
            url_raw=uri,
        ))

services = []
client_params = [['FIPS'], ['DualStack'], ['FIPS', 'DualStack'], []]

for pat in url_patterns:
    for region in random.sample(regions_list, 2):
        for cp in client_params:
            services.append(
                {
                    "service_id": pat.service_id,
                    "operation": pat.operation,
                    "input_params": pat.get_params(),
                    "region": region,
                    "client_params": cp,
                    "expected_endpoint": ""
                }
            )

serialized_patterns = json.dumps(services, indent=2)
f = open('input_endpoint_test.json', 'w', encoding='utf-8')
f.truncate(0)
f.write(serialized_patterns)
f.close()
