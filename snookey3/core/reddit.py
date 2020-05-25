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
from .exceptions import UnsuccessfulRequestException


def get_headers() -> dict:
    headers = {'User-agent': config['USER_AGENT']}

    token = os.getenv('REDDIT_ACCESS_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token

    return headers


def get_me() -> dict:
    headers = get_headers()
    response = requests.get('http://oauth.reddit.com/api/v1/me', headers=headers)
    try:
        response_json = response.json()
    except ValueError:
        raise UnsuccessfulRequestException(response.status_code, response.content)
    return response_json


def get_video_json(stream_id: str = None) -> dict:
    if stream_id is None:
        stream_id = os.getenv('RPAN_STREAM_ID')
    headers = get_headers()
    response = requests.get(f'https://strapi.reddit.com/videos/{stream_id}', headers=headers)
    try:
        video_json = response.json()['data']
    except (KeyError, ValueError):
        raise UnsuccessfulRequestException(response.status_code, response.content)

    return video_json


def get_authorization_url() -> str:
    state = callbacks.create_state()
    params = {'client_id': config['REDDIT']['CLIENT_ID'],
              'response_type': 'code',
              'state': state,
              'redirect_uri': config['REDDIT']['REDIRECT_URI'],
              'scope': '*'}
    url = 'https://www.reddit.com/api/v1/authorize?' + urllib.parse.urlencode(params)
    return url


def post_broadcast(title: str, subreddit: str):
    headers = get_headers()
    title = urllib.parse.quote(title)
    url = f'https://strapi.reddit.com/r/{subreddit}/broadcasts?title={title}'
    response = requests.post(url, data={}, headers=headers)

    try:
        data = response.json()['data']
        streamer_key = data['streamer_key']
        stream_url = data['post']['url']
        stream_id = data['post']['id']
    except (KeyError, ValueError):
        raise UnsuccessfulRequestException(response.status_code, response.content)
    else:
        os.environ['RPAN_STREAMER_KEY'] = streamer_key
        os.environ['RPAN_STREAM_URL'] = stream_url
        os.environ['RPAN_STREAM_ID'] = stream_id
