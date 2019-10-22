import click
import requests
import json
import pprint
import os
import time
import click

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

def find_project(project):
    me = requests.get(get_url('user/me/get'), headers=HEADERS)
    me = me.json()

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
    for d in deployments:
        created = utils.pretty_date(dateutil.parser.parse(d['CreatedAt']))
        if d['DeletedAt']:
            deleted = utils.pretty_date(dateutil.parser.parse(d['DeletedAt']))
        else:
            deleted = ""
        data = [
            ['Name', d['name']],
            ['Created At', created],
            ['Deleted At', deleted],
        ]
        table = SingleTable(data)
        print(table.table)


    # df = pd.read_json(deployments.text)
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(df)

    # pprint.pprint(deployments.json())

@click.command(name='list')
def catalog_list():
    H = HEADERS
    catalog = requests.get(get_url('v2/catalog'), headers=H)
    catalog = deployments.json()
    pprint.pprint(catalog)
    return
    for d in deployments:
        created = utils.pretty_date(dateutil.parser.parse(d['CreatedAt']))
        if d['DeletedAt']:
            deleted = utils.pretty_date(dateutil.parser.parse(d['DeletedAt']))
        else:
            deleted = ""
        data = [
            ['Name', d['name']],
            ['Created At', created],
            ['Deleted At', deleted],
        ]
        table = SingleTable(data)
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
