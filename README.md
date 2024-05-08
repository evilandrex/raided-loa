# Raided - Lost Ark Scraper

[![Daily Log Scrape](https://github.com/evilandrex/raided-loa-scraper/actions/workflows/scrape_daily.yml/badge.svg)](https://github.com/evilandrex/raided-loa-scraper/actions/workflows/scrape_daily.yml)

Scrapes Faust's Lost Ark logs and stores all of the data as a csv. This includes
a CLI to select which logs to scrape. We also scrape daily using Github Actions
to continuously update data in the /data file. This data is used for Raided Lost
Ark.

To see how to use the CLI

```
python scrape.py --help
```
