from flask import Flask, request
import requests
import config

app = Flask(__name__)
YO_API_KEY = config.YO_API_TOKEN

@app.route('/')
def index():
    count_number = count()
    return """smello, playa! looks like you have {0} subscribers<br/>
           <img src=\"http://media.giphy.com/media/YjFiZTA3MDEt/200.gif\"/>""".format(count_number)

@app.route('/count')
def count():
    get_count = requests.get("https://api.justyo.co/subscribers_count/",
                             params={'api_token': YO_API_KEY})

    if 'result' in get_count.json() and type(get_count.json()['result']) is int:
        return str(get_count.json()['result'])
    return ":P"

@app.route('/yo/<username>')
def yo(username):
    data = {'api_token': YO_API_KEY, 'username': username}
    link = request.args.get('link')
    if link:
        data['link'] = link

    yo_request = requests.post("https://api.justyo.co/yo/",
                                data=data)

    if 'result' in yo_request.json() and yo_request.json()['result'] == "OK":
        return "sent yo to {0}!".format(username)
    return "got a dumb error :("

@app.route('/yoall')
def yoall():
    data = {'api_token': YO_API_KEY}
    link = request.args.get('link')
    if link:
        data['link'] = link

    yoall_request = requests.post("https://api.justyo.co/yoall/",
                                data=data)

    if yoall_request.text == "{}":
        return "sent yo to everyone!"
    return "got a dumb error :("

@app.route('/callback')
def callback():
    username = request.args.get('username', '')
    print(username)
    return "got a yo from {0}".format(username)

if __name__ == "__main__":
    #app.debug = True
    app.run()

