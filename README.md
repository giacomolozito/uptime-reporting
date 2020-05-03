# uptime-reporting

Service Uptime reporting tool, designed around uptime checks and leveraging tags to organize checks in the report.  
Currently supports [Pingdom](https://www.pingdom.com/) for data collection.

Key features:
- uses the service API to gather uptime statistics for a designed time range (weekly, monthly, custom)
- [tags grouping](docs/TAGSGROUPING.md) capability with aggregated stats per tags, to make reports more structured and readable
- [inclusion/exclusion](docs/PARAMETERS.md#filters) of checks from the reports based on their id, tags or status
- terminal-friendly on-screen report generation or Jinja-based [report templating](docs/TEMPLATING.md) to output in HTML, PDF, XML, etc.

![Report examples](https://user-images.githubusercontent.com/9863475/82117785-88764000-976a-11ea-9549-735411ca813b.png)

## How to install

Requires Python => 3.7

```bash
pip install uptime-reporting
```

## Usage

On-screen report of all checks for last week:
```bash
uptime-reporting --service pingdom --token XYZ --report weekly --date last
```

On-screen report of all checks for Jan 2020 (any date within that month causes the month to be selected):
```bash
uptime-reporting --service pingdom --token XYZ --report monthly --date 2020-01-01
```

HTML-based report of all checks for a custom date range, written to file report.html:
```bash
uptime-reporting --service pingdom --token XYZ --report range --date 2020-02-01_2020-03-15 \
  --report-format jinja --report-jinja-template default.html --report-filename report.html
```

On-screen report with terminal colors, excluding certain tags and checks from the report:
```bash
uptime-reporting --service pingdom --token XYZ --report weekly --date last --tags-exclude foo,bar \
  --checks-exclude 123456,123457 --report-format text --report-text-colors
```

Report grouping checks by product and for each product by client-facing vs internal endpoint (based on tags):
```bash
uptime-reporting --service pingdom --token XYZ --report weekly --date last --tags-grouping "productA,productB|client-facing,internal" \
  --report-format jinja -report-jinja-template default.html --report-filename report.html
```

See [Parameters](docs/PARAMETERS.md), [Tags Grouping](docs/TAGSGROUPING.md) and [Template Writing](docs/TEMPLATES.md) docs for in-depth explanation.  
Understanding Tag Grouping is especially important for well-organized reports.


## Disclaimer

This is an open source tool released under GPLv3, in the hope it will be useful.  
It is not endorsed by Pingdom, Solarwinds or any other organization.
