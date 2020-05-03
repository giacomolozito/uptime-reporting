## uptime-reporting - tags grouping

Tags Grouping is a peculiar feature of this reporting tool allowing to group checks and aggregate their statistics based on tags.

The classic use case is the following: with services like Pingdom, people manage hundreds of uptime checks, typically for different products and portals belonging to their organizations. Products also have different type of monitored endpoints: client-facing user-interface, API, service endpoints for internal use in the organization.

As such, a flattened report that puts all of these entities together and builds an uptime average across all of them is not necessarily useful. After all, an outage on an internal service endpoint might not be as critical as an outage on the client-facing user-interface or API.

Thankfully, checks can have tags (or more rigorously, "labels") allowing to qualify each uptime check in one or more way. This can be leveraged to group checks with uptime-reporting, using the `--tags-grouping` parameter.

### A practical example

As a practical example, let's assume the following tags are used with the uptime checks in Pingdom.
- productA
- productB
- client-facing
- internal

An uptime check might have `productA` and `client-facing`. Another one might have `productA` and `internal`. Another `productB` and `internal`. And so on. We are in effect describing a hierarchical structure where we group checks by product at the first level, and by client-facing vs internal at the second level. There could be other choices at each level and even more than two levels, the tool supports any arbitrary depth although it's rarely useful to go deeper than two.

For the example above, the tags grouping parameter would be `--tags-grouping "productA,productB|client-facing,internal"`.  
With this parameter the tool would generate, along with individual checks stats:

```bash
| the aggregated uptime stats of all checks in the report (this is always done)
|
\-- the aggregated uptime stats of all checks wih tag productA
| |
| \-- the aggregated uptime stats of all checks with tag productA and client-facing
| |
| \-- the aggregated uptime stats of all checks with tag productA and internal
|
\-- the aggregated uptime stats of all checks with tag productB
  |
  \-- the aggregated uptime stats of all checks with tag productB and client-facing
  |
  \-- the aggregated uptime stats of all checks with tag productB and internal
```

A few things to note:
- Checks having only a productA tag without internal or client-facing tag would be only considered within the aggregated uptime stats at productA level, but not deeper than that
- Checks having a productA tag and both a client-facing and internal tag would appear listed twice under both aggregations and factor twice in the uptime stats at productA level; for this reason, it's best to design a tag strategy without these overlaps
- Checks without the productA or productB label would only factor into the aggregated uptime stats of all checks in the report (and depending on the report and template used, listed under it); if this is not desired and the report must only contain checks referring to productA and productB, use `--include-tags productA,productB` to ensure this is the case and exclude all other checks

An example with more products and an additional second level could look like this: `--tags-grouping "productA,productB,productC,productD|client-facing,api,internal"`.

### Summarizing

These are the key steps to a structured report:
- define the tagging strategy on uptime checks, based on the desired view of the world (in example categorise by product and purpose)
- avoid same-level overlaps in the tagging strategy (i.e. a check being both "client-facing" and "internal") unless it is expressly desired to have certain checks listed and factored twice in the report
- take advantage of [filter parameters](PARAMETERS.md#filters) to include/exclude tags and checks and ensure the report only contains the desired information
