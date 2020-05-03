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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime, date, timedelta
import calendar
import logging
import re

# validate and get range information
def get_date_range(p_report_type, p_date):
  date_range = {}
  logging.debug(f'Date parameter: {p_date}')
  # range report
  if p_report_type == 'range':
    date_range_m = re.match(r'([0-9]{4}-[0-9]{2}-[0-9]{2})_([0-9]{4}-[0-9]{2}-[0-9]{2})$', p_date)
    if not date_range_m:
      raise Exception('ERROR: date is not in YYYY-MM-DD_YYYY-MM-DD format')
    logging.debug(f'Report type {p_report_type}, analysing range {p_date}')
    date_range = {
      'start': datetime.strptime(date_range_m.group(1), '%Y-%m-%d'),
      'end': datetime.strptime(date_range_m.group(2), '%Y-%m-%d')
    }
    if date_range['start'] >= date_range['end']:
      raise Exception('ERROR: in date range, start date should be older than end date')
  # weekly report
  if p_report_type == 'weekly':
    date_range_m = re.match(r'([0-9]{4}-[0-9]{2}-[0-9]{2})$|(last)$', p_date)
    if not date_range_m:
      raise Exception('ERROR: date is not in YYYY-MM-DD format or \'last\'')
    if p_date == 'last':
      ref_date = datetime.today() + timedelta(weeks=-1)
    else:
      ref_date = datetime.strptime(p_date, '%Y-%m-%d')
    logging.debug(f'Report type {p_report_type}, identifying weekly date range around {ref_date}')
    start_date = ref_date + timedelta(-ref_date.weekday())
    end_date = start_date + timedelta(days=6)
    date_range = { 'start': start_date, 'end': end_date }
  # monthly report
  if p_report_type == 'monthly':
    date_range_m = re.match(r'([0-9]{4}-[0-9]{2}-[0-9]{2})$|(last)$', p_date)
    if not date_range_m:
      raise Exception('ERROR: date is not in YYYY-MM-DD format or \'last\'')
    if p_date == 'last':
      ref_date = datetime.today().replace(day=1) + timedelta(days=-1)
    else:
      ref_date = datetime.strptime(p_date, '%Y-%m-%d')
    logging.debug(f'Report type {p_report_type}, identifying monthly date range around {ref_date}')
    month_c = calendar.monthrange(ref_date.year, ref_date.month)
    start_date = ref_date.replace(day=1)
    end_date = ref_date.replace(day=month_c[1])
    date_range = { 'start': start_date, 'end': end_date }
  # for all report types, ensure that start date has time 00:00
  # and end date has time 23:59:59 and also store a timestamp version
  date_range['start']= date_range['start'].replace(hour=0,minute=0,second=0,microsecond=0)
  date_range['end']= date_range['end'].replace(hour=23,minute=59,second=59,microsecond=0)
  date_range['start_ts'] = int(date_range['start'].timestamp())
  date_range['end_ts'] = int(date_range['end'].timestamp())
  return date_range
