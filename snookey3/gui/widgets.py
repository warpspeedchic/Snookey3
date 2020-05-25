#  Snookey3 - Unofficial streaming utility for the Reddit Public Access Network
#  Copyright (C) 2020 warpspeedchic <https://github.com/warpspeedchic/>QLabel
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

import webbrowser

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QAbstractButton, QLineEdit, QVBoxLayout

from snookey3.gui import fonts
from snookey3.utils import files
from snookey3.version import __title__, __copyright__, __url__, __version__


class PicButton(QAbstractButton):
    def __init__(self, pixmap):
        super(PicButton, self).__init__()
        self.pixmap = pixmap
        self.setFixedSize(QSize(self.pixmap.size()))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()


class LabeledLineEdit(QWidget):

    def __init__(self, label_text: str, line_edit_text: str):
        super(LabeledLineEdit, self).__init__()

        self.label = QLabel(label_text)
        self.label.setFont(fonts.default_bold)
        self.line_edit = QLineEdit(line_edit_text)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.label, Qt.AlignBottom)
        self.main_layout.addWidget(self.line_edit, Qt.AlignTop)

        self.setLayout(self.main_layout)


class TitleWidget(QWidget):

    def __init__(self):
        super(TitleWidget, self).__init__()

        self.title_label = QLabel(__title__.replace('3', '<span style="color:#488cfa">3</span>'))
        self.title_label.setFont(fonts.title)

        self.github_mark = QPixmap(files.get_path('resources', 'img', 'Github-Mark-Light-32px.png'))
        self.github_button = PicButton(self.github_mark)
        self.github_button.clicked.connect(self.open_github)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.title_label, alignment=Qt.AlignVCenter | Qt.AlignLeft)
        self.main_layout.addWidget(self.github_button, alignment=Qt.AlignVCenter | Qt.AlignRight)

        self.setLayout(self.main_layout)

    @staticmethod
    def open_github():
        webbrowser.open(__url__)


class FooterWidget(QWidget):

    def __init__(self):
        super(FooterWidget, self).__init__()

        self.version_label = QLabel(f'{__title__} - v{__version__}')
        self.version_label.setFont(fonts.small)
        self.version_label.setAlignment(Qt.AlignHCenter)

        self.copyright_label = QLabel(__copyright__)
        self.copyright_label.setFont(fonts.small)
        self.copyright_label.setAlignment(Qt.AlignHCenter)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.version_label)
        self.main_layout.addWidget(self.copyright_label)

        self.setLayout(self.main_layout)
