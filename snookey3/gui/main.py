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
import os
import webbrowser

from PyQt5.QtCore import Qt, pyqtSignal, QTimer, pyqtSlot
from PyQt5.QtWidgets import QWidget, QGridLayout, QStackedWidget, QPushButton, QLineEdit, QComboBox, QMessageBox, \
    QLabel

from snookey3 import config
from snookey3.core import reddit
from snookey3.core.exceptions import UnsuccessfulRequestException
from snookey3.gui.widgets import TitleWidget, FooterWidget, LabeledLineEdit

logger = logging.getLogger(__name__)


class BroadcastReadyWidget(QWidget):

    def __init__(self):
        super(BroadcastReadyWidget, self).__init__()

        self.streamer_key = os.getenv('RPAN_STREAMER_KEY')
        self.stream_url = os.getenv('RPAN_STREAM_URL')

        self.streamer_key_line = LabeledLineEdit('Broadcast key', self.streamer_key)
        self.streamer_key_line.line_edit.setPlaceholderText('Streamer key')
        self.streamer_key_line.line_edit.setReadOnly(True)

        self.copy_streamer_key_button = QPushButton('Copy')

        self.rtmp_address_line = LabeledLineEdit('Server address', 'rtmp://ingest.redd.it/inbound/')
        self.rtmp_address_line.line_edit.setPlaceholderText('RTMP address')
        self.rtmp_address_line.line_edit.setReadOnly(True)

        self.copy_rtmp_address_button = QPushButton('Copy')

        self.instructions = 'Copy and paste the Server address and Broadcast key\n' \
                            'to your broadcasting software.'
        self.instructions_label = QLabel(self.instructions)
        self.instructions_label.setAlignment(Qt.AlignCenter)

        self.open_control_panel_button = QPushButton('Open broadcast control panel')

        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.streamer_key_line, 0, 0, Qt.AlignVCenter)
        self.main_layout.addWidget(self.copy_streamer_key_button, 0, 1, Qt.AlignVCenter)
        self.main_layout.addWidget(self.rtmp_address_line, 1, 0, Qt.AlignVCenter)
        self.main_layout.addWidget(self.copy_rtmp_address_button, 1, 1, Qt.AlignVCenter)
        self.main_layout.addWidget(self.instructions_label, 2, 0, 1, 2, Qt.AlignVCenter)
        # self.main_layout.addWidget(self.open_control_panel_button, 3, 0, 1, 2, Qt.AlignVCenter)

        self.setLayout(self.main_layout)


class BroadcastSetupWidget(QWidget):

    broadcast_created = pyqtSignal()

    def __init__(self):
        super(BroadcastSetupWidget, self).__init__()

        self.username = reddit.get_me()['name']

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
            reddit.post_broadcast(title, subreddit)
        except UnsuccessfulRequestException as e:
            message = 'Broadcast creation failed.'
            if e.status_code == 503:
                message += f'\n{subreddit} is currently unavailable.'
            logger.warning(message + 'Status code: %i, full response: %s', e.status_code, e.response_content)
            QMessageBox.warning(self, 'Broadcast creation unsuccessful', message)
        else:
            self.broadcast_created.emit()


class AuthorizationWidget(QWidget):

    authorized = pyqtSignal()

    def __init__(self):
        super(AuthorizationWidget, self).__init__()

        self.message = "This app needs your authorization\nin order to create a broadcast.\n" \
                       "We promise not to do anything on your account\nwithout your explicit consent.\n" \
                       "We don't store any of your data."

        self.some_text = QLabel(self.message)
        self.some_text.setEnabled(False)
        self.some_text.setAlignment(Qt.AlignCenter)

        self.authorize_button = QPushButton('Authorize')
        self.authorize_button.clicked.connect(self.authorize)

        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.some_text, 0, 0, Qt.AlignBottom)
        self.main_layout.addWidget(self.authorize_button, 1, 0, Qt.AlignCenter)

        self.setLayout(self.main_layout)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.look_for_token)

    def authorize(self):
        webbrowser.open(reddit.get_authorization_url())
        self.timer.start()

    def look_for_token(self):
        if 'REDDIT_ACCESS_TOKEN' in os.environ:
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
        self.main_stacked.setFixedSize(400, 240)
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

    @pyqtSlot()
    def on_broadcast_created(self):
        self.switch_to_widget(BroadcastReadyWidget())

    def switch_to_widget(self, widget: QWidget):
        focus_widget = self.main_stacked.focusWidget()
        self.main_stacked.setCurrentIndex(self.main_stacked.addWidget(widget))
        self.main_stacked.removeWidget(focus_widget)
        focus_widget.deleteLater()