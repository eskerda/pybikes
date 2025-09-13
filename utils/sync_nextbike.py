"""Very dumb script that goes through the public list of nextbike feeds and
syncs it with pybikes. Might work for 80% of the cases.
"""

import json

import requests
from slugify import slugify

import pybikes

NEXTBIKE_LIVE_FEED = "https://api.nextbike.net/maps/nextbike-live.json"

# There are many tests systems. Put them here so they are ignored
ignored_domains = [
    "wh",
    "tb",
    "bs",
    "bw",
    "lt",
]


def pybikes_net(country):
    # Try to detect when a system has a distinct name other than
    # nextbike-city. Or otherwise, detect when it is _not_ relevant
    # that is easier I guess
    city = " - ".join([c["name"] for c in country["cities"]])
    tag = slugify(country["name"])
    if "nextbike" not in tag:
        tag = "nextbike-%s" % tag

    return {
        "domain": country["domain"],
        "tag": tag,
        "meta": {
            "name": country["name"],
            "city": city,
            "country": country["country"],
            "latitude": country["lat"],
            "longitude": country["lng"],
        },
    }


data = requests.get(NEXTBIKE_LIVE_FEED).json()
py_data = pybikes.get_data("nextbike")
py_gbfs_data = pybikes.get_data("nextbike_gbfs")

domains = [c["domain"] for c in data["countries"]]
py_domains = [i["domain"] for i in py_data["instances"]]
py_domains += [i["domain"] for i in py_gbfs_data["instances"]]

instances = []

for i in py_data["instances"]:
    if i["domain"] not in domains:
        # domain not present, check if it works
        instance = pybikes.get(i["tag"])
        try:
            instance.update()
        except:
            # its borked, remove it
            continue

    # keep it
    instances.append(i)

# Now look for new ones
for country in data["countries"]:
    places = sum([len(c["places"]) for c in country["cities"]])
    # Ignore empty networks
    if places == 0:
        # Check if such system is in pybikes and remove it
        n = next((i for i in instances if i["domain"] == country["domain"]), None)
        if n:
            instances.remove(n)
        continue

    # ignore already supported network
    if country["domain"] in py_domains:
        continue

    if country["domain"] in ignored_domains:
        continue

    instances.append(pybikes_net(country))


py_data["instances"] = instances

print(json.dumps(py_data, indent=4))
