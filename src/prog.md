---
title: Progression Analysis
toc: false
---

<h1>Progression Analysis</h1>

<div class="grid grid-cols-2" style="grid-auto-rows: auto;">
    <div class="card">
      ${fileUpload}
      ${encounterText ? encounterText : ""}
      ${dateStartSelect ? dateStartSelect : ""}
      ${dateEndSelect ? dateEndSelect : ""}
      ${minDurationRange ? minDurationRange : ""}
      ${maxDurationRange ? maxDurationRange : ""}
      ${nameTextArea ? nameTextArea : ""}
      ${clearedToggle ? clearedToggle : ""}
    </div>
    <div>
        Load your encounters.db to show analysis tools. This file can be found 
        in your database folder (e.g., C:\Users\[USER]\AppData\Local\LOA Logs). 
        You can also get to this folder from your settings of LOA Logs in the 
        database page. WARNING: if your database is very large, this will take
        a lot of RAM and extremely large databases may simply not work, sorry!
    </div>
</div>

```js constants
import pako from "npm:pako";
import SQLite from "npm:@observablehq/sqlite";

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

const supportClasses = ["Bard", "Paladin", "Artist"];

function formatPercent(x) {
  return Math.round(x * 1000) / 10 + "%";
}

function formatMillions(x) {
  return Math.round(x / 100_000) / 10 + "M";
}

function formatThousands(x) {
  return Math.round(x / 1000) + "K";
}

function formatDuration(x) {
  let progTimeStr = "";
  if (x > 60 * 60) {
    progTimeStr = `${Math.floor(x / 60 / 60)}h `;
    x %= 60 * 60;
  }
  progTimeStr += `${Math.floor(x / 60)}m ${Math.round(x % 60)}s`;

  return progTimeStr;
}
```

```js uploader
const fileUpload = Inputs.file({ label: "Load encounters.db", accept: ".db" });
const file = Generators.input(fileUpload);
```

```js sqlite
let db, bosses, bossEntities;
if (!!file) {
  db = await file.sqlite();
}
```

