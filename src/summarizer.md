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
}
// console.log(selectedEncounter);
//display(Inputs.table(filteredIDs, { select: false }));
```

```js single encounter
let encID = filteredIDs[filteredIDs.length - 1].id;
let singleEncounter = await db.query(`
  SELECT * FROM encounter
    WHERE id = ${encID}
`);

display(JSON.parse(singleEncounter[0]["misc"]));
```

```js get all single encounter info
async function get_encounter_info(encID) {
  const encounter = await db.query(`
    SELECT * FROM encounter
      WHERE id = ${encID}
  `);
  const encounterInfo = JSON.parse(encounter[0]["misc"]);

  const entities = await db.query(`
    SELECT * FROM entity
      WHERE encounter_id = ${encID}
      AND entity_type = "PLAYER"
  `);

  const encounterPreview = await db.query(`
    SELECT * FROM encounter_preview
      WHERE id = ${encID}
  `);
  
  // Get boss hp info
  const hpLog = encounterInfo["bossHpLog"];
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
  for (let i = 0; i < entities.length; i++) {
    const entity = entities[i];
    const damageInfo = JSON.parse(entity["damage_stats"]);
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
  };
}

display(await get_encounter_info(encID));
```

```js encounter entities
let encounterEntities = await db.query(`
  SELECT * FROM entity
    WHERE encounter_id = ${encID}
    AND entity_type = "PLAYER"
`);

const partyInfo = JSON.parse(singleEncounter[0]["misc"])["partyInfo"];
const partyNumbers = Object.keys(partyInfo);
const playerInfo = [];
for (let i = 0; i < encounterEntities.length; i++) {
  const entity = encounterEntities[i];
  const damageInfo = JSON.parse(entity["damage_stats"]);
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
    supBrandUptime: damageInfo["debuffedBySupport"] / damageInfo["damageDealt"],
    critPercent: damageInfo["critDamage"] / damageInfo["damageDealt"],
    frontPercent: damageInfo["frontAttackDamage"] / damageInfo["damageDealt"],
    backPercent: damageInfo["backAttackDamage"] / damageInfo["damageDealt"],
    damageTaken: damageInfo["damageTaken"],
    deaths: damageInfo["deaths"],
    deathTime: damageInfo["deathTime"],
  });
}
display(Inputs.table(encounterEntities, { select: false }));
```

```js damage states example
display(JSON.parse(encounterEntities[7]["damage_stats"]));
```

```js test
display(playerInfo);
```

```js boss hp info
const hpLog = JSON.parse(singleEncounter[0]["misc"])["bossHpLog"];
const bosses = Object.keys(hpLog);

function getBossHPInfo(hpLog) {
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
  return bossesHPInfo;
}

const bossesHPInfo = getBossHPInfo(hpLog);
// display(bossesHPInfo);
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
