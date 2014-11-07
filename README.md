# yos from your doorbell wassup

## installation

    git clone git@github.com:pokemoncards/doorbellyo.git
    cd doorbellyo
    mkvirtualenv doorbellyo
    pip install -r requirements.txt
    echo 'YO_API_TOKEN = "THEAPIKEYFROMTHATEMAIL"' > config.py

install ngrok to receive requests from the outside world.

    brew install ngrok

or

    sudo apt-get install ngrok

## usage
start the service:

    python app.py

in another tab:

    ngrok 5000

## api
### /
the home screen with a form to subscribe to a doorbell

### /count/doorbell
a subscriber count for `doorbell`

### /yo/username
send a yo to `username`

### /yoall
send a yo to all of doorbellyo's subscribers
