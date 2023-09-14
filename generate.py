#!/usr/bin/env python3
#-.- coding: utf8 -.-

import os
import requests

base_url = f"https://api.ring.nlnog.net/1.0/"
output_path = "/tmp/smokeping"

def get_nodes(url):
    """Make a request to the API and get the JSON response."""
    response = requests.get(url).json()

    # Extract the nodes from the response
    return response['results']['nodes']


def get_country_codes(nodes):
    """Prepare a dictionary to collect nodes per country_code."""
    return {node['countrycode']: [] for node in nodes}


def write_ring_config(country_codes):
    """Generate a ring.conf which loads all country configs."""
    header = (
        "+ nlnogring\n"
        "menu = NLNOG RING\n"
        "title = NLNOG RING nodes\n\n"
    )

    with open(f'{output_path}/ring.conf', 'w') as f:
        f.write(header)
        f.writelines(f"@include /etc/smokeping/config.d/Targets.d/nlnog-ring/{country_code}.conf\n"
                     for country_code in sorted(country_codes.keys()))


def resolve_participant_name(participant_id):
    """What's his face?"""
    participant_url = f"{base_url}/participants/{participant_id}"
    res = requests.get(participant_url).json()
    return res['results']['participants'][0]['company']


def write_country_configs(nodes, country_codes):
    """Generate a config for each country code for all active nodes."""

    for node in nodes:
        country_codes[node['countrycode']].append(
            {
                'asn': node['asn'],
                'ipv4': node['ipv4'],
                'ipv6': node['ipv6'],
                'participant_name': resolve_participant_name(node['participant']),
                'hostname': node['hostname'].removesuffix(".ring.nlnog.net")
            }
        )

    # Initialize the group and config file contents
    country_header = """
        ++ {country_code}
        menu = {country_code}
        title = {country_code}
        """

    # Add the node to the group and config file contents
    country_contents = """
        +++ {hostname}
        menu = IPv4: {participant_name} (AS{asn}) - {hostname}
        title = {participant_name} (AS{asn}) - {hostname} - {ipv4}
        host = {ipv4}
        +++ {hostname}v6
        menu = IPv6: {participant_name} (AS{asn}) - {hostname}
        probe = FPing6
        title = {participant_name} (AS{asn}) - {hostname} - {ipv6}
        host = {ipv6}
        """

    # Write the country group config file contents
    for country, participants in country_codes.items():
        with open(f'{output_path}/{country}.conf', 'w') as f:
            f.write(country_header)
            f.writelines(
                country_contents.format(**p)
                for p in participants
            )


def main():
    # Make directory to store generated files in
    try:
        os.makedirs("/tmp/smokeping")
    except FileExistsError:
        # directory already exists
        pass

    # URL of the API
    url = f"{base_url}/nodes/active"

    nodes = get_nodes(url)
    country_codes = get_country_codes(nodes)

    write_ring_config(country_codes)
    write_country_configs(nodes, country_codes)


if __name__ == "__main__":
    main()
