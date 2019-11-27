import click
import requests
import json
import pprint
import os
import time
import click

from colorama import init, Fore, Back, Style
init()

from terminaltables import SingleTable
from . import utils
import dateutil.parser

# import pandas as pd
# get all projects

HEADERS = None

try:
    if os.path.exists('./.rapyuta'):
        with open("./.rapyuta") as f:
            HEADERS = json.load(f)

    with open(os.path.expanduser('~/.config/rapyuta_cli/rapyuta')) as f:
        HEADERS = json.load(f)
except:
    print("Could not find rayputa initialization file.")

def get_url(endpoint):
    if endpoint.startswith('user'):
        return "https://gaapiserver.apps.rapyuta.io/api/{}".format(endpoint)
    return "https://gacatalog.apps.rapyuta.io/{}".format(endpoint)

def find_project(project=None):
    me = requests.get(get_url('user/me/get'), headers=HEADERS)
    me = me.json()

    if not project:
        return me['projects'][0]['guid']

    # find project GUID
    for p in me['projects']:
        if p['name'] == project or p['guid'] == project:
            guid = p['guid']

    return guid

@click.group()
def cli():
    pass

@click.command()
def user():
    res = requests.get(get_url('user/me/get'), headers=HEADERS)
    res = res.json()
    # pprint.pprint()
    data = [
        ['Email', res['emailID']],
        ['Name', "{} {}".format(res['firstName'], res['lastName'])],
        ['Projects', ', '.join([p['name'] for p in res['projects']])]
    ]
    table = SingleTable(data)
    print(table.table)

@click.group()
def deployments():
    pass

@click.group()
def catalog():
    pass

@click.command(name='list')
@click.argument('project')
def deployments_list(project):
    guid = find_project(project)

    project_header = {
        "project": guid
    }

    H = HEADERS
    H.update(project_header)
    deployments = requests.get(get_url('deployment/list'), headers=H)
    deployments = deployments.json()
    # pprint.pprint(deployments)
    t_header = [['Name', 'Package', 'Created', 'Deleted', 'Phase']]

    def format_phase(phase):
        if phase == 'Deployment stopped':
            return Fore.RED + phase + Style.RESET_ALL
        elif phase == 'Succeeded':
            return Fore.GREEN + phase + Style.RESET_ALL
        elif phase == 'Partially deprovisioned':
            return Fore.YELLOW + phase + Style.RESET_ALL
        else:
            return phase

    data = []
    for d in deployments:
        raw_create = dateutil.parser.parse(d['CreatedAt'])
        created = utils.pretty_date(raw_create)
        if d['DeletedAt']:
            deleted = utils.pretty_date(dateutil.parser.parse(d['DeletedAt']))
        else:
            deleted = ""
        data.append([d['name'], d['packageName'], created, deleted, format_phase(d['phase']), raw_create])

    data = sorted(data, key=lambda x: x[-1])
    data = [row[:-1] for row in data] # remove the sort key
    table = SingleTable(t_header + data)
    print(table.table)

@click.command(name='list')
@click.option('--project', default=None)
def catalog_list(project):
    H = HEADERS
    H['project'] = find_project(project)
    catalog = requests.get(get_url('v2/catalog'), headers=H)
    catalog = catalog.json()
    # pprint.pprint(catalog)
    t_headers = [['Name', 'Created', 'Version']]
    data = []
    for d in catalog['services']:
        raw_create = dateutil.parser.parse(d['metadata']['creationDate'])
        created = utils.pretty_date(raw_create)
        data.append([d['name'], created, d['metadata']['packageVersion'], raw_create])

    data = sorted(data, key=lambda x: x[0] + x[2])
    data = [row[:-1] for row in data]

    table = SingleTable(t_headers + data)
    print(table.table)

def print_response(res):
    print('HTTP/1.1 {status_code}\n{headers}\n\n{body}'.format(
        status_code=res.status_code,
        headers='\n'.join('{}: {}'.format(k, v) for k, v in res.headers.items()),
        body=res.content,
    ))    # print(res.content)

def print_request(req):
    print('HTTP/1.1 {method} {url}\n{headers}\n\n{body}'.format(
        method=req.method,
        url=req.url,
        headers='\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        body=req.body,
    ))


# request debugging:
# import logging
# import http.client as http_client

# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True


@click.command(name='upload')
@click.argument('project')
@click.argument('file')
def catalog_upload(project, file):
    guid = find_project(project)

    with open(file, 'r') as fi:
        content = fi.read()

    H = HEADERS
    H.update({'project': guid})
    print(H)
    url = get_url('serviceclass/add')
    res = requests.post(url, data=content, headers=H)

    pprint.pprint(res.json())

deployments.add_command(deployments_list)
catalog.add_command(catalog_list)
catalog.add_command(catalog_upload)
cli.add_command(user)
cli.add_command(deployments)
cli.add_command(catalog)

if __name__ == '__main__':


    cli()
