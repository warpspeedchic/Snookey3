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
import sys
from datetime import date

import requests

from .utils import fjson
from .version import __version__, __title__

ROOT_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
HOME_DIR = os.path.expanduser('~')


def _init_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)
    logs_dir = os.path.join(HOME_DIR, '.Snookey3', 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    log_filename = str(date.today()) + '.log'
    f_handler = logging.FileHandler(os.path.join(logs_dir, log_filename))
    f_handler.setLevel(logging.DEBUG)

    c_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    f_formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

    c_handler.setFormatter(c_formatter)
    f_handler.setFormatter(f_formatter)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    def handle_exception(exctype, excvalue, exctraceback):
        if issubclass(exctype, KeyboardInterrupt):
            sys.__excepthook__(exctype, excvalue, exctraceback)
            return

        logger.critical('Uncaught exception', exc_info=(exctype, excvalue, exctraceback))

    sys.excepthook = handle_exception

    logger.info('Logger ready')

    return logger


def _pull_subreddits_from_github():
    try:
        response = requests.get('https://raw.githubusercontent.com/warpspeedchic/Snookey3/master/subreddits',
                                headers={'User-agent': config.get('USER_AGENT')})
    except:
        return None

    if response.status_code == 200:
        return [subreddit.strip() for subreddit in response.text.splitlines()]
    return None


_logger = _init_logger()

with open(os.path.join(ROOT_DIR, 'config.json')) as config_file:
    config = fjson.load(config_file, title=__title__, version=__version__)

if config['PULL_SUBREDDITS_FROM_GITHUB']:
    subreddits = _pull_subreddits_from_github()
    if subreddits:
        config['SUBREDDITS'] = subreddits
        _logger.info('Using online subreddit list.')
    else:
        _logger.info('Using local subreddit list.')
