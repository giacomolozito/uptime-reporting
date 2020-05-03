#!/usr/bin/env python
#
# a simple class to abtract the Python 3.1 API
# https://docs.pingdom.com/api/
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


class Pingdom(BaseUptimeService):

  SERVICE_NAME='pingdom'
  PINGDOM_API_URL='https://api.pingdom.com/api/3.1'

  def __init__(self, api_token, filter_opts):
    self.api_token = api_token
    self.req_headers = {'Authorization': f'Bearer {api_token}'}
    self.filter_opts = filter_opts
    # try to open a connection to confirm correct token
    logging.debug('Attempt a checks API request to Pingdom to confirm token validity')
    self.__req_get('/checks?limit=1')

  def check_get_all(self):
    # we always want to retrieve the tags information in our request
    req_parameters = 'include_tags=true'
    # tags_include filter can be used here to optimize initial results, but only if our special 'none' tag is not present
    if self.filter_opts['tags_include'] and 'none' not in self.filter_opts['tags_include']:
      req_parameters += '&tags=' + ','.join(self.filter_opts['tags_include'])
    # make request
    req = self.__req_get(f'/checks?{req_parameters}')
    res = json.loads(req.text)
    # return structure
    checks = { 'count': len(res['checks']), '_data': res }
    return checks

  def check_get_all_summary_avg(self, checks, from_ts, to_ts, report_progress_func=None):
    checks_uptime = { '_meta': { 'service_name': self.SERVICE_NAME, 'from_ts': from_ts, 'to_ts': to_ts }, '_checks': [] }
    pr_total, pr_counter, pr_thr = checks['count'], 0, 10 # report every 10% increase
    for check in checks['_data']['checks']:
      pr_counter += 1
      check_tags = [tag['name'] for tag in check['tags']]
      logging.debug(check)
      # check filter options
      if self.__is_check_filtered(check, check_tags):
        logging.debug('Check {} skipped based on include/exclude filters'.format(check['id']))
        continue # skip check
      # process check
      summary = self.__check_get_summary_avg(check['id'], from_ts, to_ts)
      logging.debug(summary)
      status = summary['summary']['status']
      # additional info: calculate the percentage of uptime
      try:
        status['pct'] = status['totalup'] / (status['totalup'] + status['totaldown']) * 100
      except ZeroDivisionError:
        status['pct'] = -1 # check does not have up or down time, it must be all unknown
      # for each check, store uptime and tags
      checks_uptime['_checks'].append({
        'name': check['name'], 'id': check['id'],
        'tags': check_tags,
        'uptime': status
      })
      pr = round((pr_counter / pr_total * 100), 2)
      if report_progress_func and pr > pr_thr:
        pr_thr += 10
        report_progress_func(pr)
    return checks_uptime

  def __check_get_summary_avg(self, check_id, from_ts, to_ts):
    req = self.__req_get(f'/summary.average/{check_id}?from={from_ts}&to={to_ts}&includeuptime=true')
    return json.loads(req.text)

  # utility method to handle requests, will raise exception if request fails
  def __req_get(self, url):
    req = requests.get(self.PINGDOM_API_URL+url, headers=self.req_headers)
    req.raise_for_status()
    return req

  # utility method to process check/tag filters; returns true if check must be filtered
  def __is_check_filtered(self, check, check_tags):
    # check filter options
    if self.filter_opts['checks_exclude_paused'] and check['status'] == 'paused':
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
 
