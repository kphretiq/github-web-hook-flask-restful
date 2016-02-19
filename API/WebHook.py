import logging, logging.handlers
from hashlib import sha1
import hmac
from subprocess import Popen, PIPE
from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
app.config.from_object("config")
api = Api(app)

class WebHook(Resource):

    def get(self):
        return "nothing here"

    def post(self):
        # set to debug to avoid filling up logs if someone is playing
        # silly buggers
        if not all([
            "X-Hub-Signature" in request.headers,
            "GitHub-Hookshot" in str(request.user_agent)
            ]):
            app.config["LOGGER"].debug("Missing Sig or Hookshot")
            return "Missing Header Key", 422
        return True

        try:
            data = request.get_json()
        except Exception as error:
            app.config["LOGGER"].warning(error)
            return error.msg, 415

        try:
            # extract key from hex digest of payload
            sig = "sha1=%s"%hmac.new(
                    app.config["X_HUB_SIGNATURE"],
                    request.data,
                    sha1).hexdigest()

        except Exception as error:
            app.config["LOGGER"].warning(error)
            return error.msg, 400

        if not request.headers["X-Hub-Signature"] == sig:
            app.config["LOGGER"].debug(sig)
            app.config["LOGGER"].debug(request.headers["X-Hub-Signature"])
            app.config["LOGGER"].debug(app.config["X_HUB_SIGNATURE"])
            return "invalid key", 422 

        return True

        # run your PAYLOAD_SCRIPT
        out, err = Popen([
            app.config["PAYLOAD_SCRIPT"]
            ], stdout=PIPE, stderr=PIPE).communicate()

        out, err = out.strip(), err.strip()

        if err:
            app.app.config["LOGGER"].warning(err)
        if out:
            app.app.config["LOGGER"].debug(err)

        return str(out)

api.add_resource(WebHook, "/")