```js encounter select
let encounterText, selectedEncounter;
if (!!db) {
  encounterText = Inputs.text({
    label: "Encounter",
    placeholder: "Type to search",
    datalist: encounters,
    required: true,
    submit: true,
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

```js min duration filter
let minDuration, minDurationRange;
if (!!db) {
  minDurationRange = Inputs.range([0, 1200], {
    label: "Min Duration (s)",
    step: 10,
    value: 30,
  });

  minDuration = Generators.input(minDurationRange);
}
```

```js max duration filter
let maxDuration, maxDurationRange;
if (!!db) {
  maxDurationRange = Inputs.range([0, 1800], {
    label: "Max Duration (s)",
    step: 10,
    value: 1800,
  });

  maxDuration = Generators.input(maxDurationRange);
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

```js cleared toggle filter
let clearedToggle, filterCleared;
if (!!db) {
  clearedToggle = Inputs.toggle({
    label: "Show only cleared",
    value: false,
  });
  filterCleared = Generators.input(clearedToggle);
}
```

```js boss info
let selectedBossNames, selectedBossBars, selectedBossTotalBars;

if (!!selectedEncounter) {
  selectedBossNames = encounterDict[selectedEncounter.split(" - ")[0]]["names"];
  selectedBossBars = selectedBossNames.map((name) => hpBarMap[name]);
  selectedBossTotalBars = selectedBossBars
    .filter((bars) => !!bars)
    .reduce((a, b) => a + b, 0);
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
    selectedDiff = ["", "Normal"];
  } else {
    selectedDiff = [selectedDiff];
  }

  let filterQuery = `
    SELECT id FROM encounter_preview
      WHERE current_boss IN (${selectedBoss
        .map((name) => `'${name}'`)
        .join(", ")})
      AND difficulty IN (${selectedDiff.map((diff) => `'${diff}'`).join(", ")}) 
      AND fight_start BETWEEN '${dateStart.getTime()}' AND '${dateEnd.getTime()}'
      AND duration BETWEEN ${minDuration * 1000} AND ${maxDuration * 1000}
      ${filterCleared ? "AND cleared = 1" : ""}
  `;

  // console.log(filterQuery);
  filteredIDs = await db.query(filterQuery);
  // console.log(filteredIDs);
}
// console.log(selectedEncounter);
// display(Inputs.table(filteredIDs, { select: false }));
```

```js get encounter info
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
      if (lastInfo["hp"] == 1) {
        bossBars = hpBars;
      } else {
        bossBars = hpBars - Math.ceil(hpBars * lastInfo["p"]);
      }
    }

    bossesHPInfo.push({
      name: bosses[i],
      hp: lastInfo["hp"],
      p: lastInfo["p"],
      barsComplete: bossBars,
      time: lastInfo["time"],
    });
  }

  bossesHPInfo.sort((a, b) => a.time - b.time);

  const encounterEnd = encounter[0]["last_combat_packet"];

  // Get player info
  const partyInfo = encounterInfo["partyInfo"];
  let partyNumbers;
  if (partyInfo) {
    partyNumbers = Object.keys(partyInfo);
  }
  // console.log(partyInfo);

  const playerInfo = [];
  for (let i = 0; i < playerEntities.length; i++) {
    const entity = playerEntities[i];
    const skillStats = JSON.parse(entity["skill_stats"]);
    let damageInfo = entity["damage_stats"];
    if (typeof damageInfo === "object") {
      let inflated = pako.inflate(entity["damage_stats"]);
      damageInfo = new TextDecoder().decode(inflated);
      damageInfo = JSON.parse(damageInfo);
    } else {
      damageInfo = JSON.parse(damageInfo);
    }

    const realDeath = encounterEnd - damageInfo["deathTime"] > 1000;

    const party = partyNumbers
      ? Number(
          partyNumbers.filter((num) =>
            partyInfo[num].includes(entity["name"])
          )[0]
        )
      : 0;
    playerInfo.push({
      name: entity["name"],
      class: entity["class"],
      isSupport: supportClasses.includes(entity["class"]),
      party: party,
      dps: damageInfo["dps"],
      supAPUptime: damageInfo["buffedBySupport"] / damageInfo["damageDealt"],
      supBrandUptime:
        damageInfo["debuffedBySupport"] / damageInfo["damageDealt"],
      supIdentityUptime:
        damageInfo["buffedByIdentity"] / damageInfo["damageDealt"],
      shielded: damageInfo["damageAbsorbedOnOthers"],
      critPercent: skillStats["crits"] / skillStats["hits"],
      frontPercent: skillStats["frontAttacks"] / skillStats["hits"],
      backPercent: skillStats["backAttacks"] / skillStats["hits"],
      damageTaken: damageInfo["damageTaken"],
      deaths: realDeath ? damageInfo["deaths"] : damageInfo["deaths"] - 1,
      deathTime: realDeath ? damageInfo["deathTime"] : 0,
      cleared: encounterPreview[0]["cleared"],
    });
  }

  const fightDuration =
    (encounter[0]["last_combat_packet"] - encounterPreview[0]["fight_start"]) /
    1000;
  const nDPS = playerInfo.filter((player) => !player.isSupport).length;
  const nSup = playerInfo.filter((player) => player.isSupport).length;

  const avgTeamDps = playerInfo
    .filter((player) => !player.isSupport)
    .map((player) => player.dps)
    .reduce((a, b) => a + b, 0);

  const avgTeamDamageTaken = playerInfo
    .map((player) => player.damageTaken)
    .reduce((a, b) => a + b, 0);
  const avgTeamDPSTaken = avgTeamDamageTaken / fightDuration;

  const avgAPUptime =
    nDPS > 0
      ? playerInfo
          .filter((player) => !player.isSupport)
          .map((player) => player.supAPUptime)
          .reduce((a, b) => a + b, 0) / nDPS
      : 0;
  const avgBrandUptime =
    nDPS > 0
      ? playerInfo
          .filter((player) => !player.isSupport)
          .map((player) => player.supBrandUptime)
          .reduce((a, b) => a + b, 0) / nDPS
      : 0;
  const avgIdentityUptime =
    nDPS > 0
      ? playerInfo
          .filter((player) => !player.isSupport)
          .map((player) => player.supIdentityUptime)
          .reduce((a, b) => a + b, 0) / nDPS
      : 0;

  return {
    id: encID,
    avgTeamDps: avgTeamDps,
    barsComplete: bossesHPInfo
      .map((boss) => boss.barsComplete)
      .filter((bars) => !!bars)
      .reduce((a, b) => a + b, 0),
    avgTeamDPSTaken: avgTeamDPSTaken,
    avgTeamDamageTaken: avgTeamDamageTaken,
    avgAPUptime: avgAPUptime,
    avgBrandUptime: avgBrandUptime,
    avgIdentityUptime: avgIdentityUptime,
    deaths: playerInfo
      .map((player) => player.deaths)
      .reduce((a, b) => a + b, 0),
    cleared: encounterPreview[0]["cleared"],
    fightStart: encounterPreview[0]["fight_start"],
    duration: fightDuration,
    bossHPInfo: bossesHPInfo,
    playerInfo: playerInfo,
  };
}

const encounterInfos = [];
if (!!selectedEncounter) {
  const names = nameFilter.split(",").map((name) => name.trim());
  for (let i = 0; i < filteredIDs.length; i++) {
    try {
      const encounterInfo = await get_encounter_info(filteredIDs[i]["id"]);

      if (nameFilter !== "") {
        const playerNames = encounterInfo.playerInfo.map(
          (player) => player.name
        );
        if (names.every((name) => playerNames.includes(name))) {
          encounterInfos.push(encounterInfo);
        }
      } else {
        encounterInfos.push(encounterInfo);
      }
    } catch (e) {
      console.log("Failed encounter ID: " + filteredIDs[i]["id"]);
      console.log(e);
    }
  }
  encounterInfos.sort((a, b) => a["id"] - b["id"]);
}

// display(encounterInfos);
```

**${selectedEncounter ? selectedEncounter : ""}**

```js boss info / encounter summaries
let totalDuration,
  avgPullDuration,
  avgTeamDPS,
  avgTeamDmgTaken,
  avgTeamDPSTaken,
  avgAPUptime,
  avgBrandUptime,
  avgIdentityUptime,
  bestEncounter,
  avgBossBarsComplete;

if (!!selectedEncounter) {
  totalDuration = tableEncounters
    .map((enc) => enc.duration)
    .reduce((a, b) => a + b, 0);
  avgPullDuration = totalDuration / tableEncounters.length;

  avgTeamDPS =
    tableEncounters.map((enc) => enc.avgTeamDps).reduce((a, b) => a + b, 0) /
    tableEncounters.length;

  avgTeamDmgTaken =
    tableEncounters
      .map((enc) => enc.avgTeamDamageTaken)
      .reduce((a, b) => a + b, 0) / tableEncounters.length;
  avgTeamDPSTaken =
    tableEncounters
      .map((enc) => enc.avgTeamDPSTaken)
      .reduce((a, b) => a + b, 0) / tableEncounters.length;

  avgAPUptime =
    tableEncounters.map((enc) => enc.avgAPUptime).reduce((a, b) => a + b, 0) /
    tableEncounters.length;
  avgBrandUptime =
    tableEncounters
      .map((enc) => enc.avgBrandUptime)
      .reduce((a, b) => a + b, 0) / tableEncounters.length;
  avgIdentityUptime =
    tableEncounters
      .map((enc) => enc.avgIdentityUptime)
      .reduce((a, b) => a + b, 0) / tableEncounters.length;

  bestEncounter = tableEncounters.reduce((a, b) =>
    a.barsComplete > b.barsComplete ? a : b
  );

  avgBossBarsComplete = Math.round(
    tableEncounters.map((enc) => enc.barsComplete).reduce((a, b) => a + b, 0) /
      tableEncounters.length
  );

  // display(bestEncounter);
}
```

```js summary div
if (!!selectedEncounter) {
  display(html`<div class="grid grid-cols-3 card" style="grid-auto-rows: auto;">
    <div>
      Pulls: ${tableEncounters.length} (${formatDuration(avgPullDuration)} per
      pull)
      <br />
      Total Prog Time: ${formatDuration(totalDuration)}
    </div>
    <div>
      Avg Team DPS: ${formatMillions(avgTeamDPS)}
      <br />
      Avg Dmg Taken: ${formatThousands(avgTeamDmgTaken)} (${formatThousands(
        avgTeamDPSTaken
      )} DPS)
    </div>
    <div>
      Avg Sup. Performance: ${Math.round(avgAPUptime * 100)}/${Math.round(
        avgBrandUptime * 100
      )}/${Math.round(avgIdentityUptime * 100)}
      <br />
      Avg Complete: ${avgBossBarsComplete}/${selectedBossTotalBars} bars
    </div>
    <div class="grid-colspan-3">
      <b>Best Run —</b> Log ID: ${bestEncounter.id} - Bars complete: ${bestEncounter.barsComplete}/${selectedBossTotalBars}
      - Duration: ${formatDuration(bestEncounter.duration)} - Cleared: ${bestEncounter.cleared ==
      1
        ? "Yes"
        : "No"}
      <br />
      DPS: ${formatMillions(bestEncounter.avgTeamDps)} - Total Damage Taken: ${formatThousands(
        bestEncounter.avgTeamDamageTaken
      )} - Average Support Performance: ${Math.round(
        bestEncounter.avgAPUptime * 100
      )}/${Math.round(bestEncounter.avgBrandUptime * 100)}/${Math.round(
        bestEncounter.avgIdentityUptime * 100
      )}
    </div>
  </div> `);
}
```

**${selectedEncounter ? "Pulls" : ""}**

```js encounters table
function sparkbar(max) {
  return (x) => htl.html`<div style="
    background: var(--theme-foreground-faintest);
    color: var(--theme-foreground);
    font: 10px/1.6 var(--sans-serif);
    width: ${(100 * x) / max}%;
    float: left; 
    box-sizing: border-box;
    overflow: visible;
    display: flex;
    justify-content: start;">${x.toLocaleString("en-US")}`;
}

