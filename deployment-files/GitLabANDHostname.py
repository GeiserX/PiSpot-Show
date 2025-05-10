#!/usr/bin/env python3

import requests
import uuid
import os

# Upload public key to GitLab #
mac_addr = hex(uuid.getnode()).replace('0x', '')
sshkey = open('/root/.ssh/id_ecdsa.pub', 'r')
sshkeyText = sshkey.read().splitlines()
r = requests.post('https://gitlab.com/api/v4/user/keys?private_token=YOUR_PRIVATE_TOKEN', data={'title':'PiSpot_HDMI_' + mac_addr, 'key':sshkeyText})
print(r.text)

# Set Hostname #
hostname = 'PiSpot_HDMI_' + mac_addr
os.system('hostnamectl set-hostname ' + hostname)

with open("/etc/hosts", "r+") as file:
    for line in file:
        if hostname in line:
           break
    else: # We are at the EOF
        file.write("127.0.1.1 " + hostname)
