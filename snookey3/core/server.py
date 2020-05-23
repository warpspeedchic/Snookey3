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
from threading import Thread

import psutil
import waitress

from snookey3 import config
from . import callbacks
from .exceptions import PortOccupiedException

logger = logging.getLogger(__name__)


def run():
    for connection in psutil.net_connections():
        if connection.laddr.port == 65010:
            process = psutil.Process(connection.pid)
            logger.warning('Port occupied, raising PortOccupiedException.')
            raise PortOccupiedException(process)

    thread = Thread(target=lambda: waitress.serve(callbacks.app,
                                                  host=config['SERVER']['HOST'],
                                                  port=config['SERVER']['PORT'],
                                                  _quiet=True),
                    daemon=True)
    thread.start()
    logger.info('Started the server thread.')
