from flask import Flask, render_template, request, Response
import requests

import os
from dotenv import load_dotenv
import base64
import hashlib

from Loop import Loop

# Set up global variables ########################

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = "http://localhost:3000"
SCOPE = 'user-modify-playback-state user-read-private'

LOOP = Loop()

##################################################
app = Flask(__name__)

@app.route("/", methods=["GET"])
async def index():
    return render_template("index.html")

@app.route('/run_login', methods=['GET'])
async def login():
    def generate_random_string(length):
        possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        values = os.urandom(length)
        return ''.join(possible[x % len(possible)] for x in values)

    async def sha256(plain):
        data = plain.encode('utf-8')
        hashed = hashlib.sha256(data).digest()
        return hashed

    def base64encode(input_bytes):
        encoded = base64.b64encode(input_bytes)
        return encoded.decode('utf-8').replace('=', '').replace('+', '-').replace('/', '_')

    code_verifier = generate_random_string(64)
    hashed = await sha256(code_verifier)
    code_challenge = base64encode(hashed)

    auth_url = "https://accounts.spotify.com/authorize"

    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'scope': SCOPE,
        'code_challenge_method': 'S256',
        'code_challenge': code_challenge,
        'redirect_uri': REDIRECT_URI,
    }

    auth_url += '?' + '&'.join(f'{key}={value}' for key, value in params.items())
    get_request = [auth_url, code_verifier]
    print(get_request)
    return get_request

@app.route("/run_get_token", methods=["GET"])
async def get_token():
    code = request.cookies.get("code")
    code_verifier = request.cookies.get("code_verifier")
    refresh_token = request.cookies.get("refresh_token")
    if (code == None or code_verifier == None):
        if (refresh_token == None):
            return Response(status=400)
        payload = {
            'client_id' : CLIENT_ID,
            'grant_type' : 'refresh_token',
            'refresh_token' : refresh_token
        }
    else:
        payload = {
            'client_id': CLIENT_ID,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'code_verifier': code_verifier,
        }
    request_url = "https://accounts.spotify.com/api/token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.post(request_url, data=payload, headers=headers)
    response_json = response.json()

    access_token = response_json.get('access_token')
    refresh_token = response_json.get('refresh_token')

    get_request = [access_token, refresh_token]
    return get_request

@app.route("/run_get_user", methods=["GET"])
async def get_user():
    access_token = request.cookies.get("access_token")
    request_url = "https://api.spotify.com/v1/me/"
    headers = {
        'Authorization':'Bearer ' + access_token
    }
    response = requests.get(request_url, headers=headers)
    response_json = response.json()

    display_name = response_json.get('display_name')

    return Response(display_name, 200)


@app.route("/start_loop", methods=["POST"])
async def start_loop():
    if (request.cookies.get("access_token") == None):
        return Response("You're not logged in.", status=400)
    if (request.form.get("start") == '' or request.form.get("end") == ''):
        return Response("Invalid input.", status=400)
    LOOP.set_start(int(request.form.get("start")))
    LOOP.set_end(int(request.form.get("end")))
    if (LOOP.duration < 3):
        return Response("The loop is too short, make it at least 3 seconds long.", status=400)
    if (LOOP.loop == None):
        LOOP.access_token = request.cookies.get("access_token")
        LOOP.start_loop()
    return Response(status=200)

@app.route("/stop_loop", methods=["PUT"])
async def stop_loop():
    if (LOOP.loop != None):
        LOOP.stop_loop()
    return Response(status=200)

if __name__ == '__main__':
      app.run(host='localhost', port=3000, debug=True)