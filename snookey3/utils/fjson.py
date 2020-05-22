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

"""
This module provides an f-string-like functionality for json.
"""

import json
import re


def load(filepath: str, **fvars: str) -> dict:
    with open(filepath) as file:
        dict_ = json.load(file)
    _format(dict_, dict(**fvars))
    return dict_


def _format(dict_, fvars: {str}):
    if len(fvars) == 0:
        return

    def explore(explored_object):
        if isinstance(explored_object, dict):
            items = explored_object.items()
        elif isinstance(explored_object, list):
            items = enumerate(explored_object)
        else:
            return

        for key, value in items:
            if not isinstance(value, str):
                if isinstance(value, (dict, list)):
                    explore(value)
                continue

            for fvar_key, fvar_value in fvars.items():
                value = re.sub('{' + fvar_key + '}', fvar_value, value)

            explored_object[key] = value

    explore(dict_)
