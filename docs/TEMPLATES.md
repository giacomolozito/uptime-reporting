## uptime-reporting - writing templates

Report templates are written using the [Jinja2](https://jinja.palletsprojects.com/en/2.11.x/) template format.

* [ Overview ](#overview)
* [ Variables available to the template ](#variables-available-to-the-template)
* [ Custom jinja filters ](#custom-jinja-filters)

## Overview

The template to use can be specified with `--report-jinja-template` ; if a path is specified, the jinja template filename is taken from the specified path which can be anywhere on filesystem. If the path is not specified, then the template is taken from the UptimeReports python package of the tool. See [UptimeReporting/Templates](../UptimeReporting/Templates) for the list of predefined templates and the [Parameters](PARAMETERS.md) doc section for more details around the jinja template parameters.

In order to fill in data, the template can use the documented variables and some custom jinja filters. Jinja supports recursion (see [default.html](../UptimeReporting/Templates/default.html) template for an example) but recursion is not necessary if not using tag grouping or if generating a report for a fixed group of tags, so the combinations to process are predictable in the template.

Example from default.html, putting statistics in a table using a recursive macro:
```
<table class='check_table'>
<tbody>
<tr class='check_tableh'><th><div>Check Name</div></th><th><div>Uptime %</div></th><th><div>Downtime</div></th></tr>
{% macro table_populate(data, label=[]) -%}
  {% set group_name = ' + '.join(label) if label else 'ALL' %}
  <tr class='check_summary taglevel-{{ label|length }}'><td><div>average uptime {{ group_name }}</div></td>
  <td><div class='tr_{{ data._stats.gs_pct_avg|threshold_status }}'>{{ data._stats.gs_pct_avg|round(4) }}</div></td><td><div>&nbsp;</div></td>
  {% for check in data._checks %}
    <tr class='check_row taglevel-{{ label|length }}'><td><div>{{ check.name }}</div></td>
    <td><div class='tr_{{ check.uptime.pct|threshold_status }}'>{{ check.uptime.pct|round(4) }}</div></td><td><div>{{ check.uptime.totaldown|seconds_to_dhms }}&nbsp;</div></td></tr>
  {% endfor %}
  {% for tag in data.keys() %}
    {% if tag[0] != '_' %}
      {{ table_populate(data[tag], label=(label + [tag])) }}
    {% endif %}
  {% endfor %}
{%- endmacro %}
{{ table_populate(checks_data) }}
</tbody>
</table>
```

## Variables available to the template

* [ checks\_data ](#checks_data)
* [ checks\_thresholds ](#checks_thresholds)
* [ checks\_date\_range ](#checks_date_range)
* [ flags ](#flags)
* [ now ](#now)

#### checks\_data
Stores the uptime data collected by the tool. Uses the following structure format:
```
{
  '_meta': {     # overall info about the data
    'service_name': SERVICE_NAME,  # uptime service used to collect data
    'from_ts':      VALUE,         # uptime range of interest, begin timestamp
    'to_ts':        VALUE          # uptime range of interest, end timestamp
  },
  '_checks': [ ... ],  # a group of checks
  '_stats':  { ... },  # aggregated stats for the group of checks

  # if tag grouping is enabled, then the data structure recursively expands
  # to cover all combinations; in example for TAG-1,TAG-2|TAG-A,TAG-B:

  'TAG-1': {
    '_checks': [ ... ],  # a group of checks with TAG-1
    '_stats':  { ... },  # aggregated stats for the group of checks with TAG-1
    'TAG-A': {
      '_checks': [ ... ],  # a group of checks with TAG-1 and TAG-A
      '_stats':  { ... },  # aggregated stats for the group of checks with TAG-1 and TAG-A
    },
    'TAG-B': {
      '_checks': [ ... ],  # a group of checks with TAG-1 and TAG-B
      '_stats':  { ... },  # aggregated stats for the group of checks with TAG-1 and TAG-B
    }
  },
  'TAG-2': {
    '_checks': [ ... ],  # a group of checks with TAG-2
    '_stats':  { ... },  # aggregated stats for the group of checks with TAG-2
    'TAG-A': {
      '_checks': [ ... ],  # a group of checks with TAG-2 and TAG-A
      '_stats':  { ... },  # aggregated stats for the group of checks with TAG-2 and TAG-A
    },
    'TAG-B': {
      '_checks': [ ... ],  # a group of checks with TAG-2 and TAG-B
      '_stats':  { ... },  # aggregated stats for the group of checks with TAG-2 and TAG-B
    }
  }

}
```

The  `_checks` and `_stats` keys store check information and aggregated statistics for each group. When using tag grouping, this provides aggregated statistics per-tag and each group also contains keys (gs\_\*) that aggregate the statistics for the group and all children groups.
```
{
  '_checks': [   # a group of checks
    {
      'name': CHECK_NAME,
      'id':   CHECK_ID,
      'tags': [
        TAG1,
        TAG2,
        ...
      ],
      'uptime': {
        'totaldown':     VALUE, # values are in seconds
        'totalunknown':  VALUE,
        'totalup':       VALUE,
        'pct':           VALUE  # percentage of uptime on total time
      }
    },
    {
      ... # and so on for the other checks
    }
  ],
  '_stats': { # aggregated statistics
  {
    'g_checks_count':   VALUE, # count of aggregated checks in this group (see tag grouping)
    'g_pct_avg':        VALUE, # average of uptime for checks in this group
    'gs_checks_count':  VALUE, # count of aggregated checks in this group and all children groups
    'gs_pct_avg':       VALUE  # average of uptime for checks in this group and all children groups
  }
}
```

### checks\_thresholds

Stores the threshold information passed through the `--report-thresholds` parameter.
```
{'w': 99.95, 'c': 99.0}
```

### checks\_date\_range

Stores the date range information for the report. Provides the information in both datetime objects and unix TS format.
```
{'start': datetime.datetime(2020, 4, 1, 0, 0), 'end': datetime.datetime(2020, 4, 30, 23, 59, 59), 'start_ts': 1585695600, 'end_ts': 1588287599}
```

### flags

Stores any arbitrary flag passed through the `--report-jinja-flags` parameter.
```
# example value for --report-jinja-flags foo,bar
['foo', 'bar']
```

### now

Stores the time of report generation (from `datetime.now()`).

## Custom jinja filters

The templates can also use some convenience filters provided by the application.

| Filter name | Description |
| --- | --- |
| `seconds_to_dhms` | Filter that converts a numerical value from seconds to days, hours, minutes, seconds for improved human readability |
| `threshold_status` | Filter to be used with the uptime percentage values; returns 0 if the uptime % is above warning threshold, 1 if uptime % is below warning threshold but above critical threshold, 2 if uptime % is below critical threshold and 3 if uptime % is unknown |

