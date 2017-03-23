#!/usr/bin/env python3
# coding: utf-8
import argparse
import requests
import json
from pprint import pprint


class AuthError(Exception):
    pass


class UnknownError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def read_token():
    try:
        with open('.pddtoken', 'rt') as t:
            return t.read().strip()
    except FileNotFoundError:
        raise AuthError()


def read_last_ip():
    try:
        with open('.lastip', 'rt') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def write_last_ip(ip):
    try:
        with open('.lastip', 'wt') as f:
            return f.write(str(ip))
    except FileNotFoundError:
        return None

def get_domain_records(hostname):
    domain = hostname.split('.', 1)[1]
    auth_token = read_token()
    if auth_token is None:
        raise AuthError()

    headers = {
        'PddToken': str(auth_token),
    }
    url = "https://pddimp.yandex.ru/api2/admin/dns/list?domain={0}".format(domain)
    result = requests.get(url, headers=headers).text.strip()
    try:
        return json.loads(result)['records']
    except Exception:
        return []


def write_ip_value(ip, hostname, record_id):
    auth_token = read_token()
    if auth_token is None:
        raise AuthError()

    url = "https://pddimp.yandex.ru/api2/admin/dns/edit"
    headers = {
        'PddToken': auth_token,
    }
    post_data = {
        'domain': hostname.split('.', 1)[1],
        'subdomain': hostname,
        'record_id': record_id,
        'content': ip,
    }
    print('writing new ip {0} to hostname {1}'.format(ip, hostname))
    result = requests.post(url, headers=headers, data=post_data)
    if result.status_code == 200:
        if json.loads(result.text)['success'] == 'ok':
            print('success set')
            return 'ok'
    raise UnknownError('some error')


def auth():
    print('got to https://pddimp.yandex.ru/api2/admin/get_token')
    print('and place token to .pddtoken')


def get_my_ip():
    """
    http://ipinfo.io/ip
    http://ipecho.net/plain
    http://ifconfig.me
    http://ipv4.icanhazip.com
    http://v4.ident.me
    http://checkip.amazonaws.com
    """
    return requests.get("http://ipinfo.io/ip").text.strip()


def main(args):
    if args.auth:
        return auth()
    else:
        try:
            last_ip = read_last_ip()
            my_ip = get_my_ip()
            if last_ip != my_ip:
                records = get_domain_records(args.host)
                for r in records:
                    if r['fqdn'] == args.host:
                        write_ip_value(my_ip, args.host, r['record_id'])
                        write_last_ip(my_ip)
                        break
                else:
                    print('Hostname not found. Maybe you should create some.')
        except AuthError:
            return auth()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Write your internet ip to some hostname hosted at pdd.yandex.ru")
    parser.add_argument("-a", "--auth", help="New authorization", action='store_true', required=False)
    parser.add_argument("--host", help="Hostname to set", type=str, required=True)
    args = parser.parse_args()
    main(args)
