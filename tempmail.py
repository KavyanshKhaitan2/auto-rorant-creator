import random
import string
import requests
import json
from typing import Literal
import time
import pyperclip

TOKEN = None


def hit_endpoint(
    method: Literal["GET"] | Literal["POST"],
    path,
    body=None,
    base_url="https://api.mail.tm",
    token=None,
):
    if token is None:
        token = TOKEN
    headers = {}
    if body:
        headers["accept"] = "application/ld+json"
        headers["Content-Type"] = "application/json"
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"

    r = requests.request(
        method, base_url + path, data=json.dumps(body), headers=headers
    )
    if r.status_code == 209:
        print("[Warning] Reached rate limit, waiting for a second...")
        time.sleep(1)
    if r.status_code < 200 or r.status_code > 204:
        raise Exception(f"NOT OK!!! {r} {r.text}")
    return r.json()


def get_random_string(length=10):
    output = ""
    for _ in range(length):
        output += random.choice(string.ascii_letters)
    return output.lower()


def register_account(address, password):
    global TOKEN
    hit_endpoint(
        "POST", "/accounts", body={"address": address, "password": password}
    )
    token = hit_endpoint(
        "POST", "/token", body={"address": address, "password": password}
    )["token"]
    TOKEN = token
    return token


def get_email():
    domains = hit_endpoint("GET", "/domains")["hydra:member"]
    return "tmp" + get_random_string() + "@" + domains[0]["domain"]


# Mail example:
mail_example = {
    "@id": "/messages/6959faac416a662eec6a6438",
    "@type": "Message",
    "id": "6959faac416a662eec6a6438",
    "msgid": "<20260104052914.ff9cb9b13f6b64b5@mg.dupdub.com>",
    "from": {"address": "dupdub-support@mobvoi.com", "name": "DupDub"},
    "to": [{"address": "tmpzedzaauabm@airsworld.net", "name": ""}],
    "subject": "Welcome to DupDub Family!",
    "intro": "Hi, tmpzedzaauabm Welcome to your DupDub Family! Your Verification Code is 6600 Please enter the code above to complete the…",
    "seen": False,
    "isDeleted": False,
    "hasAttachments": False,
    "size": 7098,
    "downloadUrl": "/messages/6959faac416a662eec6a6438/download",
    "sourceUrl": "/sources/6959faac416a662eec6a6438",
    "createdAt": "2026-01-04T05:29:14+00:00",
    "updatedAt": "2026-01-04T05:29:16+00:00",
    "accountId": "/accounts/6959fa77d857843ddd03d524",
}

if __name__ == "__main__":
    address = get_email()
    print("E-mail address:", address)
    pyperclip.copy(address)
    print('📎  copied address to clipboard')
    register_account(address, "temp")
    emails_found = 0
    while True:
        time.sleep(1)
        emails = hit_endpoint("GET", "/messages")["hydra:member"]
        if len(emails) == emails_found:
            print(f"No new emails; still refreshing. {get_random_string()}", end="\r")
            continue
        print()
        emails_found += 1
        email = emails[-1]
        if email['from']['address'] == 'dupdub-support@mobvoi.com' or email['from']['name'] == 'DupDub':
            print("✅ E-mail received from DupDub!")
            usr = address.split('@')
            body:str = email['intro']
            otp = None
            for token in body.split():
                is_numeric = True
                for char in token:
                    if char not in '01234567890':
                        is_numeric = False
                        break
                if is_numeric:
                    otp = token
                    break
            
            if otp:
                print(f"OTP Received: {otp}")
                pyperclip.copy(otp)
                print('📎  copied otp to clipboard')
                break
            else:
                print("No OTP found! Still waiting...")