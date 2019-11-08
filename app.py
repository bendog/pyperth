import datetime
from itertools import zip_longest

import pytz
from flask import Flask, render_template, request
from flask_humanize import Humanize

from meetups import get_meetups

PERTH_TIMEZONE = pytz.timezone("Australia/Perth")


app = Flask(__name__)
humanize = Humanize(app)


@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now(tz=PERTH_TIMEZONE)}


@app.route('/')
def home_page():
    date_str = "".join(list(request.args.keys())).strip()
    if date_str:
        now = datetime.datetime.now(tz=PERTH_TIMEZONE)
        default_args = (now.year, now.month, 1)
        user_args = list(map(int, date_str.split("-")))
        args = tuple(
            user_num or default for default, user_num in zip_longest(default_args, user_args)
        )
        date = datetime.datetime(*args, tzinfo=PERTH_TIMEZONE)
    else:
        date = datetime.datetime.now(tz=PERTH_TIMEZONE)
    try:
        # coming_event = get_events('upcoming', date)[0]
        events = get_meetups()
        coming_event = events[0]
    except (IndexError, AttributeError):
        coming_event = {
            "event_name": "No upcoming event",
            "event_description": "Check back in the middle of the month",
            "og_event_description": "Check back in the middle of the month",
        }
        events = []
    return render_template(
        "home.html",
        coming_event=coming_event,
        group_events=events,
    )

