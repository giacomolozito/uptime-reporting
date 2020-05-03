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


# if tags grouping is enabled, build structures based on tag hierarchy
# each level of hierarchy is separated by pipe and defined as a list of tags for example
# cats,dogs|apples,pears,trees|...
# this results in checks being classified based on the tags they have:
# --cats
#    \--apples
#    \--pears
#    \--trees
# --dogs
#    \--apples
#    \--pears
#    \--trees
# each tag has a "_checks" key containing a list of corresponding checks

import logging

def get_uptime_tags_groups(checks_uptime, tag_grouping):

  checks_uptime_tg = {'_meta': checks_uptime['_meta'], '_checks':[]}
  tags = [tag_group.split(',') for tag_group in tag_grouping.split('|')]
  logging.debug('Tag grouping enabled with hierarchy: {}'.format(tags))

  # a recursive function to populate the tag structure
  def place_in_tag_hierarchy(check_dict, check, tags, tag_level):
    added = False
    for tag in tags[tag_level]:
      # initialize tag space in the structure if not done
      if tag not in check_dict:
        check_dict[tag] = {'_checks':[]}
      # does the check have this tag?
      if tag in check['tags']:
        # found, check deeper level
        if tag_level+1 >= len(tags) or not place_in_tag_hierarchy(check_dict[tag], check, tags, tag_level+1):
          # if not found at deeper level, add at this level
          check_dict[tag]['_checks'].append(check)
        added = True # either at deeper level or at this one, this is now added
    # if at level 0 and not found anywhere, add at outer level
    if tag_level == 0 and not added:
      check_dict['_checks'].append(check)
      added = True
    return added

  # populate tag structure
  for check in checks_uptime['_checks']:
    place_in_tag_hierarchy(checks_uptime_tg, check, tags, 0)

  return checks_uptime_tg
