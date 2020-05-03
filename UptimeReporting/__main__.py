#!/usr/bin/env python
#
# uptime-reporting: a tool to report on service availability statistics
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

import sys, os, re
import argparse
import logging
from datetime import datetime
import UptimeReporting.UptimeService
import UptimeReporting.TagsGrouping
import UptimeReporting.DateRange
import UptimeReporting.Report
import UptimeReporting.Aggreg


def main():

  # validation functions
  def arg_vld_report_thresholds(s):
    if not re.match('^\d+\.?\d*,\d+\.?\d*$',s):
      raise argparse.ArgumentTypeError('Wrong format for report threshold parameter')
    return s
  def arg_vld_date(s):
    if not re.match('(^last$)|(^[0-9]{4}-[0-9]{2}-[0-9]{2}$)|(^[0-9]{4}-[0-9]{2}-[0-9]{2})_([0-9]{4}-[0-9]{2}-[0-9]{2}$)',s):
      raise argparse.ArgumentTypeError('Wrong format for date parameter; use "last" or YYYY-MM-DD or YYYY-MM-DD_YYYY-MM-DD depending on report type')
    return s
  def arg_vld_list_str(s):
    return s.split(',') if s else []

  # get supported uptime services
  supported_services = UptimeReporting.UptimeService.getSupportedServices()
  # parse input arguments
  args_required = ('--version' not in sys.argv)
  parser_example_text = '''example:\n\n  uptime-reporting.py -t API_TOKEN --report weekly --date last\n '''
  parser = argparse.ArgumentParser(description='Report statistics on uptime checks', epilog=parser_example_text, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('--service', help='Uptime Service for data collection; supported services: {}'.format(','.join(supported_services)), dest='service', action='store', choices=supported_services, required=args_required)
  parser.add_argument('--token', help='Uptime Service API token for authentication', dest='api_token', action='store', required=args_required)
  parser.add_argument('--date', help='Date in YYYY-MM-DD (used to identify month or week for weekly/monthly report type); use "last" as convenient way to get report for last week or last month; if using range report type, then use format "YYYY-MM-DD_YYYY-MM-DD")', action='store', dest='date', required=args_required, type=arg_vld_date)
  parser.add_argument('--report-type', help='Report type', action='store', dest='report_type', required=args_required, choices=['weekly','monthly','range'])
  parser.add_argument('--report-format', help='Report format (default: text); text is a terminal-friendly report, jinja uses templates to produce custom format reports', action='store', dest='report_format', choices=['text','jinja'], default='text')
  parser.add_argument('--report-thresholds', help='Set thresholds for warning and critical uptime status (default "99.95,99.00"). These are typically used to color-code uptime stats in the reports.', action='store', dest='report_thresholds', default='99.95,99.00', type=arg_vld_report_thresholds)
  parser.add_argument('--report-text-colors', help='Shows threshold colors in terminal-friendly text report', action='store_true', dest='report_text_colors', default=False)
  parser.add_argument('--report-jinja-template', help='Report jinja template for custom format (default: default.html). If a path is not specified, uses the templates available under templates/ module dir.', action='store', dest='report_jinja_template', default='default.html')
  parser.add_argument('--report-jinja-flags', help='A comma-separated list of flags that can be used within the jinja template to customize generation of the report', action='store', type=arg_vld_list_str, dest='report_jinja_flags', default=None)
  parser.add_argument('--report-filename', help='If specified, save report to file instead of printing on screen', action='store', dest='report_filename', default=None)
  parser.add_argument('--tags-grouping', help='If specified, groups checks and aggregates statistics based on tags; different hierarchy levels can be specified; see documentation for details', action='store', dest='tags_grouping', default=None)
  parser.add_argument('--tags-exclude', help='A comma-separated list of tags; checks associated with these tags will be excluded from the report. Use "none" to exclude checks without any tag.', action='store', type=arg_vld_list_str, dest='tags_exclude', default=None)
  parser.add_argument('--tags-include', help='A comma-separated list of tags; if specified, only checks associated with at least one of these tags will be included in the report. Use "none" to include checks without any tag.', action='store', type=arg_vld_list_str, dest='tags_include', default=None)
  parser.add_argument('--checks-exclude', help='A comma-separated list of checks Id, to be excluded from the report.', action='store', type=arg_vld_list_str, dest='checks_exclude', default=None)
  parser.add_argument('--checks-exclude-paused', help='Skip paused check in the report', action='store_true', dest='checks_exclude_paused', default=False)
  parser.add_argument('--checks-include', help='A comma-separated list of checks Id; if specified, only these checks will be included in the report.', action='store', type=arg_vld_list_str, dest='checks_include', default=None)
  parser.add_argument('--verbosity', help='Verbosity of output: 0 = quiet, 1 = standard (default), 2 = debug', action='store', dest='verbosity', choices=['0','1','2'], default=1)
  parser.add_argument('--version', help='Display version and exit', action='store_true', dest='version')
  args = parser.parse_args()

  if args.version:
    print(UptimeReporting.__version__)
    sys.exit(0)

  # logging
  root = logging.getLogger()
  root.setLevel(logging.DEBUG if args.verbosity == '2' else logging.INFO if args.verbosity == '1' else logging.ERROR)
  printver = print if args.verbosity != '0' else lambda *a, **k: None

  # validate and further parse date input
  printver(f'Report type: {args.report_type}')
  date_range = UptimeReporting.DateRange.get_date_range(args.report_type, args.date)
  printver('Date range: {} - {}'.format(date_range['start'],date_range['end']))

  # get all the checks, along with tags
  service_filter_options = {
    'checks_exclude_paused': args.checks_exclude_paused,
    'checks_include': args.checks_include, 'checks_exclude': args.checks_exclude,
    'tags_include': args.tags_include, 'tags_exclude': args.tags_exclude
  }
  service = UptimeReporting.UptimeService.getService(service_name=args.service, api_token=args.api_token, filter_opts=service_filter_options)
  logging.debug('Test connection to uptime service successful, retrieving all checks')
  checks = service.check_get_all()

  # for each check, retrieve the uptime stats for the desired range
  printver('Found {} checks to evaluate, gathering uptime stats for each'.format(checks['count']))
  def print_progress(progress): # utility function for progress report
    if args.verbosity != '0':
      sys.stdout.write("Progress: {}%   \r".format(progress))
      sys.stdout.flush()
  checks_uptime = service.check_get_all_summary_avg(checks, date_range['start_ts'], date_range['end_ts'], print_progress)

  # if tag grouping is enabled, build a data structure based on tag hierarchy
  if args.tags_grouping:
    printver('Grouping checks based on tag hierarchy: {}'.format(args.tags_grouping))
    checks_uptime = UptimeReporting.TagsGrouping.get_uptime_tags_groups(checks_uptime, args.tags_grouping)

  # add aggregated statistics
  printver('Aggregating check uptime statistics')
  UptimeReporting.Aggreg.add_aggregated_stats(checks_uptime)

  # report results
  printver('Writing report')
  report = UptimeReporting.Report.Report(
    checks_uptime, checks_date_range=date_range, report_type=args.report_format, thresholds=args.report_thresholds,
    jinja_template=args.report_jinja_template, jinja_flags=args.report_jinja_flags, text_use_colors=args.report_text_colors
  )
  rendered_report = report.render()
  if args.report_filename:
    with open(args.report_filename, 'w') as f:
      f.write(rendered_report)
    printver(f'Report written to {args.report_filename}')
  else:
    print(rendered_report)


if __name__=="__main__":
  main()
