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

import os
import urllib.parse

import requests

from snookey3 import config
from . import callbacks


def get_headers() -> dict:
    headers = {'User-agent': config['USER_AGENT']}

    token = os.getenv('REDDIT_ACCESS_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token

    return headers


def get_me() -> dict:
    headers = get_headers()
    response = requests.get('http://oauth.reddit.com/api/v1/me', headers=headers)
    response_json = response.json()
    return response_json


def get_authorization_url() -> str:
    state = callbacks.create_state()
    params = {'client_id': config['REDDIT']['CLIENT_ID'],
              'response_type': 'code',
              'state': state,
              'redirect_uri': config['REDDIT']['REDIRECT_URI'],
              'scope': '*'}
    url = 'https://www.reddit.com/api/v1/authorize?' + urllib.parse.urlencode(params)
    return url
