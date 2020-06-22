#!/usr/bin/env python
#
# This uses https://uptimerobot.com/api (v2)
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

import requests
import json
import logging
from .Base import BaseUptimeService


class UptimeRobot(BaseUptimeService):

  SERVICE_NAME='uptimerobot'
  API_URL='https://api.uptimerobot.com/v2'

  def __init__(self, api_token, filter_opts):
    self.api_token = api_token
    self.req_headers = {
      'content-type': 'application/x-www-form-urlencoded',
      'cache-control': 'no-cache'
    }
    self.api_key = f'api_key={api_token}'
    self.filter_opts = filter_opts
    # try to open a connection to confirm correct api key
    logging.debug('Attempt a getMonitors request to UptimeRobot to confirm API key validity')
    res = self.__req('getMonitors', {'limit':1})
    if res['stat'] != 'ok':
      raise Exception(f'getMonitors request failed - {res}')

  def check_get_all(self):
    # for uptimerobot, do the actual data requests in check_get_all_summary_avg
    # so at this time we only provide back the total check count, optimised on checks_include if present
    req_params = { 'limit':1 }
    # put checks_include filter directly in the request if we have any
    if self.filter_opts['checks_include']:
      req_params['monitors'] = '-'.join(self.filter_opts['checks_include'])
    res = self.__req('getMonitors', req_params)
    checks = { 'count': res['pagination']['total'], '_data': None }
    return checks

  def check_get_all_summary_avg(self, checks, from_ts, to_ts, report_progress_func=None):
    checks_uptime = { '_meta': { 'service_name': self.SERVICE_NAME, 'from_ts': from_ts, 'to_ts': to_ts }, '_checks': [] }
    pr_total, pr_counter, pr_thr = checks['count'], 0, 10 # report every 10% increase
    # iterate through paginated requests to get the information (max = 50)
    checks_offset = 0
    checks_page = 50
    while (checks_offset < checks['count']):
      req_params = { 'limit':checks_page, 'offset':checks_offset, 'custom_uptime_ranges':f'{from_ts}_{to_ts}' }
      # put checks_include filter directly in the request if we have any
      if self.filter_opts['checks_include']:
        req_params['monitors'] = '-'.join(self.filter_opts['checks_include'])
      # make request
      res = self.__req('getMonitors', req_params)
      for check in res['monitors']:
        pr_counter += 1
        # uptimerobot does not have tags at time of writing,
        # we emulate them by reading any text after a pipe as tag |tag1,tag2,...
        if '|' in check['friendly_name']:
          pos = check['friendly_name'].index('|')
          check_tags = check['friendly_name'][pos+1:].split(',')
          check_name = check['friendly_name'][:pos].strip()
        else:
          check_tags = []
          check_name = check['friendly_name']
        logging.debug(check)
        # check filter options
        if self.__is_check_filtered(check, check_tags):
          logging.debug('Check {} skipped based on include/exclude filters'.format(check['id']))
          continue # skip check
        elif check['create_datetime'] > to_ts:
          logging.debug('Check {} skipped due to having been created after time range of interest'.format(check['id']))
          continue # skip check
        # process check
        uptime = {}
        uptime['pct'] = float(check['custom_uptime_ranges'])
        # up/down time based on time range
        # something like all_time_uptime_durations would be handy, but it does not work with ranges
        # so we go with second best, and calculate up/down based on pct; pause time is ignored
        time_interval = to_ts - from_ts
        uptime['totalup'] = int(time_interval * uptime['pct'] / 100)
        uptime['totaldown'] = time_interval - uptime['totalup']
        uptime['totalunknown'] = 0
        checks_uptime['_checks'].append({
          'name': check_name, 'id': check['id'],
          'tags': check_tags, 'uptime': uptime
        })
        pr = round((pr_counter / pr_total * 100), 2)
        if report_progress_func and pr > pr_thr:
          pr_thr += 10
          report_progress_func(pr)
      checks_offset += checks_page
    return checks_uptime

  # utility method to handle requests, will raise exception if request fails
  def __req(self, path, post_dict):
    post_data = '&'.join([self.api_key, 'format=json'] + [f'{k}={v}' for k,v in post_dict.items()])
    req = requests.post(f'{self.API_URL}/{path}', data=post_data, headers=self.req_headers)
    req.raise_for_status()
    res = json.loads(req.text)
    # UptimeRobot API returns 200 even on API failure (i.e. wrong api key) so check the stat code on response
    if res['stat'] != 'ok':
      raise Exception(f'{path} request failed - {res}')
    return res

  # utility method to process check/tag filters; returns true if check must be filtered
  def __is_check_filtered(self, check, check_tags):
    # check filter options
    if self.filter_opts['checks_exclude_paused'] and check['status'] == 0:
      return True # skip paused checks
    if self.filter_opts['checks_include'] and str(check['id']) not in self.filter_opts['checks_include']:
      return True # skip check not in include list
    if self.filter_opts['checks_exclude'] and str(check['id']) in self.filter_opts['checks_exclude']:
      return True # skip check in exclude list
    # tag filters options
    if self.filter_opts['tags_include']:
      if not any(tag in check_tags for tag in self.filter_opts['tags_include']):
        if 'none' not in self.filter_opts['tags_include']:
          return True # skip checks with tags not in include list
        elif check_tags:
          return True # skip checks which have tags, but none specified in the include list ('none' case)
    if self.filter_opts['tags_exclude']:
      if any(tag in check_tags for tag in self.filter_opts['tags_exclude']):
        return True # skip tags in exclude list
      elif 'none' in self.filter_opts['tags_exclude'] and not check_tags:
        return True # skip checks without tags, as 'none' is in exclude list
    # no filter applies to this check
    return False
 
