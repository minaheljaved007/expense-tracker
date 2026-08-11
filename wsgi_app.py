"""
wsgi_app.py
-----------
Deployment adapter for PythonAnywhere.

CONTEXT:
NiceGUI is built on FastAPI, which is an ASGI app (async). PythonAnywhere's
standard web app hosting (including the free tier) serves WSGI apps
(synchronous, Flask/Django-style). These are different protocols -- you
can't hand `ui.run()`'s server directly to PythonAnywhere's WSGI slot.

This file bridges the two using `a2wsgi`, which wraps an ASGI app so a
WSGI server can call it. This is the standard workaround for deploying a
NiceGUI / FastAPI app on PythonAnywhere's free or lower-tier plans,
which don't support running your own long-lived ASGI process.

LIMITATIONS OF THIS BRIDGED MODE (fine for this project, worth knowing):
  - No NiceGUI `reload=True` dev auto-reload (that's a local-dev-only feature
    anyway, not something you'd want in production).
  - Realtime websocket-driven UI updates and NiceGUI's own connection
    handling can be less snappy through a WSGI bridge than through a native
    ASGI server, because the bridge translates each request individually.
    For a form-and-list app like this one (no `ui.timer` polling loops,
    no live push updates from a background job), you won't notice this.
  - If you later add background timers or push notifications, that's a
    signal to move to PythonAnywhere's "Always-on task" feature instead
    (requires a paid Hacker plan or higher), running `main.py` directly
    as a native process instead of through this bridge.

On PythonAnywhere, your Web tab's WSGI configuration file should import
`application` from this module. See the deployment guide for exact steps.
"""

import sys
import os

# Make sure this project's folder is on the import path, since
# PythonAnywhere's working directory when loading the WSGI file may not
# be this folder.
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from fastapi import FastAPI
from nicegui import ui
from a2wsgi import ASGIMiddleware

import main  # noqa: F401  (imported for its side effect: registers the @ui.page("/") route on `ui`)

# Build a real FastAPI app and mount NiceGUI's routes (including the
# "/" page defined in main.py) onto it.
fastapi_app = FastAPI()
ui.run_with(fastapi_app, storage_secret="change-this-to-a-random-secret-string")

# a2wsgi wraps the ASGI app so a WSGI server (like PythonAnywhere's) can
# call it. PythonAnywhere's WSGI config file looks for a variable named
# `application` by convention -- that's why it's named this exact way.
application = ASGIMiddleware(fastapi_app)
