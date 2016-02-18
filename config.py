import os
import logging, logging.handlers

_basedir = os.path.abspath(os.path.dirname(__file__))

# debug is on by default, you'll want to change this, lest your 
# logfiles grow like Vasty Moses.
DEBUG=True

#LOGDIR = "/path/to/logfile"
try:
    LOGDIR
except NameError:
    # if you are lazy, let config choose logging directory
    LOGDIR = os.path.join(_basedir, "logs")

if not os.path.exists(LOGDIR):
    os.mkdir(LOGDIR)

# create a nice, long random string for gitlab to use.
X_HUB_SIGNATURE = "changeme"

# full path to payload script. 
PAYLOAD_SCRIPT = os.path.join(_basedir, "fake-payload.bash")

# set up logging object
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.INFO

LOGGER = logging.getLogger("webhook")
LOGGER.setLevel(level)
handler = logging.handlers.RotatingFileHandler(
        os.path.join(LOGDIR, "webhook.log"),
        maxBytes=100000,
        backupCount=3,
        )
handler.setLevel(level)
handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(message)s"))
LOGGER.addHandler(handler)

del os