const subBossFormat = {
  ID: String,
  "DPS (Total)": formatMillions,
  Duration: formatDuration,
  "DPS Taken (Total)": formatThousands,
};
const subBossWidths = {};
let encounterTable, tableSelect;
if (!!selectedEncounter) {
  for (let i = 0; i < selectedBossNames.length; i++) {
    subBossFormat[selectedBossNames[i]] = sparkbar(selectedBossBars[i]);
    subBossWidths[selectedBossNames[i]] = 100;
  }

  encounterTable = encounterInfos.map((enc) => {
    const row = {
      ID: enc.id,
      "Bars Complete": enc.barsComplete,
      Duration: enc.duration,
      "DPS (Total)": enc.avgTeamDps,
      "DPS Taken (Total)": enc.avgTeamDPSTaken,
      "Sup. Perf. ": `${Math.round(enc.avgAPUptime * 100)}/${Math.round(
        enc.avgBrandUptime * 100
      )}/${Math.round(enc.avgIdentityUptime * 100)}`,
      Deaths: enc.playerInfo
        .map((player) => player.deaths)
        .reduce((a, b) => a + b, 0),
      Cleared: enc.cleared == 1 ? "Yes" : "No",
    };

    for (let i = 0; i < enc.bossHPInfo.length; i++) {
      if (!enc.bossHPInfo[i].barsComplete) {
        continue;
      }
      const barsLeft =
        hpBarMap[enc.bossHPInfo[i].name] - enc.bossHPInfo[i].barsComplete;
      row[enc.bossHPInfo[i].name] = barsLeft;
    }

    return row;
  });

  tableSelect = view(
    Inputs.table(encounterTable, {
      select: true,
      value: encounterTable,
      format: subBossFormat,
      width: subBossWidths,
      layout: "auto",
    })
  );
}
```

```js table selected encounters
let tableEncounters;
if (!!selectedEncounter) {
  tableEncounters = encounterInfos.filter((enc) => {
    const selectedIDs = tableSelect.map((row) => row.ID);
    return selectedIDs.includes(enc.id);
  });
}
```

**${selectedEncounter ? "Player Summaries" : ""}**

```js player table
if (!!selectedEncounter) {
  const dpsNames = tableEncounters
    .map((enc) =>
      enc.playerInfo
        .filter((player) => !supportClasses.includes(player["class"]))
        .map((player) => player.name)
    )
    .flat()
    .filter((name, i, arr) => arr.indexOf(name) === i);
  const supNames = tableEncounters
    .map((enc) =>
      enc.playerInfo
        .filter((player) => supportClasses.includes(player["class"]))
        .map((player) => player.name)
    )
    .flat()
    .filter((name, i, arr) => arr.indexOf(name) === i);

  const dpsTable = dpsNames.map((name) => {
    const playerInfo = tableEncounters
      .map((enc) => enc.playerInfo.filter((player) => player.name === name))
      .flat();

    const row = {
      Name: name,
      Class: playerInfo[0].class,
      Pulls: playerInfo.length,
      "Last Party": playerInfo[playerInfo.length - 1].party,
      "DPS (Avg)":
        playerInfo.map((player) => player.dps).reduce((a, b) => a + b, 0) /
        playerInfo.length,
      "Crit Rate":
        playerInfo
          .map((player) => player.critPercent)
          .reduce((a, b) => a + b, 0) / playerInfo.length,
      "FA Rate":
        playerInfo
          .map((player) => player.frontPercent)
          .reduce((a, b) => a + b, 0) / playerInfo.length,
      "BA Rate":
        playerInfo
          .map((player) => player.backPercent)
          .reduce((a, b) => a + b, 0) / playerInfo.length,
      "Dmg Taken (Avg)":
        playerInfo
          .map((player) => player.damageTaken)
          .reduce((a, b) => a + b, 0) / playerInfo.length,
      "Deaths / Pull":
        playerInfo.map((player) => player.deaths).reduce((a, b) => a + b, 0) /
        playerInfo.length,
      "Deaths (Total)": playerInfo
        .map((player) => player.deaths)
        .reduce((a, b) => a + b, 0),
      Clears: playerInfo.filter((player) => player.cleared == 1).length,
    };

    return row;
  });

  const supTable = supNames.map((name) => {
    const playerEncs = tableEncounters.filter((enc) =>
      enc.playerInfo.map((player) => player.name).includes(name)
    );

    let playerAllies = [];
    const player = [];
    for (let i = 0; i < playerEncs.length; i++) {
      const playerParty = playerEncs[i].playerInfo.filter(
        (player) => player.name === name
      )[0].party;

      playerAllies.push(
        playerEncs[i].playerInfo.filter(
          (player) => player.party === playerParty && player.name !== name
        )
      );

      player.push(
        playerEncs[i].playerInfo.filter((player) => player.name === name)[0]
      );
    }

    playerAllies = playerAllies.filter((ally) => ally.length > 0);

    const playerClass = player[0].class;
    const playerParty = player[player.length - 1].party;
    const playerDeaths = player
      .map((player) => player.deaths)
      .reduce((a, b) => a + b, 0);
    const playerShielded =
      player.map((player) => player.shielded).reduce((a, b) => a + b, 0) /
      player.length;

    const allyAPUptime =
      playerAllies
        .map(
          (allies) =>
            allies.map((ally) => ally.supAPUptime).reduce((a, b) => a + b, 0) /
            allies.length
        )
        .reduce((a, b) => a + b, 0) / playerAllies.length;

    const allyBrandUptime =
      playerAllies
        .map(
          (allies) =>
            allies
              .map((ally) => ally.supBrandUptime)
              .reduce((a, b) => a + b, 0) / allies.length
        )
        .reduce((a, b) => a + b, 0) / playerAllies.length;

    const allyIdentityUptime =
      playerAllies
        .map(
          (allies) =>
            allies
              .map((ally) => ally.supIdentityUptime)
              .reduce((a, b) => a + b, 0) / allies.length
        )
        .reduce((a, b) => a + b, 0) / playerAllies.length;

    // console.log(playerAllies);

    const row = {
      Name: name,
      Class: playerClass,
      Pulls: player.length,
      "Last Party": playerParty,
      "AP %": allyAPUptime,
      "Brand %": allyBrandUptime,
      "Identity %": allyIdentityUptime,
      "Dmg Shielded (Avg)": playerShielded,
      "Dmg Taken (Avg)":
        player.map((player) => player.damageTaken).reduce((a, b) => a + b, 0) /
        player.length,
      "Deaths / Pull": playerDeaths / player.length,
      "Deaths (Total)": playerDeaths,
      Clears: player.filter((player) => player.cleared == 1).length,
    };

    return row;
  });

  display(
    Inputs.table(dpsTable, {
      select: false,
      sort: "Pulls",
      reverse: true,
      format: {
        "DPS (Avg)": formatMillions,
        "Crit Rate": formatPercent,
        "FA Rate": formatPercent,
        "BA Rate": formatPercent,
        "Dmg Taken (Avg)": formatThousands,
        "Last Party": (x) => x + 1,
      },
    })
  );
  display(html`<p>Supports</p>`);
  display(
    Inputs.table(supTable, {
      select: false,
      sort: "Pulls",
      reverse: true,
      format: {
        "AP %": formatPercent,
        "Brand %": formatPercent,
        "Identity %": formatPercent,
        "Dmg Shielded (Avg)": formatThousands,
        "Dmg Taken (Avg)": formatThousands,
        "Last Party": (x) => x + 1,
      },
    })
  );
}
```

```js
const x1Select = Inputs.select(
  ["DPS (Total)", "Sup. Perf. ", "Bars Complete", "Duration"],
  {
    label: "Top X Data",
    value: "Bars Complete",
  }
);
const x2Select = Inputs.select(
  ["DPS (Total)", "Sup. Perf. ", "Bars Complete", "Duration"],
  {
    label: "Bottom X Data",
    value: "DPS (Total)",
  }
);

