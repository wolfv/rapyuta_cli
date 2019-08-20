import click
import requests
import json
import pprint
# import pandas as pd
# get all projects

HEADERS = None

try:
    with open("./.rapyuta") as f:
        HEADERS = json.load(f)
except:
    print("Could not find rayputa initialization file.")

def get_url(endpoint):
    if endpoint.startswith('user'):
        return "https://gaapiserver.apps.rapyuta.io/api/{}".format(endpoint)
    return "https://gacatalog.apps.rapyuta.io/{}".format(endpoint)

import click

@click.group()
def cli():
    pass

@click.command()
def user():
    res = requests.get(get_url('user/me/get'), headers=HEADERS)
    pprint.pprint(res.json())

@click.group()
def deployments():
    pass

@click.command(name='list')
@click.argument('project')
def xlist(project):
    me = requests.get(get_url('user/me/get'), headers=HEADERS)
    me = me.json()

    # find project GUID
    for p in me['projects']:
        if p['name'] == project or p['guid'] == project:
            guid = p['guid']

    project_header = {
        "project": guid
    }

    H = HEADERS
    H.update(project_header)
    deployments = requests.get(get_url('deployment/list'), headers=H)


    # df = pd.read_json(deployments.text)
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(df)

    pprint.pprint(deployments.json())

deployments.add_command(xlist)
cli.add_command(user)
cli.add_command(deployments)

if __name__ == '__main__':


    cli()
