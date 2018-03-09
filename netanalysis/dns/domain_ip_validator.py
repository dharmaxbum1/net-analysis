# Copyright 2018 Jigsaw Operations LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import asyncio
import ipaddress
import logging
import pprint
import socket
import ssl
import sys

import netanalysis.ip.info as ip_info

async def validate_ip(domain: str, ip: ip_info.IpAddress, timeout=2.0):
    """
    Returns successfully if the IP is valid for the domain.
    Raises exception if the validation fails.
    """
    cert = await ip_info.get_tls_certificate(ip, domain, timeout=timeout)
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        logging.debug("Certificate:\n{}".format(pprint.pformat(cert)))
    ssl.match_hostname(cert, domain)


def main(args):
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    all_good = True
    for ip_address in args.ip_address:
        try:
            asyncio.get_event_loop().run_until_complete(
                validate_ip(args.domain, ip_address, timeout=args.timeout))
            result_str = "VALID"
        except (ssl.CertificateError, ConnectionRefusedError, OSError, asyncio.TimeoutError) as e:
            all_good = False
            result_str = "UNKNOWN (%s)" % repr(e)
        print("IP {} is {}".format(ip_address, result_str))
    return 0 if all_good else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Checks if the given IP addresses are valid for the domain")
    parser.add_argument("domain", type=str,
                        help="The domain to validate the IPs for")
    parser.add_argument("ip_address", type=ipaddress.ip_address,
                        nargs="+", help="The IP address to query")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--timeout", type=float, default=2.0,
                        help="Timeout in seconds for getting the certificate")
    sys.exit(main(parser.parse_args()))
