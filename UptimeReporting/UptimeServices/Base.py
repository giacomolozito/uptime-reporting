#!/usr/bin/env python
#
# Giacomo.Lozito@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from abc import ABC

class BaseUptimeService(ABC):

  def __init__(self, api_token, filter_opts):
    pass
  
  # the implementation of this function must return a data structure as follows
  # (to be later passed to check_get_all_summary_avg as parameter):
  # {
  #   "count": VALUE, # count of checks retrieved
  #   "_data": VALUE  # coult be a list or a dict; implementation is service-dependent; not used outside class
  # }
  def check_get_all(self):
    pass

  # the implementation of this function must return a data structure as follows:
  # {
  #   "_meta":{
  #     "service_name": "SERVICE_NAME",
  #     "from_ts":      VALUE,
  #     "to_ts":        VALUE
  #   },
  #   "_checks":[
  #     {
  #       "name":  "CHECK_NAME",
  #       "id":    CHECK_ID,
  #       "tags":[
  #          "ONETAG",
  #          "ANOTHERTAG",
  #          "MORETAGS"
  #       ],
  #       "uptime":{
  #         "totaldown":    VALUE,
  #         "totalunknown": VALUE,
  #         "totalup":      VALUE,
  #         "pct":          VALUE
  #       }
  #     },
  #     {
  #       ...
  #     }
  #   ]
  # }
  def check_get_all_summary_avg(self, checks, from_ts, to_ts, report_progress_func=None):
    pass
