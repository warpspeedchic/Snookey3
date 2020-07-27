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
import webbrowser

import pyperclip
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, pyqtSlot
from PyQt5.QtWidgets import QWidget, QGridLayout, QStackedWidget, QPushButton, QLineEdit, QComboBox, QMessageBox, \
    QLabel

from snookey3 import config
from snookey3.core import callbacks
from snookey3.core.reddit import r, Broadcast
from snookey3.core.exceptions import UnsuccessfulRequestException
from snookey3.gui.chat import ChatWidget
from snookey3.gui.widgets import TitleWidget, FooterWidget, LabeledLineEdit

logger = logging.getLogger(__name__)


class BroadcastReadyWidget(QWidget):

    new_broadcast = pyqtSignal()

    def __init__(self, broadcast: Broadcast):
        super(BroadcastReadyWidget, self).__init__()

        self.broadcast = broadcast

        self.streamer_key = self.broadcast.streamer_key
        self.stream_url = self.broadcast.stream_url

        self.streamer_key_line = LabeledLineEdit('Broadcast key', self.streamer_key)
        self.streamer_key_line.line_edit.setPlaceholderText('Streamer key')
        self.streamer_key_line.line_edit.setReadOnly(True)
        self.streamer_key_line.line_edit.setEchoMode(QLineEdit.Password)

        self.copy_streamer_key_button = QPushButton('Copy')
        self.copy_streamer_key_button.clicked.connect(lambda: pyperclip.copy(self.streamer_key))

        self.rtmp_address_line = LabeledLineEdit('Server address', 'rtmp://ingest.redd.it/inbound/')
        self.rtmp_address_line.line_edit.setPlaceholderText('RTMP address')
        self.rtmp_address_line.line_edit.setReadOnly(True)

        self.copy_rtmp_address_button = QPushButton('Copy')
        self.copy_rtmp_address_button.clicked.connect(lambda: pyperclip.copy(self.rtmp_address_line.line_edit.text()))

        self.open_browser_button = QPushButton('Open in browser')
        self.open_browser_button.clicked.connect(lambda: webbrowser.open(self.stream_url))

        self.copy_stream_url_button = QPushButton('Copy URL')
        self.copy_stream_url_button.clicked.connect(lambda: pyperclip.copy(self.stream_url))

        self.instructions = 'Copy and paste the Server address and Broadcast key\n' \
                            'to your broadcasting software.'
        self.instructions_label = QLabel(self.instructions)
        self.instructions_label.setAlignment(Qt.AlignCenter)

        self.open_chat_window_button = QPushButton('Open chat window')
        try:
            self.chat = ChatWidget(self.broadcast)
        except (KeyError, UnsuccessfulRequestException):
            self.open_chat_window_button.setEnabled(False)
        else:
            self.open_chat_window_button.clicked.connect(self.chat.show)

        self.new_broadcast_button = QPushButton('New broadcast')
        self.new_broadcast_button.clicked.connect(self.new_broadcast.emit)

        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.streamer_key_line, 0, 0, Qt.AlignVCenter)
        self.main_layout.addWidget(self.copy_streamer_key_button, 0, 1, Qt.AlignVCenter)
        self.main_layout.addWidget(self.rtmp_address_line, 1, 0, Qt.AlignVCenter)
        self.main_layout.addWidget(self.copy_rtmp_address_button, 1, 1, Qt.AlignVCenter)
        self.main_layout.addWidget(self.instructions_label, 2, 0, 1, 2, Qt.AlignVCenter)
        self.main_layout.addWidget(self.open_browser_button, 3, 0, Qt.AlignBottom)
        self.main_layout.addWidget(self.copy_stream_url_button, 3, 1, Qt.AlignBottom)
        self.main_layout.addWidget(self.open_chat_window_button, 4, 0, 1, 2, Qt.AlignTop)
        self.main_layout.addWidget(self.new_broadcast_button, 5, 0, 1, 2, Qt.AlignVCenter)

        self.setLayout(self.main_layout)


