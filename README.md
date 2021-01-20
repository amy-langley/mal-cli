# mal-cli

This is a quick and dirty tool to scrape the MAL database (via the caching service jikan.moe) and insert nodes into a Neo4j graph database.

For example, to load Hideaki Anno (MAL id 5111), every series he has worked on (according to the relationships that are configured in the `EntityManager`), everyone who worked on THOSE series, and every series THEY worked on:

```
$ mal-cli update -p 5111 -d 3
```

You can always blow away the contents of the graph database with:

```
$ mal-cli clear
```

Do not scrape the entire MAL db because they don't like that. This code tries to be respectful of Jikan's rate limits by using exponential backoff with urllib3 retry, but don't push your luck.
