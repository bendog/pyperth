from itertools import zip_longest
import datetime
import pytz

import requests
from cachetools import cached, TTLCache

from helpers import strip_tags

PERTH_TIMEZONE = pytz.timezone("Australia/Perth")
MEETUP_EVENTS_URL = "https://api.meetup.com/Perth-Django-Users-Group/events/"


@cached(cache=TTLCache(maxsize=1024, ttl=60 * 15))  # cache for 15 minutes
def get_meetups():
    """ get all the upcoming meetup events """
    results = None  # return None only if the request fails
    try:
        response = requests.get(MEETUP_EVENTS_URL)
        if response.status_code == 200:
            results = [
                {
                    "event_id": event["id"],
                    "event_name": event["name"],
                    "event_url": event["link"],
                    "og_event_name": "({}) {}".format(
                        datetime.datetime.fromtimestamp(
                            event["time"] / 1000.0, PERTH_TIMEZONE
                        ).strftime("%D %d %M"),
                        event["name"],
                    ),
                    "event_address": "{}, {}".format(
                        event["venue"]["name"], event["venue"]["address_1"]
                    )
                    if "venue" in event
                    else "",
                    "event_description": event["description"],
                    "og_event_description": strip_tags(event["description"]).encode(
                        "ascii", "ignore"
                    ),
                    "event_yes_rsvp_count": event["yes_rsvp_count"],
                    "event_datetime": datetime.datetime.fromtimestamp(event["time"] / 1000.0, PERTH_TIMEZONE),
                }
                for event in sorted(response.json(), key=lambda d: d["time"])
            ]

    except requests.exceptions.RequestException as e:
        print(e)  # need to log this somehow
    return results


