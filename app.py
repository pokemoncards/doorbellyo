#!/usr/bin/env python
"""doorbellyo is a yo service that notifies you when your doorbel rings."""

from flask import Flask, request, render_template
from elasticsearch import Elasticsearch, NotFoundError
import requests
import config

app = Flask(__name__)
YO_API_KEY = config.YO_API_TOKEN
es = Elasticsearch()

# Check if index exists:
if not es.indices.exists('doorbells'):
    es.indices.create('doorbells')

@app.route('/')
def index():
    """Render the index page."""
    return render_template('base.html')

@app.route('/count/')
@app.route('/count/<doorbell>')
def count(doorbell=None):
    """Count the subscribers to a provided doorbell, if no doorbell is suplied,
    count doorbellyo's subscribers"""
    # If no doorbell is provided, then check our subscribers.
    if not doorbell:
        get_count = requests.get("https://api.justyo.co/subscribers_count/",
                                 params={'api_token': YO_API_KEY})

        if 'result' in get_count.json() and type(get_count.json()['result']) is int:
            subscriber_count = str(get_count.json()['result'])
            return render_template('count.html', count=subscriber_count, doorbell='doorbellyo')
        else:
            return render_template('message.html', code=400), 400

    # If a doorbell name was provided, look it up in ES.
    try:
        doorbell = doorbell.upper()
        subscribers = es.get(index="doorbells", id=doorbell)['_source']['subscribers']
        return render_template('count.html', count=len(subscribers), doorbell=doorbell)

    except NotFoundError:
        print("CAUGHT THE ERROR")
        # The doorbell is not registered with doorbellyo
        return render_template('message.html', code="Sorry, can't do that :("), 400

@app.route('/yo/<username>')
def yo_route(username):
    """Route to yo any user."""
    username = username.upper()
    location = request.args.get('location')
    link = request.args.get('link')
    if yo(username, location, link) == 200:
        return render_template('message.html', code="sent a yo to {0}!".format(username))
    return render_template('message.html', code='got a dumb error :('), 400

def yo(username, location=None, link=None):
    """Yo any user."""
    username = username.upper()
    data = {'api_token': YO_API_KEY, 'username': username}
    if location:
        data['location'] = location

    if link:
        data['link'] = link

    yo_request = requests.post("https://api.justyo.co/yo/",
                               data=data)

    if 'result' in yo_request.json() and yo_request.json()['result'] == "OK":
        return 200
    return 400

@app.route('/yoall')
def yoall_route():
    """Route to yo all of doorbellyo's subscribers."""
    location = request.args.get('location')
    link = request.args.get('link')
    if yoall(location, link) == 200:
        return render_template('message.html', code='sent everyone a yo!')
    return render_template('message.html', code='blah blah got an error blah blah'), 400

def yoall(location=None, link=None):
    """Yo all of doorbellyo's subscribers."""
    data = {'api_token': YO_API_KEY}
    if location:
        data['location'] = location

    if link:
        data['link'] = link

    yoall_request = requests.post("https://api.justyo.co/yoall/",
                                  data=data)

    if yoall_request.text == "{}":
        return 200
    return 400

@app.route('/callback')
def callback():
    """Yo hits this route when doorbellyo is yo'd."""
    username = request.args.get('username', '').upper()
    yo(username, link="lsvx.com")
    return render_template('message.html', code="Got a Yo from {0}!".format(username))

@app.route('/signup', methods=['POST'])
def signup_route():
    username = request.form.get('username')
    doorbell = request.form.get('doorbell')

    if not username or not doorbell:
        return render_template('message.html', code='i think you messed up'), 400

    username = username.upper()
    doorbell = doorbell.upper()

    try:
        doorbell_document = es.get(index="doorbells", id=doorbell)['_source']
        if username in doorbell_document['subscribers']:
            return render_template('message.html', code='Already subscribed!'), 400

        doorbell_document['subscribers'].append(username)
        es.index(index="doorbells", id=doorbell, doc_type="doorbell", body=doorbell_document)
        return render_template('message.html', code="Thanks, {0}! You subscribed to {1}!".format(username, doorbell)), 200

    except NotFoundError:
        # The doorbell is not registered with doorbellyo
        return render_template('message.html', code="that doorbell doesn't exist :("), 400

@app.route('/ring', methods=['POST'])
def ring_route():
    """Route to ring a provided doorbell's subscribers."""
    doorbell = request.form['doorbell'].upper()

    if es.exists(index="doorbells", id=doorbell):
        ip_address = request.remote_addr
        if ip_address == "127.0.0.1":
            ip_address = requests.get('http://myexternalip.com/raw').headers['My-External-Ip']

        location_request = requests.get("http://freegeoip.net/json/{0}".format(ip_address))

        location = "{0},{1}".format(location_request.json()['latitude'], location_request.json()['longitude'])
        return ring(doorbell, location)

    es.index(index="doorbells", id=doorbell, doc_type="doorbell", body={"subscribers": []})
    return "Registered {0}!".format(doorbell)

def ring(doorbell, location):
    """Yo a provided doorbell's subscribers."""
    doorbell = doorbell.upper()
    subscribers = es.get(index="doorbells", id=doorbell)['_source']['subscribers']

    for username in subscribers:
        yo(username, location=location)

    return "Yo'd {0}".format(', '.join(subscribers))

@app.errorhandler(404)
@app.errorhandler(405)
def page_not_found(e):
    """Error page route."""
    return render_template('message.html', code=404), 404

if __name__ == "__main__":
    #app.debug = True
    app.run()

