#!/usr/bin/env python3

from mailjet_rest import Client
import time, datetime
import requests
import json

def get_config(filename='config.json'):
    with open(filename) as f:
        config = json.load(f)
    config['headers'] = {
        'Authorization': config['token']
    }
    return config


def build_mail(config, tasks):
    return {
        "From": {
            "Email": "robin9975@gmail.com",
            "Name": "Robin Developer"
        },
        "To": [{
            "Email": "robin9975@gmail.com",
            "Name": "Robin Developer"
        }],
        "Subject": "{} tasks completed last week!".format(len(tasks)),
        "TextPart": "You completed the following tasks last week: {}".format(
            "\n".join([t['name'] for t in tasks])
        ),
        "HTMLPart": """
            <h2>Awesome!</h2>
            
            <p>
            You completed the following tasks last week:

            <ul>
                <li>
            {}  
            </li></ul>
            </p>
        """.format(
            "</li><li>".join([t['name'] for t in tasks])
        )
    }


def exec_mail(config, tasks):
    mailjet = Client(auth=(config['mailjet']['api_key'], config['mailjet']['api_secret']), version='v3.1')
    mail = build_mail(config, tasks)
    result = mailjet.send.create(data={'Messages': [mail]})
    print("Sending mail: {}".format(mail))
    print(result.json())


base_url = "https://api.clickup.com/api/v1"

def get_team(config):
    res = requests.get(
        "{}/team".format(base_url),
        headers=config['headers']
    ).json()
    return res['teams']

def get_tasks(config, team_id):
    today = datetime.date.today()
    last_monday = today - datetime.timedelta(days=-today.weekday(), weeks=1)
    gt_timestamp = int(time.mktime(last_monday.timetuple())) * 1000
    res = requests.get(
        "{}/team/{}/task?include_closed=true&statuses[]=closed&date_updated_gt={}".format(
            base_url,
            team_id,
            gt_timestamp
        ),
        headers=config['headers']
    ).json()
    return [t for t in res['tasks'] if int(t['date_closed']) > gt_timestamp]


if __name__ == "__main__":
    print("Loading config..")
    c = get_config()
    team_ids = [t['id'] for t in get_team(c)]
    for t in team_ids:
        tasks = get_tasks(c, t)
        exec_mail(c, tasks)
