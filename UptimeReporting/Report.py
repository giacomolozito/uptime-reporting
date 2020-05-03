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
import os
from tabulate import tabulate
import jinja2
from datetime import datetime


class Report:

  def __init__(self, checks_data, checks_date_range, report_type, thresholds, jinja_template='default', jinja_flags=[], text_use_colors=False):
    self.render = self.render_jinja if report_type == 'jinja' else self.render_text
    self.jinja_template = jinja_template
    self.jinja_flags = jinja_flags
    self.thresholds = dict(zip(['w','c'],[float(x) for x in thresholds.split(',')]))
    self.checks_data = checks_data
    self.checks_date_range = checks_date_range
    self.text_use_colors = text_use_colors

  def render_text(self):
    # a terminal-friendly report leveraging tabulate module for pretty-printing
    headers=['Check Name','Uptime %', 'Downtime']
    def render_text_iter(checks_data, label=[], minsize=80):
      # print aggregated stats for this level
      report = ''
      group_name = ' + '.join(label).upper() if label else 'ALL CHECKS'
      stats_row = [self.__color_text([f'AVERAGE UPTIME {group_name}', round(checks_data['_stats']['gs_pct_avg'],4), ''], checks_data['_stats']['gs_pct_avg'])]
      # print checks uptime results for this level
      checks_rows = [self.__color_text([row['name'], round(row['uptime']['pct'],4), self.__seconds_to_dhms(row['uptime']['totaldown'])], row['uptime']['pct'])
        for row in checks_data['_checks']]
      sizing_row = [['-' * minsize, '', '']] # sizing row, used to equally-size all tables
      # put together and print
      report += ('|  ' * len(label)) + '\n'
      report += ('|  ' * len(label)) + f'\-- Uptime statistics {group_name}\n'
      for report_line in tabulate(stats_row + checks_rows + sizing_row, headers=headers, numalign='right').splitlines():
        report += ('|  ' * (len(label)+1)) + report_line + '\n'
      for tag in [tag for tag in checks_data.keys() if tag[0] != '_']:
        report += render_text_iter(checks_data[tag], label=(label + [tag]))
      return report
    report = render_text_iter(self.checks_data)
    return report

  def render_jinja(self):
    # if specified without path, pick template from the module templates dir; otherwise assume it's user-provided
    if os.path.basename(self.jinja_template) == self.jinja_template:
      logging.debug(f'Using template {self.jinja_template} from module templates dir')
      template_loader=jinja2.PackageLoader('UptimeReporting', 'Templates')
    else:
      logging.debug(f'Using template {self.jinja_template}, user-provided')
      template_searchpath = os.path.dirname(self.jinja_template)
      template_loader = jinja2.FileSystemLoader(searchpath=template_searchpath)
    template_env = jinja2.Environment(loader=template_loader)
    # custom filters:
    # - a timedelta filter to make duration in seconds more readable
    # - a filter to return threshold status 0,1,2 (ok, warning, critical) based on % value vs thresholds
    template_env.filters['seconds_to_dhms'] = self.__seconds_to_dhms
    template_env.filters['threshold_status'] = self.__threshold_status
    # render
    template = template_env.get_template(os.path.basename(self.jinja_template))
    report = template.render(
      checks_data=self.checks_data, checks_thresholds=self.thresholds,
      checks_date_range=self.checks_date_range, flags=self.jinja_flags, now=datetime.now()
    )
    return report

  # utility function to color text based on thresholds - used in the text report if colors are enabled
  def __color_text(self, strings, value):
    if self.text_use_colors and value > -1:
      color = ['\033[0;32m', '\033[0;33m', '\033[0;31m', '\033[0;37m'][self.__threshold_status(value)]
      return [f'{color}{string}\033[0;37m' for string in strings]
    return strings # no color

  # utility function to return uptime check status against threshold; 0 = ok, 1 = warning, 2 = critical, 3 = na
  def __threshold_status(self, uptime_pct):
    if uptime_pct < 0:
      return 3
    elif uptime_pct > self.thresholds['w']:
      return 0
    elif uptime_pct <= self.thresholds['w'] and uptime_pct > self.thresholds['c']:
      return 1
    else:
      return 2

  # utility function to convert seconds in a human-readable "?d ?h ?m ?s" string (days, hours, minutes, seconds)
  def __seconds_to_dhms(self, seconds):
    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    locals_ = locals()
    dhms = ' '.join(["{n}{mag}".format(n=int(locals_[mag]), mag=mag) for mag in ['d','h','m','s'] if locals_[mag]])
    return dhms
