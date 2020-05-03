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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging


# aggregate statistics, to produce more complete reports;
# -1 values (i.e. checks fully paused for measured interval) are excluded
# no return value, the dict is transformed inline
def add_aggregated_stats(checks_data):
  # for each level process tags first, and _checks at that level last
  for check_index in sorted(checks_data.keys(),reverse=True):
    if check_index[0] != '_':
      add_aggregated_stats(checks_data[check_index])
    elif check_index == '_checks':
      checks_data['_stats'] = { 'g_checks_count': 0, 'g_pct_avg': 0, 'gs_checks_count': 0, 'gs_pct_avg': 0 }
      checks_data['_stats']['g_checks_count'] = len([check for check in checks_data[check_index] if check['uptime']['pct'] > -1])
      checks_data['_stats']['g_pct_avg'] = sum(
        [check['uptime']['pct'] for check in checks_data[check_index] if check['uptime']['pct'] > -1 ]
        ) / checks_data['_stats']['g_checks_count'] if checks_data['_stats']['g_checks_count'] != 0 else -1
      checks_data['_stats']['gs_checks_count'] = sum(
        [checks_data[tag]['_stats']['gs_checks_count'] for tag in sorted(checks_data.keys(),reverse=True) if tag[0] != '_']
        ) + checks_data['_stats']['g_checks_count']
      # for the group + subgroup percentage uptime, use a weighted average
      count_and_pct_for_subs = [[checks_data[tag]['_stats']['gs_pct_avg'], checks_data[tag]['_stats']['gs_checks_count']]
        for tag in sorted(checks_data.keys(),reverse=True) if tag[0] != '_']
      count_and_pct_for_subs.append([checks_data['_stats']['g_pct_avg'], checks_data['_stats']['g_checks_count']])
      checks_data['_stats']['gs_pct_avg'] = weighted_avg(count_and_pct_for_subs)
	

# utility function to calculate weighted average
# input is [[val1, w1], [val2, w2], ...]
def weighted_avg(val_and_w):
  # calculate sum of weights
  wsum = sum([w for val,w in val_and_w])
  # apply each weight as decimal percentage to each value and sum them
  wavg = sum([(val * (w/wsum)) for val,w in val_and_w]) if wsum != 0 else -1
  return wavg
