import os
import json
import requests
from scr.settings import *

def checkForUpdates():
    with open(f'{INSTALL_PATH}\\appdata.json', 'r') as f:
        current_version = json.load(f)['version']

    r = requests.get(f'{GITHUB_REPO}/latest.json')
    latest_version = r.json()['version']

    if current_version != latest_version:
        return True
    
def downloadUpdate():
    r = requests.get(f'{GITHUB_REPO}/latest.json')
    data = r.json()

    if "new" in data:
        for file_path in data["new"]:
            repo_path = f'{GITHUB_REPO}/{file_path}'
            local_path = f'{HOME_PATH}\\{file_path}'

            r = requests.get(repo_path)
            with open(local_path, 'wb') as f:
                f.write(r.content)

    if "updated" in data:
        for file_path in data["updated"]:
            repo_path = f'{GITHUB_REPO}/{file_path}'
            local_path = f'{HOME_PATH}\\{file_path}'

            r = requests.get(repo_path)
            with open(local_path, 'wb') as f:
                f.write(r.content)