import json
import requests

from rubber_stamp_exceptions import PullNotMergeableException


BASE_URL = "https://api.github.com"
AUTH_TOKEN = "074faad559090f4adc3928e723db1ee6e3133e68"

NOT_MERGEABLE_EXCEPTION_MESSAGE = '405 Client Error: Method Not Allowed'


def get_pulls(repo, owner):
    url = "/repos/%s/%s/pulls" % (owner, repo)

    response = _make_request(url)

    return response.json()


def merge_pull(repo, owner, number, method, message=None):
    url = "/repos/%s/%s/pulls/%s/merge" % (owner, repo, number)

    data = {
        "merge_method": method
    }

    if message:
        data["commit_message"] = message

    try:
        _make_request(url, method="PUT", data=data)
    except requests.exceptions.HTTPError as e:
        if e.message == NOT_MERGEABLE_EXCEPTION_MESSAGE:
            raise PullNotMergeableException()
        raise e

    return True


def approve_pull(repo, owner, number, message=None):
    url = "/repos/%s/%s/pulls/%s/reviews" % (owner, repo, number)

    data = {
        'event': 'APPROVE',
        'body': message
    }

    _make_request(url, method="POST", data=data)
    return True


def _make_request(endpoint, method="GET", data=None):
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token %s" % AUTH_TOKEN,
        "Content-type": "application/json"
    }
    if data:
        data = json.dumps(data)
    
    response = requests.request(method, BASE_URL + endpoint, headers=headers, data=data)
    response.raise_for_status()

    return response
