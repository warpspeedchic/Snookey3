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
import urllib.parse
from time import time

import requests
import requests.auth

from snookey3 import config
from .exceptions import UnsuccessfulRequestException

logger = logging.getLogger(__name__)


REFRESH_AFTER = 2700


class Reddit:

    def __init__(self, client_id: str, redirect_uri: str, user_agent: str):
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.user_agent = user_agent
        self.auth = Auth(self)
        self.broadcast = BroadcastManager(self)

    def headers(self):
        headers = {'User-agent': self.user_agent}

        if self.auth.access_token:
            headers['Authorization'] = 'Bearer ' + self.auth.access_token

        return headers

    def get(self, url: str, params: dict = None, data: dict = None) -> requests.models.Response:
        if self.auth.authorized_time and (time() - self.auth.authorized_time >= REFRESH_AFTER):
            self.auth.refresh()
            logger.info('Refreshing the token.')

        headers = self.headers()
        response = requests.get(url, params=params, headers=headers, data=data)

        return response

    def post(self, url: str, params: dict = None, data: dict = None) -> requests.models.Response:
        if self.auth.authorized_time and (time() - self.auth.authorized_time >= REFRESH_AFTER):
            self.auth.refresh()
            logger.info('Refreshing the token.')

        headers = self.headers()
        response = requests.post(url, params=params, headers=headers, data=data)

        return response

    def username(self):
        response = self.get('https://oauth.reddit.com/api/v1/me')

        try:
            username = response.json()['name']
        except (ValueError, KeyError):
            return None
        else:
            return username


class Auth:

    def __init__(self, reddit: Reddit):
        self.reddit = reddit
        self.access_token = None
        self.refresh_token = None
        self.authorized_time = None

    def url(self, state: str) -> str:
        params = {'client_id': self.reddit.client_id,
                  'response_type': 'code',
                  'state': state,
                  'redirect_uri': self.reddit.redirect_uri,
                  'scope': '*',
                  'duration': 'permanent'}
        url = 'https://www.reddit.com/api/v1/authorize?' + urllib.parse.urlencode(params)
        return url

    def authorize(self, code):
        auth = requests.auth.HTTPBasicAuth(self.reddit.client_id, '')
        data = {'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.reddit.redirect_uri}
        headers = {'User-agent': self.reddit.user_agent}
        response = requests.post('https://ssl.reddit.com/api/v1/access_token',
                                 auth=auth,
                                 data=data,
                                 headers=headers)

        try:
            self.access_token = response.json()['access_token']
            self.refresh_token = response.json()['refresh_token']
        except (KeyError, ValueError):
            raise UnsuccessfulRequestException(response.status_code, response.content)
        else:
            self.authorized_time = time()

    def refresh(self):
        if not self.refresh_token:
            return
        auth = requests.auth.HTTPBasicAuth(self.reddit.client_id, '')
        data = {'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token}
        headers = {'User-agent': self.reddit.user_agent}
        response = requests.post('https://ssl.reddit.com/api/v1/access_token',
                                 auth=auth,
                                 data=data,
                                 headers=headers)

        try:
            self.access_token = response.json()['access_token']
        except (KeyError, ValueError):
            raise UnsuccessfulRequestException(response.status_code, response.content)
        else:
            self.authorized_time = time()


class BroadcastManager:

    def __init__(self, reddit: Reddit):
        self.reddit = reddit

    def post(self, title: str, subreddit: str):
        title = urllib.parse.quote(title)
        url = f'https://strapi.reddit.com/r/{subreddit}/broadcasts?title={title}'
        response = self.reddit.post(url, data={})

        try:
            data = response.json()['data']
            streamer_key = data['streamer_key']
            stream_url = data['post']['url']
            stream_id = data['post']['id']
        except (KeyError, ValueError):
            raise UnsuccessfulRequestException(response.status_code, response.content)
        else:
            return Broadcast(self.reddit, stream_id, streamer_key, stream_url)


class Broadcast(object):

    def __init__(self, reddit: Reddit, stream_id: str, streamer_key: str, stream_url: str):
        self.reddit = reddit
        self.stream_id = stream_id
        self.streamer_key = streamer_key
        self.stream_url = stream_url

    def live_comments_websocket(self):
        response = self.reddit.get(f'https://strapi.reddit.com/videos/{self.stream_id}')
        try:
            live_comments_websocket = response.json()['data']['post']['liveCommentsWebsocket']
        except (KeyError, ValueError):
            raise UnsuccessfulRequestException(response.status_code, response.content)

        return live_comments_websocket

    def post_comment(self, text: str):
        params = {'api_type': 'json',
                  'text': text,
                  'thing_id': self.stream_id}
        url = 'https://oauth.reddit.com/api/comment/'
        response = self.reddit.post(url, params=params)
        if response.status_code != 200:
            print(response.url)
            raise UnsuccessfulRequestException(response.status_code, response.content)


r = Reddit(config['REDDIT']['CLIENT_ID'],
           config['REDDIT']['REDIRECT_URI'],
           config['USER_AGENT'])
