#  Snookey3 - Unofficial streaming utility for the Reddit Public Access Network
#  Copyright (C) 2020 warpspeedchic <https://github.com/warpspeedchic/>
#
#  Snookey3 is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Snookey3 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Snookey3.  If not, see <https://www.gnu.org/licenses/>.

import logging
from uuid import uuid4

from flask import Flask, request, abort

from snookey3.version import __title__
from .reddit import r
from .exceptions import UnsuccessfulRequestException

logger = logging.getLogger(__name__)

app = Flask(__title__)


@app.route('/callback')
def callback():
    error = request.args.get('error', '')
    if error:
        logger.error(error)
    state = request.args.get('state', '')
    if not is_valid_state(state):
        logger.warning('Received invalid state: %s', state)
        abort(403)

    code = request.args.get('code')

    try:
        r.auth.authorize(code)
    except UnsuccessfulRequestException as e:
        logger.error('Token not found. Status code: %i. Response: %s', e.status_code, e.response_content)
        message = "Couldn't obtain a token."
    else:
        logger.info('Token obtained.')
        message = 'Token obtained. You may now close this page.'

    return f"""
    <head>
    <title>{__title__}</title>
        <style>
            * {{ 
            background: #181818; 
            color: #ffffff; 
            font-family: sans-serif; 
            font-size: 18px; 
            text-align: center;
            padding-top: 25vh;
            }}
        </style>
    </head>
    <body>{__title__.replace("3", "<span style='color: #488cfa'>3</span>")} - {message}</body>"""


valid_states = []


def is_valid_state(state: str) -> bool:
    if state in valid_states:
        return True
    return False


def create_state() -> str:
    state = str(uuid4())
    valid_states.append(state)
    return state
