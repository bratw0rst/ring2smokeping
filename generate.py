import os
import requests

# Make directory to store generated files in 
try:
    os.makedirs("/tmp/smokeping")
except FileExistsError:
    # directory already exists
    pass

# URL of the API
url = 'https://api.ring.nlnog.net/1.0/nodes/active'

# Make a request to the API and get the JSON response
response = requests.get(url).json()

# Extract the nodes from the response
nodes = response['results']['nodes']

# Create a separate group and config file for each country code
country_codes = set(node['countrycode'] for node in nodes)
for country_code in country_codes:
    config_entry = f"@include /etc/smokeping/config.d/Targets.d/nlnog-ring/{country_code}.conf\n"
    with open(f'/tmp/smokeping/ring.conf', 'a') as f:
        f.write(config_entry)

    # Initialize the group and config file contents
    country_contents = f"""
++ {country_code}
menu = {country_code}
title = {country_code}
"""

    # Loop through the nodes for the current country code
    for node in nodes:
        if node['countrycode'] == country_code:
            # Get the participant information for the current node
            participant_id = node['participant']
            participant_url = f"https://api.ring.nlnog.net/1.0/participants/{participant_id}"
            participant_response = requests.get(participant_url).json()
            participant_name = participant_response['results']['participants'][0]['company']

            # Remove the ".ring.nlnog.net" suffix from the hostname
            hostname = node['hostname'].split(".ring.nlnog.net")[0]

            # Add the node to the group and config file contents
            country_contents += f"""
+++ {hostname}
menu = {participant_name} (AS{node['asn']}) - {hostname}
title = {participant_name} (AS{node['asn']}) - {hostname} - {node['ipv4']}
host = {node['ipv4']}
"""
    # Write the group and config file contents to files
    with open(f'/tmp/smokeping/{country_code}.conf', 'w') as f:
        f.write(country_contents)

# Sort file contents
with open('/tmp/smokeping/ring.conf', 'r') as f:
    lines = f.readlines()
    lines.sort()

with open('/tmp/smokeping/ring.conf', 'w') as f:
    for line in lines:
        f.write(line)

with open('/tmp/smokeping/ring.conf', 'w') as f:
    # Write new content to file
    new_content = (
        "+ nlnogring\n"
        "menu = NLNOG RING\n"
        "title = NLNOG RING nodes\n\n"
    )
    f.write(new_content)
    # Write sorted existing content to file
    for line in lines:
        f.write(line)
