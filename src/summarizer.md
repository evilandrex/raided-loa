---
title: Raided Lost Ark Log Summarizer
toc: false
---

<h1>Raided Lost Ark Log Summarizer</h1>
Locally summarize your runs!

<div class="grid grid-cols-2" style="grid-auto-rows: auto;">
    <div class="card">
      ${fileUpload}
      ${encounterText ? encounterText : ""}
      ${dateStartSelect ? dateStartSelect : ""}
      ${dateEndSelect ? dateEndSelect : ""}
      ${nameTextArea ? nameTextArea : ""}
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
}
```

```js constants
import pako from "npm:pako";

const encounterDict = await FileAttachment("encounters.json").json();
const encounters = Object.keys(encounterDict)
  .map((key) =>
    encounterDict[key].difficulties.map((diff) => `${key} - ${diff}`)
  )
  .flat()
  .map((encounter) =>
    encounter.split(" - ")[1] == "" ? encounter.split([" - "])[0] : encounter
  );
const hpBarMap = await FileAttachment("bossHPBars.json").json();
```

```js encounter select
let encounterText, selectedEncounter;
if (!!db) {
  encounterText = Inputs.text({
    label: "Encounter (start typing to search)",
    datalist: encounters,
    required: true,
  });

  selectedEncounter = Generators.input(encounterText);
}
```

```js name filters
let nameTextArea, nameFilter;
if (!!db) {
  nameTextArea = Inputs.textarea({
    label: "Names (comma separated)",
    placeholder: "Leave blank to include all",
  });

  nameFilter = Generators.input(nameTextArea);
}
```

```js date selectors
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

let dateStart, dateEnd, dateStartSelect, dateEndSelect;
if (!!db) {
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

```js filtered encounters
let filteredIDs;
// console.log(selectedEncounter);
// console.log(dateStart);
// console.log(dateEnd);
if (!!selectedEncounter) {
  const selectedBoss = encounterDict[selectedEncounter.split(" - ")[0]].names;
  let selectedDiff = selectedEncounter.split(" - ")[1];
  if (!selectedDiff) {
    selectedDiff = "";
  }
  let filterQuery = `
    SELECT id FROM encounter_preview
      WHERE current_boss IN (${selectedBoss
        .map((name) => `'${name}'`)
        .join(", ")})
      AND difficulty = '${selectedDiff}' 
      AND fight_start BETWEEN '${dateStart.getTime()}' AND '${dateEnd.getTime()}'
  `;

  filteredIDs = await db.query(filterQuery);
  // console.log(filteredIDs);
}
// console.log(selectedEncounter);
//display(Inputs.table(filteredIDs, { select: false }));
```

```js get all single encounter info
async function get_encounter_info(encID) {
  const encounter = await db.query(`
    SELECT * FROM encounter
      WHERE id = ${encID}
  `);
  const encounterInfo = JSON.parse(encounter[0]["misc"]);
  // console.log(encounter[0]);
  const playerEntities = await db.query(`
    SELECT * FROM entity
      WHERE encounter_id = ${encID}
      AND entity_type = "PLAYER"
  `);

  const encounterPreview = await db.query(`
    SELECT * FROM encounter_preview
      WHERE id = ${encID}
  `);

  // Get boss hp info
  // zlib.gunzipSync(blobObj).toString('utf8')
  let hpLog = encounterInfo["bossHpLog"];
  if (!hpLog) {
    let inflated = pako.inflate(encounter[0]["boss_hp_log"]);
    hpLog = new TextDecoder().decode(inflated);
    hpLog = JSON.parse(hpLog);
  }
  const bosses = Object.keys(hpLog);

  const bossesHPInfo = [];
  for (let i = 0; i < bosses.length; i++) {
    const hpBars = hpBarMap[bosses[i]];
    const lastInfo = hpLog[bosses[i]].slice(-1)[0];

    let bossBars;
    if (hpBars) {
      bossBars = Math.ceil(hpBars * lastInfo["p"]);
    }

    bossesHPInfo.push({
      name: bosses[i],
      hp: lastInfo["hp"],
      p: lastInfo["p"],
      bars: bossBars,
      time: lastInfo["time"],
    });
  }

  bossesHPInfo.sort((a, b) => a.time - b.time);

  // Get player info
  const partyInfo = encounterInfo["partyInfo"];
  const partyNumbers = Object.keys(partyInfo);
  const playerInfo = [];
  for (let i = 0; i < playerEntities.length; i++) {
    const entity = playerEntities[i];
    let damageInfo = entity["damage_stats"];
    if (typeof damageInfo === "object") {
      let inflated = pako.inflate(entity["damage_stats"]);
      damageInfo = new TextDecoder().decode(inflated);
      damageInfo = JSON.parse(damageInfo);
    } else {
      damageInfo = JSON.parse(damageInfo);
    }
    playerInfo.push({
      name: entity["name"],
      class: entity["class"],
      party: Number(
        partyNumbers.filter((num) => partyInfo[num].includes(entity["name"]))[0]
      ),
      dps: damageInfo["dps"],
      supAPUptime: damageInfo["buffedBySupport"] / damageInfo["damageDealt"],
      supIdentityUptime:
        damageInfo["buffedByIdentity"] / damageInfo["damageDealt"],
      supBrandUptime:
        damageInfo["debuffedBySupport"] / damageInfo["damageDealt"],
      critPercent: damageInfo["critDamage"] / damageInfo["damageDealt"],
      frontPercent: damageInfo["frontAttackDamage"] / damageInfo["damageDealt"],
      backPercent: damageInfo["backAttackDamage"] / damageInfo["damageDealt"],
      damageTaken: damageInfo["damageTaken"],
      deaths: damageInfo["deaths"],
      deathTime: damageInfo["deathTime"],
    });
  }

  return {
    bossHPInfo: bossesHPInfo,
    playerInfo: playerInfo,
    cleared: encounterPreview[0]["cleared"],
    fightStart: encounterPreview[0]["fight_start"],
  };
}

const encounterInfos = [];
for (let i = 0; i < filteredIDs.length; i++) {
  try {
    const encounterInfo = await get_encounter_info(filteredIDs[i]["id"]);
    encounterInfos.push(encounterInfo);
  } catch (e) {
    console.log("Failed encounter ID: " + filteredIDs[i]["id"]);
    console.log(e);
  }
}
display(encounterInfos);
```

# Dev preview

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
