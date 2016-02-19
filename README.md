# github-web-hook-flask-restful
Flask-based webhook using flask-restful api to run a script in response to a GitHub webhook call.

This service does not "do" anything but call an external script. If you don't like this technique, fork it and have at it.

Before setting this up, have a quick skim of the GitHub [Webhooks](https://developer.github.com/webhooks/) Developer Documentation, so you can see what is expected.

## A Word of Warning
Know what you are doing when creating your payload script. Your payload script can do just about anything you give it permission to do. If you are going to use it to automate deployment of a website with git (which is what I originally wrote it for), then make sure you have thoroughly tested your script, have it's permissions strictly limited, and make sure it throws useful errors. A script run with too many privileges will rebel, raining woe and a stink of failure onto your house. Your future self will thank you.

## Key Creation
You'll need to generate a "Secret" key for github's webhooks to use when generating a signature. I just use an RFC 4122 v4 key, you may have a better idea.

```python
>>> import uuid
>>> str(uuid.uuid4())
'27a05652-aacc-44f9-a941-592f64872c10'
>>>
```

## Hook Listener Configuration

Copy config.py.example to config.py. Change following as you see fit.

### X_HUB_SIGNATURE
The "X_HUB_SIGNATURE" value in config.py must match the key  you created above. Neglecting this will end in bitter recriminations.

```python
X_HUB_SIGNATURE="27a05652-aacc-44f9-a941-592f64872c10"

```

### LOGDIR
By default, the script creates a "logs" directory in it's own runtime directory and writes logs there. This is probably not what you want. If you have a better place for the log (and you do, don't you? You RASCAL!), simply uncomment the first declaration of LOGDIR and replace the string with your path.

```python
LOGDIR = "/var/log/webhooks"
```

### PAYLOAD_SCRIPT
Finally, add in your own payload script.
```bash
PAYLOAD_SCRIPT = "/path/to/payload-script.py"
```

## Suggestions for Web Service Configuration
You may be tempted to just create a little script to run API/WebHook, using Flask's built-in wsgi server. That would be kind of lazy, and frankly, I'm ashamed of you for suggesting it.

The instructions below should work on any system running systemd and nginx. 

### systemd

/etc/systemd/system/webhook.service

Example assumes github-web-hook-flask-restful installed in foobar's home directory, logfiles in default spot and virtualenv installed.

```ini
[Unit]
Description=My Hook
After=network.target

[Service]
User=foobar
Group=www-data
WorkingDirectory=/home/foobar/github-web-hook-flask-restful
Environment="PATH=/home/foobar/github-web-hook-flask-restful/venv/bin"
ExecStart=/home/foobar/github-web-hook-flask-restful/venv/bin/gunicorn --workers 1 --bind unix:hook.sock -m 007 wsgi

[Install]
WantedBy=multi-user.target
```

After you have tested this with the rest, don't forget to run 
```bash
sudo systemctl enable webhook.service
```

### nginx
Example nginx config file with ssl. Note that I have pointed the logs for this server to the webhook logs directory. I find it convenient, but you probably don't want to do that unless you obsessively delete your logs, or have configured [logrotate](http://linux.die.net/man/8/logrotate) to look for the logs there.

And I'm just saying: I sure do like [letsencrypt](https://letsencrypt.org/howitworks/technology/).

```nginx
server {
        listen 40443 ssl;
        server_name foo.bar;
        add_header Strict-Transport-Security "max-age=31536000";
        ssl on;
        ssl_certificate /etc/letsencrypt/live/foo.bar/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/foo.bar/privkey.pem;
        access_log /home/foobar/github-web-hook-flask-restful/logs/access.log;
        error_log /home/foobar/github-web-hook-flask-restful/logs/error.log;
        location / {
                include proxy_params;
                proxy_pass http://unix:/home/foobar/github-web-hook-flask-restful/hook.sock;
                }
}
```

## Smoke Test

After you get your service all set up and running you can try this curl command to simulate a call from github.  Expect it to fail with a bad signature.
```bash
curl -i -A "GitHub-Hookshot/044aadd" -H "Content-Type: application/json" -H "X-Hub-Signature: testing123"  -H "Accept: application/json" -X POST -d '{"action": "opened", "issue": {"url": "https://api.github.com/repos/octocat/Hello-World/issues/1347", "number": 1347}, "sender": {"login": "octocat", "id": 1}, "repository": {"owner": {"login": "octocat", "id": 1}, "id": 1296269, "full_name": "octocat/Hello-World"}}' http://foo.bar:40443
```

## Testing Your Payload Script
There are two bash scripts in "tests". Point your payload script at one of them, and:

1. create a throwaway repo on github
1. add a single file to the repo and commit it.
1. create your webhook on github, making sure to specify the url properly, the content as "application/json" and the correct key, matching the one you created in config.py
1. make an edit and push your changes to github.
1. check your logfile

"fail.bash" should return an error.

"succeed.bash" should return 200.

Now go run something useful!