const aggStatSelect = Inputs.select(["Average", "Max"], {
  label: "Aggregate Stat",
  value: "Max",
});
const aggWindowSelect = Inputs.select(["Batched", "Rolling Window"], {
  label: "Aggregate Method",
});
const aggWindowRange = Inputs.range([1, 20], {
  label: "Aggregate Window",
  step: 1,
  value: 10,
});

const x1Var = Generators.input(x1Select);
const x2Var = Generators.input(x2Select);
const aggStat = Generators.input(aggStatSelect);
const aggWindowMethod = Generators.input(aggWindowSelect);
const aggWindow = Generators.input(aggWindowRange);
```

**${selectedEncounter ? "Progression Graph" : ""}**

```js figure control div
if (!!selectedEncounter) {
  display(html`<div class="card grid grid-cols-2" style="grid-auto-rows: auto;">
    <div>${x1Select} ${x2Select}</div>
    <div>${aggStatSelect} ${aggWindowSelect} ${aggWindowRange}</div>
  </div>`);
}
```

```js figure aggregate
let figureData;
if (!!selectedEncounter) {
  const figureOrigData = tableSelect.slice();
  figureOrigData.sort((a, b) => a.id - b.id);

  function aggData(logs, column, stat) {
    if (stat == "Average") {
      const nLogs = logs.length;
      return column == "Sup. Perf. "
        ? logs
            .map((d) =>
              d["Sup. Perf. "]
                .split("/")
                .map((d) => Number(d))
                .reduce((a, b) => a + b, 0)
            )
            .reduce((a, b) => a + b, 0) / nLogs
        : logs.map((d) => d[column]).reduce((a, b) => a + b, 0) / nLogs;
    } else if (stat == "Max") {
      return column == "Sup. Perf. "
        ? Math.max(
            ...logs.map((d) =>
              d["Sup. Perf. "]
                .split("/")
                .map((d) => Number(d))
                .reduce((a, b) => a + b, 0)
            )
          )
        : Math.max(...logs.map((d) => d[column]));
    }
  }

  figureData = [];
  let i;
  if (aggWindowMethod == "Batched") {
    const steps = Math.ceil(figureOrigData.length / aggWindow);
    for (i = 0; i < steps; i++) {
      const windowLogs = figureOrigData.slice(
        aggWindow * i,
        aggWindow * (i + 1)
      );
      const nLogs = windowLogs.length;

      const ids = windowLogs.map((d) => d["ID"]);
      const y =
        aggWindow > 1 ? `${ids[0]}-${ids[ids.length - 1]}` : String(ids[0]);

      figureData.push({
        y: y,
        x1: aggData(windowLogs, x1Var, aggStat),
        x2: aggData(windowLogs, x2Var, aggStat),
      });
    }
  } else if (aggWindowMethod == "Rolling Window") {
    let backHalf = Math.floor((aggWindow - 1) / 2);
    let frontHalf = Math.ceil((aggWindow - 1) / 2) + 1;
    for (i = 0; i < figureOrigData.length; i++) {
      const startIdx = i - backHalf < 0 ? 0 : i - backHalf;
      const windowLogs = figureOrigData.slice(startIdx, i + frontHalf);
      const nLogs = windowLogs.length;

      figureData.push({
        y: figureOrigData[i].ID,
        x1: aggData(windowLogs, x1Var, aggStat),
        x2: aggData(windowLogs, x2Var, aggStat),
      });
    }
  }
}
```

```js figure dimensions
let width, plotHeight, margins, xAxisHeight, yAxisWidth, height;
if (!!selectedEncounter) {
  width = Generators.width(document.querySelector("main"));
  plotHeight = figureData.length * 30;
  margins = { top: 10, right: 10, bottom: 10, left: 10 };
  xAxisHeight = 30;
  yAxisWidth = 75;
  height = plotHeight + margins.top + margins.bottom + xAxisHeight * 2;
}
```

```js figure
if (!!selectedEncounter) {
  const x1Max =
    x1Var == "Sup. Perf. " ? 300 : Math.max(...figureData.map((d) => d.x1));
  const x2Max =
    x2Var == "Sup. Perf. " ? 300 : Math.max(...figureData.map((d) => d.x2));

  // Create x-scale based x1/x2
  const x1Scale = d3
    .scaleLinear()
    .domain([0, x1Max])
    .range([0, width - margins.right - yAxisWidth]);
  const x2Scale = d3
    .scaleLinear()
    .domain([0, x2Max])
    .range([0, width - margins.right - yAxisWidth]);

  // Create y-scale based on y
  const yScale = d3
    .scaleBand()
    .domain(figureData.map((d) => d.y))
    .range([margins.top + xAxisHeight, height - margins.bottom - xAxisHeight])
    .paddingInner(0.3)
    .paddingOuter(0.25);

  // Create SVG container
  const svg = d3
    .create("svg")
    .attr("width", width)
    .attr("height", height)
    .style("background", "transparent");

  const fig = svg.append("g");
  const bars = fig
    .selectAll("g")
    .data(figureData)
    .join("g")
    .attr("transform", `translate(${yAxisWidth}, 0)`);

  // Draw a rectangle for each entry of x1
  bars
    .append("rect")
    .attr("x", x1Scale(0))
    .attr("y", (d) => yScale(d.y))
    .attr("width", (d) => x1Scale(d.x1))
    .attr("height", yScale.bandwidth() / 2)
    .attr("fill", "var(--theme-foreground)");

  bars
    .append("rect")
    .attr("x", x1Scale(0))
    .attr("y", (d) => yScale(d.y) + yScale.bandwidth() / 2)
    .attr("width", (d) => x2Scale(d.x2))
    .attr("height", yScale.bandwidth() / 2)
    .attr("fill", "var(--theme-foreground-faint)");

  // Add x-axis
  const xAxisTop = d3.axisTop(x1Scale);
  fig
    .append("g")
    .call(xAxisTop)
    .attr(
      "transform",
      `translate(${yAxisWidth}, ${margins.top + xAxisHeight})`
    );
  fig
    .append("text")
    .attr("x", width / 2)
    .attr("y", margins.top + xAxisHeight - 30)
    .attr("text-anchor", "middle")
    .attr("fill", "var(--theme-foreground)")
    .style("font", "10px/1.6 var(--sans-serif)")
    .text(x1Var);

  const xAxisBot = d3.axisBottom(x2Scale);
  fig
    .append("g")
    .call(xAxisBot)
    .attr(
      "transform",
      `translate(${yAxisWidth}, ${height - margins.bottom - xAxisHeight})`
    );
  fig
    .append("text")
    .attr("x", width / 2)
    .attr("y", height - margins.bottom - xAxisHeight + 35)
    .attr("text-anchor", "middle")
    .attr("fill", "var(--theme-foreground)")
    .style("font", "10px/1.6 var(--sans-serif)")
    .text(x2Var);

  // Add y-axis
  const yAxis = d3.axisLeft(yScale).tickFormat((d) => d);
  fig.append("g").call(yAxis).attr("transform", `translate(${yAxisWidth}, 0)`);
  fig
    .append("text")
    .attr("x", -height / 2)
    .attr("y", margins.left + yAxisWidth - 75)
    .attr("text-anchor", "middle")
    .attr("transform", "rotate(-90)")
    .attr("fill", "var(--theme-foreground)")
    .style("font", "10px/1.6 var(--sans-serif)")
    .text("Log ID");

  display(svg.node());
}
```
