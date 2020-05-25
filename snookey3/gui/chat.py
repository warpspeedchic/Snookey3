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

import json
import logging

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QUrl
from PyQt5.QtWebSockets import QWebSocket
from PyQt5.QtWidgets import QWidget, QGridLayout, QTextEdit, QMessageBox

from snookey3.core import reddit

from snookey3.core.exceptions import UnsuccessfulRequestException

logger = logging.getLogger(__name__)


class Chat(QObject):

    comment_received = pyqtSignal(dict)

    def __init__(self):
        super(Chat, self).__init__()
        self.websocket = QWebSocket()
        self.websocket.textMessageReceived.connect(self.on_text_message_received)

    def connect(self):
        try:
            live_comments_websocket = reddit.get_video_json()['post']['liveCommentsWebsocket']
        except UnsuccessfulRequestException as e:
            logger.error('Could not fetch the video json. Status code: %i. Response: %s', 
                         e.status_code, e.response_content)
            raise
        except KeyError:
            logger.exception('Could not fetch the chat websocket address.')
            raise
            
        self.websocket.open(QUrl(live_comments_websocket))

    @pyqtSlot(str)
    def on_text_message_received(self, response):
        comment = json.loads(response)
        if comment['type'] != 'new_comment':
            return
        self.comment_received.emit(comment)


class ChatWidget(QWidget):

    def __init__(self):
        super(ChatWidget, self).__init__()
        self.setWindowTitle('Chat')
        self.chat = Chat()
        self.chat.comment_received.connect(self.on_comment_received)
        try:
            self.chat.connect()
        except (KeyError, UnsuccessfulRequestException):
            raise

        self.message_area = QTextEdit()
        self.message_area.setReadOnly(True)

        self.layout = QGridLayout()
        self.layout.addWidget(self.message_area)
        self.setLayout(self.layout)

    @pyqtSlot(dict)
    def on_comment_received(self, comment):
        payload = comment['payload']
        author = payload['author']
        body = payload['body']
        self.message_area.appendHtml(f'<b>{author}</b>: {body}')
