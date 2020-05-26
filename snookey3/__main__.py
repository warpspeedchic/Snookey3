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

import sys


def main():
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from snookey3.core import server
    from snookey3.utils import files
    from snookey3.version import __title__
    from snookey3.core.exceptions import PortOccupiedException
    from snookey3.gui import fonts
    from snookey3.gui.main import MainWindow

    qapp = QApplication([])

    qapp.setApplicationName(__title__)
    qapp.setWindowIcon(QIcon(files.get_path('resources', 'img', 'Icon.ico')))
    qapp.setStyle('fusion')
    qapp.setFont(fonts.default)

    with open(files.get_path('resources', 'styles', 'default.qss')) as stylesheet_file:
        qapp.setStyleSheet(stylesheet_file.read())
    fonts.load()
    try:
        server.run()
    except PortOccupiedException as e:
        QMessageBox.warning(None, 'Port occupied',
                            "This app requires a specific local port to be open\n"
                            f"but it seems to be occupied by {e.process.name()}.\n"
                            f"If it's safe to do so, close {e.process.name()} and try again.")
        sys.exit(-1)

    main_window = MainWindow()
    main_window.show()
    sys.exit(qapp.exec())


if __name__ == '__main__':
    main()
