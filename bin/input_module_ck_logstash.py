"""
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
"""
# encoding = utf-8
# pylint: disable=missing-function-docstring,line-too-long,invalid-name

import hashlib
import json
import os
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from collections import OrderedDict
import requests

try:
    from splunklib import client, results
except ImportError:
    raise ImportError('Please run this from Splunk')

HOST = os.getenv("SPLUNK_HOST", "localhost")
PORT = int(os.getenv("SPLUNK_PORT", "8089"))
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'
TIME_FORMAT_QUERY = '%Y-%m-%dT%H:%M:%S'


def validate_input(helper, definition):  # pylint: disable=unused-argument
    pass


def collect_events(helper, ew):  # pylint: disable=too-many-locals
    opt_username = helper.get_arg('username')
    opt_password = helper.get_arg('password')
    opt_storage = helper.get_arg('storage')
    opt_api = helper.get_arg('api')
    opt_query = helper.get_arg("query")
    opt_earliest_time = int(helper.get_arg("earliest_time"))
    opt_latest_time = int(helper.get_arg("latest_time"))
    opt_endpoint = helper.get_arg("endpoint")

    input_data = {
        "opt_username": opt_username,
        "opt_password": opt_password,
        "opt_storage": opt_storage,
        "opt_query": opt_query,
        "opt_endpoint": opt_endpoint
    }

    now = datetime.now(tzlocal())
    now = now - timedelta(seconds=now.second)

    session_key = helper.context_meta['session_key']

    service = client.connect(host=HOST, port=PORT, token=session_key)

    earliest_time = (now - timedelta(seconds=-opt_earliest_time +
                                             60)).strftime(TIME_FORMAT_QUERY)
    latest_time = (
            now -
            timedelta(seconds=-opt_latest_time + 60)).strftime(TIME_FORMAT_QUERY)
    input_data["earliest_time"] = earliest_time
    input_data["latest_time"] = latest_time

    kwargs_export = {
        "earliest_time": earliest_time,
        "latest_time": latest_time,
        "search_mode": "normal",
        "preview": False
    }

    exportsearch_results = service.jobs.export(str(opt_query), **kwargs_export)
    reader = results.ResultsReader(exportsearch_results)

    if opt_api == "verify":
        verify_api(reader, input_data, service, helper, ew)


def register_api(reader, input_data, helper, ew):  # pylint: disable=too-many-locals
    logs = []
    for result in reader:
        if isinstance(result, dict):
            logs += [list(str(result))]

    logs.sort()
    length = len(logs)
    opt_username = input_data["opt_username"]
    opt_password = input_data["opt_password"]
    opt_storage = input_data["opt_storage"]
    opt_endpoint = input_data["opt_endpoint"]

    logs = str(logs)
    _hash = make_hash(logs)

    logindata = login(opt_username, opt_password, opt_endpoint)
    entity_id = register(logindata, _hash, opt_endpoint, opt_storage)

    _time = datetime.now(tzlocal())
    _timestr = _time.strftime(TIME_FORMAT)
    res = {
        "hash": str(_hash),
        "query": input_data["opt_query"],
        "_time": _timestr,
        "running_script": _timestr,
        "assetId": entity_id.get("assetId"),
        "earliest_time": input_data["earliest_time"],
        "latest_time": input_data["latest_time"],
        "length": length
    }

    event = helper.new_event(source=helper.get_input_type(),
                             index=helper.get_output_index(),
                             sourcetype=helper.get_sourcetype(),
                             data=json.dumps(res))
    ew.write_event(event)


def verify_api(reader, input_data, service, helper, ew):  # pylint: disable=too-many-locals
    opt_username = input_data["opt_username"]
    opt_password = input_data["opt_password"]
    opt_storage = input_data["opt_storage"]
    opt_endpoint = input_data["opt_endpoint"]
    for result in reader:
        if isinstance(result, dict):
            dict_res = result["_raw"]
            dict_res = json.loads(dict_res)
            asset_id = dict_res["assetId"]
            message = dict_res["message"]
            uuid = dict_res["uuid"]
            port = dict_res["port"]
            host = dict_res["host"]
            version = dict_res["@version"]
            timestamp = dict_res["@timestamp"]

            content = {}
            content["uuid"] = uuid
            content["port"] = int(port)
            content["message"] = message
            content["@version"] = version
            content["@timestamp"] = timestamp
            content["host"] = host
            hash_content = json.dumps(OrderedDict(sorted(content.items())), separators=(",", ":"))

            hash_ = make_hash(hash_content)

            logindata = login(opt_username, opt_password, opt_endpoint)
            response = verify(logindata, asset_id, hash_, opt_endpoint,
                              opt_storage)
            verified = response.get("verified")

            _time = datetime.now(tzlocal())
            _timestr = _time.strftime(TIME_FORMAT)
            res = {
                "@version": version,
                "assetId": asset_id,
                "_time": _timestr,
                "hash": hash_,
                "host": host,
                "message": message,
                "port": port,
                "uuid": uuid,
                "verified": verified
            }

            event = helper.new_event(source=helper.get_input_type(),
                                     index=helper.get_output_index(),
                                     sourcetype=helper.get_sourcetype(),
                                     data=json.dumps(res))
            ew.write_event(event)


def login(username, password, opt_endpoint):
    """Construct an ProvenanceValidator object by logging in to the
    PencilDATA server.
       Both the username and the password arguments may be given as str.
       Password bytes sequence will be submitted to the server encoded in
    base64. After a successful authentication, the login_data property is
    populated by a dictionary that (among other things) contains the
    user's AccessToken. If the authentication fails, an exception is raised
    (actually a HTTPError: Bad Request)."""
    url = "{}{}".format(opt_endpoint, "/token/")
    data = {'userId': username, 'password': password}
    head = {"Content-Type": "application/json"}
    res = requests.request("POST", url, data=json.dumps(data), headers=head)
    return res.json()


def make_hash(val):
    hash_object = hashlib.sha256()
    hash_object.update(val.encode('utf-8'))
    return hash_object.hexdigest()


def register(login_data, hash_, opt_endpoint, storage="pencil"):
    """Register a file (by its SHA-256 hash) in your PencilDATA account.
    Warning: this method does not check if the file hash exists in the
    registers. It returns the asset id for the file.
    Arguments:
    login_data: Access Token
    storage: 'public' or 'private'. Whether to store the file entry in the
    public or in the private database at the PencilDATA server."""
    datajson = {"hash": hash_, "storage": storage}
    url = "{}{}".format(opt_endpoint, "/register/")
    head = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(login_data['data']['accessToken'])
    }  # Request HTTP headers
    res = requests.request("POST",
                           url,
                           data=json.dumps(datajson),
                           headers=head)
    return res.json()


def verify(login_data, asset_id, hash_, opt_endpoint, storage="pencil"):
    """Verify a file (by its SHA-256 hash) in your PencilDATA account.
    Warning: this method does not check if the file hash exists in the
    registers. It returns the asset id for the file.
    Arguments:
    file: file name or a file object. If file is given as a file-like
    object, this method advances the current position of the file until
    its end, but it does not close the file-like object
    storage: 'public' or 'private'. Whether to store the file entry in the
    public or in the private database at the PencilDATA server."""
    datajson = {"hash": hash_, "storage": storage}
    url = "{}{}{}".format(opt_endpoint, "/verify/", str(asset_id))
    head = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(login_data['data']['accessToken'])
    }  # Request HTTP headers
    res = requests.request("GET", url, params=datajson, headers=head)
    return res.json()