#!/usr/bun/env python3

import os
import subprocess
import yaml

with open('hosts.yml', 'r') as fin:
    hosts = yaml.safe_load(fin)

hosts_all = hosts['all'].get('hosts', {})
children = hosts['all'].get('children', {})
unique_hosts = set()

if hosts_all:
    for host_name, host in hosts_all.items():
        unique_hosts.add(host['ansible_host'])

if children:
    for group_name, group in children.items():
        if not group['hosts']:
            continue
        for host_name, host in group['hosts'].items():
            unique_hosts.add(host['ansible_host'])

for host in unique_hosts:
    subprocess.call(['ssh-keygen', '-f', os.environ['HOME'] + '/.ssh/known_hosts', '-R', host])
