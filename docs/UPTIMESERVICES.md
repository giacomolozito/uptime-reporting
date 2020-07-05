## uptime-reporting - uptime services

uptime-reporting currently supports two uptime services for data collection: [Pingdom](https://www.pingdom.com/) and [UptimeRobot](https://uptimerobot.com/). It does so by attempting to abstract the differences in API and data retrieval, and providing a unique data model for templating.

The uptime service is chosen with the `--service` [parameter](PARAMETERS.md) when running the tool.

This document contains service-specific notes, i.e. any notable difference in how the tool handles each service. Some of these are deliberate design decisions, others are due to different featureset in the services and API at the time of writing.


### Pingdom

- uptime-reporting only collects data from Pingdom uptime checks; it does not look into transaction checks or page speed checks


### UptimeRobot

- the API token required for uptime-reporting is the UptimeRobot Read-Only API key
- UptimeRobot does not have tagging support for checks; to work around that, uptime-reporting uses the following naming convention to read tags directly in the "Friendly Name" of the check: `your check name |tag1,tag2,...` ; therefore, to use tags grouping with UptimeRobot, tags must be added comma-separated in the friendly name, after a pipe symbol
- uptime-reporting only collects up/down time and ignores any check paused time (which is considered as up time); this is due to how the data is retrieved via API
