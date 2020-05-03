## uptime-reporting - parameters

uptime-reporting is entirely command-line driven and all parameters must be specified at command-line. This is mostly as the tool is intended to be primarily used via automated means, i.e. CI/CD tools.

1. [ Basics ](#basics)
2. [ Reporting ](#reporting)
3. [ Filters ](#filters)
4. [ Others ](#others)

<a name="basics"></a>
### Basics

The mandatory ones. Nothing can be done without these.

| Parameter | Mandatory | Default value | Parameter description |
| --- | --- | --- | --- |
| `--service SERVICE_NAME` | yes | n.a. | Used to indicate the uptime service for data collection; currently, only `pingdom` is supported |
| `--token API_TOKEN` | yes | n.a. | Used to pass the uptime service API bearer token for API authentication |
| `--report-type {monthly,weekly,range}` | yes | n.a. | The report type, from a date interval perspective. Monthly, Weekly or custom Range report. The type of report changes the expected input of the `--date` parameter |
| `--date DATE` | yes | n.a. | For Monthly and Weekly `--report-type`, this must be a date in ISO 8601 format (YYYY-MM-DD) that will be used to identify the month or week of interest; as a convenience, one can also specify "last" to get the last month or week report; for the Range `--report-type`, this must be a date range with an underscore as separator, in format YYYY-MM-DD\_YYYY-MM-DD |

<a name="reporting"></a>
### Reporting

The parameters allowing to customise the report output.

| Parameter | Mandatory | Default value | Parameter description |
| --- | --- | --- | --- |
| `--report-format {text,jinja}` | no | text | Specifies the report format. Text is a terminal-friendly report, Jinja uses jinja templates to produce custom reports in any format (i.e. HTML) |
| `--report-thresholds THRESHOLDS` | no | "99.95,99.00" | Two uptime percentages separated by a comma, the first indicating the warning threshold and the second the critical one. These can be used to color-code or represent differently alerts in the report templates. The jinja report also provides a custom filter `threshold_status` that can be used to verify each uptime percentage against the thresholds. |
| `--report-filename FILENAME` | no | none | When specified, the report (either text or jinja) will be written to the specified file instead of being printed on-screen. This can be especially desirable for jinja-based reports. |
| `--report-text-colors` | no | off | Only used with text `--report-format`. When specified, the text (terminal-friendly) report will use color codes to highlight uptime checks above/below thresholds |
| `--report-jinja-template TEMPLATE` | no | default.html | Only used with jinja `--report-format`. Specifies the jinja template to use for report generation. If a name is specified without a path, the template is taken from the tool package (see [UptimeReporting/Templates](../UptimeReporting/Templates) for the list of predefined templates). If the template is specified with a path, then it's taken from the specified filesystem location, so custom templates can be provided by the user. |
| `--report-jinja-flags FLAGS` | no | none | Only used with jinja `--report-format`. Specifies any number of comma-separated custom flags that can be used to control and alter the behavior of jinja report generation. In example one could specify `--report-jinja-flags summary` to visualize a top-level summary in a report that is otherwise hidden if the flag is not specified. How these flags are used is entirely up to the template. |

<a name="filters"></a>
### Filters

The parameters allowing to include and exclude checks based on id and tags.

| Parameter | Mandatory | Default value | Parameter description |
| --- | --- | --- | --- |
| `--tags-grouping TAGS_GROUPING` | no | none | Groups the checks in a hierarchical structure, allowing to aggregate uptime stats based on groups. This parameter requires a comma-separated list of tags for each level and each level is separated by a pipe character. For example, "productA,productB\|client-facing,internal" where checks are grouped based on productA and productB tags first and then for each further sub-grouped in client-facing and internal. Tags grouping can provide useful insight and structure to the reports and are explained in detail in the [Tags Grouping](TAGSGROUPING.md) documentation. |
| `--tags-exclude TAGS_LIST` | no | off | Specifies a comma-separated list of tags and excludes from the report any check with those tags. The special tag "none" can be used, even in combination with others, to exclude cheks without any tag. |
| `--tags-include TAGS_LIST` | no | off | Specifies a comma-separated list of tags and includes in the report only checks with at least one of those tags. The special tag "none" can be used, even in combination with others, to include cheks without any tag. |
| `--checks-exclude CHECKS_LIST` | no | off | Specifies a comma-separated list of checks ID and excludes from the report those checks. |
| `--checks-exclude-paused` | no | off | When specified, excludes from the report paused checks. By defauly paused checks are included. |
| `--checks-include CHECKS_LIST` | no | off | Specifies a comma-separated list of checks ID and includes in the report only those checks. |

<a name="others"></a>
### Others

Other parameters available in the tool.

| Parameter | Mandatory | Default value | Parameter description |
| --- | --- | --- | --- |
| `--verbosity {0,1,2}` | no | 1 | Controls the verbosity of the tool. Accepts 0 = quiet, 1 = default, 2 = debug as parameters. Quiet mode can be useful when printing the report on screen and redirecting the standard output. |
| `--help` | no | none | Displays the help with a summary of all available parameters. |
