---
title: Introduction
toc: false
---

<style>

.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: var(--sans-serif);
  margin: 4rem 0 8rem;
  text-wrap: balance;
  text-align: center;
}

.hero h1 {
  margin: 2rem 0;
  max-width: none;
  font-size: 14vw;
  font-weight: 900;
  line-height: 1;
  background: linear-gradient(30deg, var(--theme-foreground-focus), currentColor);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero h2 {
  margin: 0;
  max-width: 34em;
  font-size: 20px;
  font-style: initial;
  font-weight: 500;
  line-height: 1.5;
  color: var(--theme-foreground-muted);
}

@media (min-width: 640px) {
  .hero h1 {
    font-size: 90px;
  }
}

</style>

<div class="hero">
  <h1>Raided Lost Ark</h1>
</div>

## TL;DR

[Click here to see the charts](https://raided.pro/loa-logs). We rank classes
based on their overall performance. The boxes represent a reasonable range for
the typical performance of each build. Compare classes primarily based on these
boxes, farther right is better. The right whisker provides a reasonable ceiling,
but do not expect most players to reach this. There are many factors we do not
account for such as gear, player skill, and supports.

---

## How to read

In general, you should compare classes based on their box (the colored part), as
that's where a majority of players will fall, in terms of performance. Note that
we do not account for differences in gear outside of ilevel (which means tripods,
gems, elixirs, and transcendence will affect this). Indeed player skill matters
quite a bit, in terms of performance. If you would like to compare performance
with more similar gear, you can try to reduce the ilevel ranges in the advanced
options to cut out certain progression systems. Be careful of the low sample
sizes when doing this.

If you would like to look at
for a "reasonable ceiling" performance for each class, the right whisker
provides a reasonable estimate. Not that this "reasonable ceiling" does not mean
you cannot perform above it, this is exemplified by the stars that show off the
literal best performance given the filters.

## Method

We scrape data from [Faust's Lost Ark logs](https://logs.fau.dev/logs) every
night and classify each player in the logs based on their build. We produce
box plots using this data. The boxplots follow the typical procedures. It should
be noted that the whiskers (Q1 and Q3) are truncated to the minimum and maximum
values in the dataset to guarantee that it represents a possible value.

The default filters, in general, seek to provide a representative dataset for on
ilevel players in the typical situations in the current balance patch.

To ensure we do not use data that is not representative of the typical situation,
we classify logs as "Weird" if they do not have the expected number of players (
4 or 8, depending on content), if they have a Princess Gunlancer, if they do not
have the expected number of supports (either none or more than 1 per party), or
if we fail to classify a player's build. Additonally, we filter out players that
were dead when they cleared. These filters are on by default but can be toggled
in the advanced options.

There is no guarantee that we classify builds correctly but we do our best with
the following procedures:

<details>
<summary>Build classification criteria</summary>
Most builds are binary under a class, so if a player doesn't meet the criteria, 
they're the other build. All builds (except for Princess Maker) are named after
their main engraving.

- Berserker: Checking for the Mayhem buff.
- Destroyer: Checking for the special Gravity Training weapon attack.
- Gunlancer: If they do less than 5% damage, they're Princess Maker. If they have Nightmare or Hallucination set they're Combat Readiness.
- Paladin: If they do more than 10% of the team damage, they're Judgment.
- Slayer: If they have the Predator buff.

---

- Arcanist: If they did damage with the card Emperor
- Summoner: If they did damage with the skill Kelsion (Communication Overflow)
- Bard: If they do more than 10% of the team damage, they're True Courage
- Sorceress: Checking for the Igniter buff.

---

- Wardancer: Checking for the Esoteric Skills
- Scrapper: Checking for the unique Shock Training buff
- Soulfist: Checking for the unique Robust Spirit buff
- Glaivier: Checking for the Pinnacle buff
- Striker: Checking for the skill Call of the Wind God for Esoteric Flurry
- Breaker: Checking for the special Asura weapon attack.

---

- Deathblade: Checking for the unique Remaining Energy Death Trance doing more than 10% damage
- Shadowhunter: Checking for Demonic Impulse buff
- Reaper: Checking for the Lunar Voice buff
- Souleater: Checking for the Soul Snatch buff (Night's Edge)

---

- Sharpshooter: Checking for the Loyal Companion buff
- Deadeye: Check for the Enhanced Weapon buff
- Artillerist: Check for the Barrage skills
- Machinist: Check for the Evolutionary Legacy buff
- Gunslinger: Check for Sharpshooter skill (Peacemaker)

---

- Artist: If they do more than 10% of the team damage, they're Recurrence.
- Aeromancer: Check for Sunshower synergy buff on their own Sunshower skill (Wind Fury)
</details>

The data scraping is written in Python and the site/visualization is written
with Javascript in the Observable Framework. Data scraping and deployment is
automated through Github Actions and Github Pages. Observable Framework builds
the static files to serve the site with useful features such as responsivity,
interaction, light/dark modes, and mobile layouts. Repos are available for the
[site](https://github.com/evilandrex/raided-loa) and the
[scraper](https://github.com/evilandrex/raided-loa-scraper), contributions are
welcomed.

## Limitations

All data we get is from Faust's fork of Lost Ark Logs. This means that the data
we have is a subset of a subset of a subset. This may not be a perfectly
representative sample of the population.

Build classification (and weird logs classification) may be incorrect as we are
only inferring what we can using simple rules given the available data. Future
improvements to the data source (Faust's logs) may improve accuracy of the
classifications.

Especially for the latest content early in the balance patch cycles, we have
relatively low sample sizes meaning the estimates of performance for uncommon
builds may not be precise. We do not attempt to account for all possible causes
of performance differences, such as tripods, gems, cards, engravings, quality,
elixirs, transcendence, or player skill. Additionally, the support in the party
of each player will largely affect performance. In all, with sufficient sample
size, we should be able to estimate a reasonable range of performance (where the
true median build performance is) given the
variance from factors other than the build itself. However, it is difficult to
determine the exact cause of performance differences without more detailed data.
This means that the data should be used as a rough guide of relative balance and
not an exact representation of the true ranks of each build.
