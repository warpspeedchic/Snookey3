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

from PyQt5.QtGui import QFont, QFontDatabase

from snookey3.utils.files import get_path


def load():
    QFontDatabase.addApplicationFont(get_path('resources', 'fonts', 'Oswald-Medium.ttf'))


default = QFont('Arial', 10)
default.setStyleStrategy(QFont.PreferAntialias)
default_bold = QFont('Arial', 10, QFont.Bold)
default_bold.setStyleStrategy(QFont.PreferAntialias)
small = QFont('Arial', 8)
small.setStyleStrategy(QFont.PreferAntialias)
title = QFont('Oswald', 26, QFont.Medium)
title.setStyleStrategy(QFont.PreferAntialias)
