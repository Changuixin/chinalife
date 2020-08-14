import requests


def request(method, url, **kwargs):
    requests.packages.urllib3.disable_warnings()
    return requests.request(method, url, **kwargs, verify=False)


def get(url, params=None, **kwargs):
    requests.packages.urllib3.disable_warnings()
    return requests.get(url, params, **kwargs, verify=False)


def options(url, **kwargs):
    requests.packages.urllib3.disable_warnings()
    return requests.options(url, **kwargs, verify=False)


def post(url, data=None, **kwargs):
    requests.packages.urllib3.disable_warnings()
    return requests.post(url, data, **kwargs, verify=False)
