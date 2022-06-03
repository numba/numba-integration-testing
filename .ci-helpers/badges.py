#!/usr/bin/env python
import os
import requests

from parse import parse

GH_API_URL = os.getenv("GH_API_URL")
GH_TOKEN = os.getenv("GH_TOKEN")
JB_ENDPOINT = os.getenv("JB_ENDPOINT")
JB_TOKEN = os.getenv("JB_TOKEN")

r = requests.get(GH_API_URL, headers={"authorization": f"token {GH_TOKEN}"})
print(f"Status Code: {r.status_code}, Response: {r.json()}")

data = r.json()
states = dict()
for elem in data:
    context = parse("ci/circleci: {package}", elem["context"])
    state = elem["state"]

    if state in ["success", "failure"]:
        states[context.named["package"]] = state

for pkg, state in states.items():
    badge_dict = {"schemaVersion": 1,
                  "label": pkg,
                  "message": "passing" if state == "success" else "failing",
                  "color": "brightgreen" if state == "success" else "red",
                  "namedLogo": "numba",
                  "logoColor": "white"}

    r = requests.post(f"{JB_ENDPOINT}/{pkg}/badge", json=badge_dict, headers={"authorization": f"token {JB_TOKEN}"})
    print(f"Status Code: {r.status_code}, Response: {r.json()}")

    r = requests.put(f"{JB_ENDPOINT}/{pkg}/badge/_perms", headers={"authorization": f"token {JB_TOKEN}"})
    print(f"Status Code: {r.status_code}, Response: {r.json()}")