class BroadcastSetupWidget(QWidget):

    broadcast_created = pyqtSignal(Broadcast)

    def __init__(self):
        super(BroadcastSetupWidget, self).__init__()

        self.username = r.username()

        self.username_line = QLineEdit(self.username)
        self.username_line.setPlaceholderText('u/username')
        self.username_line.setReadOnly(True)

        self.broadcast_title_line = QLineEdit()
        self.broadcast_title_line.setPlaceholderText('Broadcast title...')

        self.subreddit_combo = QComboBox()
        self.subreddit_combo.addItems(config['SUBREDDITS'])

        self.create_broadcast_button = QPushButton('Create broadcast')
        self.create_broadcast_button.clicked.connect(self.create_broadcast)

        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.username_line, 0, 0)
        self.main_layout.addWidget(self.broadcast_title_line, 1, 0)
        self.main_layout.addWidget(self.subreddit_combo, 2, 0)
        self.main_layout.addWidget(self.create_broadcast_button, 3, 0)

        self.setLayout(self.main_layout)

    def create_broadcast(self):
        title = self.broadcast_title_line.text().strip()

        if len(title) == 0:
            QMessageBox.information(self, 'Title too short', 'Your title needs to be longer.')
            return

        subreddit = self.subreddit_combo.currentText()

        try:
            broadcast = r.broadcast.post(title, subreddit)
        except UnsuccessfulRequestException as e:
            message = f'Broadcast creation failed. Status code: {e.status_code}'
            status_message = json.loads(e.response_content).get('status_message')
            if not status_message:
                status_message = json.loads(e.response_content).get('status')
            if status_message:
                message += '\n' + status_message
            logger.warning(message, e.response_content)
            QMessageBox.warning(self, 'Broadcast creation unsuccessful', message)
        else:
            self.broadcast_created.emit(broadcast)


class AuthorizationWidget(QWidget):

    authorized = pyqtSignal()

    def __init__(self):
        super(AuthorizationWidget, self).__init__()

        self.message = "This app needs access to your Reddit account\nin order to create a broadcast.\n"

        self.some_text = QLabel(self.message)
        self.some_text.setEnabled(False)
        self.some_text.setAlignment(Qt.AlignCenter)

        self.authorize_button = QPushButton('Authorize through Reddit')
        self.authorize_button.clicked.connect(self.authorize)

        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.some_text, 0, 0, Qt.AlignBottom)
        self.main_layout.addWidget(self.authorize_button, 1, 0, Qt.AlignTop)

        self.setLayout(self.main_layout)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.look_for_token)

    def authorize(self):
        webbrowser.open(r.auth.url(callbacks.create_state()))
        self.timer.start()

    def look_for_token(self):
        if r.auth.access_token:
            self.authorized.emit()
            self.timer.stop()
            return


class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.title_widget = TitleWidget()

        authorization_widget = AuthorizationWidget()
        authorization_widget.authorized.connect(self.on_authorized)

        self.main_stacked = QStackedWidget()
        self.main_stacked.setFixedSize(400, 260)
        self.main_stacked.addWidget(authorization_widget)

        self.footer_widget = FooterWidget()

        self.main_layout = QGridLayout()
        self.main_layout.setContentsMargins(24, 12, 24, 12)
        self.main_layout.addWidget(self.title_widget, 0, 0, Qt.AlignTop)
        self.main_layout.addWidget(self.main_stacked, 1, 0, Qt.AlignCenter)
        self.main_layout.addWidget(self.footer_widget, 2, 0, Qt.AlignBottom)

        self.setLayout(self.main_layout)
        self.resize(480, 320)

    def mousePressEvent(self, a0) -> None:
        self.setFocus()

    @pyqtSlot()
    def on_authorized(self):
        broadcast_setup_widget = BroadcastSetupWidget()
        broadcast_setup_widget.broadcast_created.connect(self.on_broadcast_created)
        self.switch_to_widget(broadcast_setup_widget)

    @pyqtSlot(Broadcast)
    def on_broadcast_created(self, broadcast: Broadcast):
        broadcast_ready_widget = BroadcastReadyWidget(broadcast)
        broadcast_ready_widget.new_broadcast.connect(self.on_authorized)
        self.switch_to_widget(broadcast_ready_widget)

    def switch_to_widget(self, widget: QWidget):
        focus_widget = self.main_stacked.focusWidget()
        self.main_stacked.setCurrentIndex(self.main_stacked.addWidget(widget))
        self.main_stacked.removeWidget(focus_widget)
        focus_widget.deleteLater()
