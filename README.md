# Raided Lost Ark

A front-end for a Lost Ark log data aggregate tool. The goal is to be able to
display relevant data in a user-friendly way while still providing many options
and filters for the user to use. I emphasize data density in the main plots such
that if one were to take a screenshot of the plot, most of the relevant
information is available while allowing interactivity to give exact details and
improve ease of use.

The data is scraped from [Faust's Lost Ark logs](https://logs.fau.dev/logs)
using their API and stored in a separate repo, which is where the data is pulled
from for the client. See the
[scraper repo](https://github.com/evilandrex/raided-loa-scraper) for raw data
and details.

## Development

This is an [Observable Framework](https://observablehq.com/framework) project.
To start the local preview server, run:

```
npm run dev
```

Then visit <http://localhost:3000> to preview your project.

### Command reference

| Command              | Description                                 |
| -------------------- | ------------------------------------------- |
| `npm install`        | Install or reinstall dependencies           |
| `npm run dev`        | Start local preview server                  |
| `npm run build`      | Build your static site, generating `./dist` |
| `npm run deploy`     | Deploy your project to Observable           |
| `npm run clean`      | Clear the local data loader cache           |
| `npm run observable` | Run commands like `observable help`         |
