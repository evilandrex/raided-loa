---
title: Raided Lost Ark Log Summarizer
toc: false
---

<h1>Raided Lost Ark Log Summarizer</h1>
Locally summarize your runs!

<div class="grid grid-cols-2" style="grid-auto-rows: auto;">
    <div class="card">
      ${fileUpload}
      ${bossSelect}
      ${dateStartSelect}
      ${dateEndSelect}
      ${filterClearedToggle}
    </div>

</div>

```js uploader
const fileUpload = Inputs.file();
const file = Generators.input(fileUpload);
```

```js sqlite
let db, bosses, bossEntities;
if (!!file) {
  db = await file.sqlite();
  await db.query(`
    ALTER TABLE encounter_preview 
      ADD COLUMN boss_diff TEXT;
    UPDATE encounter_preview 
      SET boss_diff = concat(current_boss, " - ", difficulty) 
      WHERE difficulty IS NOT "";
    UPDATE encounter_preview 
      SET boss_diff = current_boss 
      WHERE difficulty IS "";
  `);

  bosses = await db.query(`SELECT DISTINCT boss_diff FROM encounter_preview`);
  bosses = bosses.map((row) => row.boss_diff);
}
```

```js boss select
const bossDict = 
// let bossSelect = "";
let bossSelect, selectedBoss;
if (!!bosses) {
  bossSelect = Inputs.select(bosses, {
    label: "Bosses (shift+click to select multiple)",
    multiple: true,
  });

  selectedBoss = Generators.input(bossSelect);
}
```

```js date selectors
let dateStart, dateEnd;
let dateStartSelect,
  dateEndSelect = "";
if (!!bosses) {
  const now = new Date(Date.now());
  let dayDiff;
  if (now.getDay() < 3) {
    // Less than Wednesday
    dayDiff = 4 + now.getDay();
  } else {
    // Wednesday or more
    dayDiff = now.getDay() - 3;
  }
  const weekStart = new Date(now);
  weekStart.setDate(now.getDate() - dayDiff);
  weekStart.setHours(0, 0, 0, 0); // TODO: Account for different server resets

  dateStartSelect = Inputs.datetime({
    label: "Start Date",
    value: weekStart,
  });
  dateStart = Generators.input(dateStartSelect);

  dateEndSelect = Inputs.datetime({
    label: "End Date",
    value: now,
  });
  dateEnd = Generators.input(dateEndSelect);
}
```

```js only cleared toggle
let filterClearedToggle, filterCleared;
if (!!bosses) {
  filterClearedToggle = Inputs.toggle({
    label: "Only Cleared",
    value: true,
  });
  filterCleared = Generators.input(filterClearedToggle);
}
```

```js filtered encounters
if (!!bosses) {
  let filterQuery = `
    SELECT * FROM encounter_preview
      WHERE fight_start BETWEEN ${dateStart.getTime()} AND ${dateEnd.getTime()}
  `;

  if (selectedBoss.length > 0) {
    filterQuery += ` AND boss_diff IN (${selectedBoss
      .map((boss) => `'${boss}'`)
      .join(",")})`;
  }

  const filteredEncounters = await db.query(filterQuery);

  display(Inputs.table(filteredEncounters, { select: false }));
}
```

```js encounter preview table
const encounterPreview = await db.sql`SELECT * FROM encounter_preview`;
display(Inputs.table(encounterPreview, { select: false }));
```

```js encounter table
const encounter = await db.sql`SELECT * FROM encounter`;
display(Inputs.table(encounter, { select: false }));
```

```js entity table
const entity = await db.sql`SELECT * FROM entity`;
display(Inputs.table(entity, { select: false }));
```
