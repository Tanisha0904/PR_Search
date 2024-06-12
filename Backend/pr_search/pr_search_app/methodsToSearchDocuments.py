import csv
import json
import traceback
from venv import logger
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import re
import requests

from .secrets_1 import GITHUB_TOKEN


def get_response_from_version_compare_api(
    owner, repo, base_version, compare_version
):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/compare/{base_version}...{compare_version}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()

    else:
        print(
            f"Failed to fetch commits from version {base_version} to version {compare_version}: {response.status_code}"
        )
        return None


def get_pr_data(owner, repo, number):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}"
    response = requests.get(url, headers=headers)
    json_data = []
    if response.status_code == 200:
        pr = response.json()
        label_names = set()
        labels = pr.get("labels", [])
        for label in labels:
            label_name = label.get("name", "")  # Get the name of the label
            label_names.add(label_name)  # Add the label name to the set
        pr_data = {
            "number": pr["number"],
            "title": pr["title"],
            "body": pr["body"],
            "labels": list(label_names)
        }
        json_data.append(pr_data)
        return pr_data

    else:
        print(f"Failed to fetch pull requests: {response.status_code}")
        return None


def get_pr_number_list(owner, repo, api_response, data={}):
    message_json_data = []
    pattern = r"\(#(\d+)\)"  # pattern to match "(#number)" in the commit messages

    data = api_response["commits"]

    for commit_data in data:
        commit_message = commit_data["commit"]["message"]
        match = re.search(pattern, commit_message)

        if match:
            number = match.group(1)  # group(1) will capture the number inside (#number)
            message_json_data.append(get_pr_data(owner, repo, number))
    sorted_data = sorted(message_json_data, key=lambda x: x["number"])
    return sorted_data



def read_data_from_json(comparisonData_sorted_json, n, owner, repo):
    with open(comparisonData_sorted_json, 'r') as file:
        data = json.load(file)

    filtered_data = []
    for key, value in data.items():
        if value["rank"] <= n:
            
            filtered_data.append({
                "index": value["rank"],
                "number": value["number"],
                "title": value["title"],
                "link": f"https://github.com/{owner}/{repo}/pull/{value['number']}"
            })

    return json.dumps(filtered_data, indent=4)
