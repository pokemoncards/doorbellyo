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
your home screen with a subscriber count.

### /count
a subscriber count

### /yo/username
send a yo to `username`

### /yoall
send a yo to all your subscribers
