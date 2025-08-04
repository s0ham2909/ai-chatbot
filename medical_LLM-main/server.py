# server.py

import os
import json
from flask import Flask, render_template, session, redirect, url_for
from dotenv import load_dotenv, find_dotenv
from authlib.integrations.flask_client import OAuth
from urllib.parse import urlencode, quote_plus

# Load environment variables (.env)
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY")

# --- Auth0 Configuration ---
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=os.environ.get("AUTH0_CLIENT_ID"),
    client_secret=os.environ.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{os.environ.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

@app.route("/")
def home():
    user_info = session.get("user")
    return render_template("home.html", session=user_info, pretty=json.dumps(user_info, indent=4) if user_info else None)

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback")
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token['userinfo']
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + os.environ.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": os.environ.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

if __name__ == "__main__":
    print("🚀 Flask server running at http://localhost:3000")
    app.run(host="0.0.0.0", port=3000, debug=True)
