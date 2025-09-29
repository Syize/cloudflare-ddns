import os
from os.path import exists, dirname, abspath
from json import load, dump
from requests import get, put


if __name__ == "__main__":
    zone = "syize.cn"
    dns_record_list = ["ssh.syize.cn"]

    envs = os.environ

    # check if CLOUDFLARE_EMAIL and CLOUDFLARE_KEY is set
    if not "CLOUDFLARE_EMAIL" in envs or not "CLOUDFLARE_KEY" in envs:
        print("[ERROR] You need to set 'CLOUDFLARE_EMAIL' and 'CLOUDFLARE_KEY' environment variables")
        exit(1)

    cloudflare_email = envs["CLOUDFLARE_EMAIL"]
    cloudflare_key = envs["CLOUDFLARE_KEY"]

    # get IPv4 address from the result of command "hostname -i"
    res = os.popen("hostname -i").readline().strip()
    ip_address = res.split()[0]

    # check if the IP address changed
    record_path = f"{abspath(dirname(__file__))}/ip_record.json"
    is_changed = False

    if not exists(record_path):
        is_changed = True
    else:
        with open(record_path, "r") as f:
            ip_record = load(f)

        old_ip_address = ip_record["ip"]
        if old_ip_address != ip_address:
            is_changed = True

    if not is_changed:
        print("[INFO] No changes detected.")
        exit(0)

    # update ip_record.json
    with open(record_path, "w") as f:
        dump({"ip": ip_address}, f)

    # update DNS of the cloudflare
    # proxy settings for requests
    proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}

    # get zone id
    request_url = f"https://api.cloudflare.com/client/v4/zones?name={zone}&status=active"
    headers = {
        "X-Auth-Email": cloudflare_email,
        "Authorization": f"Bearer {cloudflare_key}",
        "Content-Type": "application/json",
    }
    res = get(request_url, headers=headers, proxies=proxies)
    zone_id = res.json()["result"][0]["id"]

    for _record in dns_record_list:
        # get dns record id
        request_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={_record}"
        res = get(request_url, headers=headers, proxies=proxies)
        dns_record_id = res.json()["result"][0]["id"]

        # update the dns record
        request_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{dns_record_id}"
        data = {
            "type": "A",
            "name": _record,
            "content": ip_address,
            "ttl": 60,
            "proxied": False,
            "comment": "",
        }
        res = put(request_url, headers=headers, proxies=proxies, json=data)
        success_status = res.json()["success"]
        print(f"[INFO] {_record}: {success_status}")
