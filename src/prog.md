---
title: Progression Analysis
toc: false
---

<h1>Progression Analysis</h1>
Analyze progression data.

<div class="grid grid-cols-2" style="grid-auto-rows: auto;">
    <div class="card">
      ${fileUpload}
      ${dateStartSelect ? dateStartSelect : ""}
      ${dateEndSelect ? dateEndSelect : ""}
      ${encounterText ? encounterText : ""}
      ${nameTextArea ? nameTextArea : ""}
    </div>
</div>

**${selectedEncounter ? selectedEncounter : ""}**

```js summary div
if (!!selectedEncounter) {
  display(html`<div class="grid grid-cols-3 card" style="grid-auto-rows: auto;">
    <div>
      Pulls: ${encounterInfos.length} (${Math.round(avgPullMin * 10) / 10}m per
      pull)
      <br />
      Total Prog Time: ${progTimeStr}
    </div>
    <div>
      Avg Team DPS: ${Math.round(avgTeamDPS / 100_000) / 10}M
      <br />
      Avg Team Dmg Taken: ${Math.round(avgTeamDmgTaken / 1000)}K (${Math.round(
        avgTeamDPSTaken / 1000
      )}K DPS)
    </div>
    <div>
      Avg Sup. Performance: ${Math.round(avgAPUptime * 100)}/${Math.round(
        avgBrandUptime * 100
      )}/${Math.round(avgIdentityUptime * 100)}
      <br />
      Avg Progress: ${avgBossBarsComplete}/${selectedBossTotalBars} bars
      complete
    </div>
    <div class="grid-colspan-3">
      <b>Best Run —</b> ID: ${bestEncounter.id} - Bars complete: ${bestEncounter.barsComplete}/${selectedBossTotalBars}
      - Duration: ${Math.floor(bestEncounter.duration / 60)}m ${Math.round(
        bestEncounter.duration % 60
      )}s - DPS: ${Math.round(bestEncounter.avgTeamDps / 100000) / 10}M - Dmg Taken:
      ${Math.round(bestEncounter.avgTeamDamageTaken / 1000)}K - Sup. Perf.: ${Math.round(
        bestEncounter.avgAPUptime * 100
      )}/${Math.round(bestEncounter.avgBrandUptime * 100)}/${Math.round(
        bestEncounter.avgIdentityUptime * 100
      )} - Cleared: ${bestEncounter.cleared == 1 ? "Yes" : "No"}
    </div>
  </div> `);
}
```

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

const supportClasses = ["Bard", "Paladin", "Artist"];
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

```js boss info / encounter summaries
let selectedBossNames,
  selectedBossBars,
  selectedBossTotalBars,
  avgPullMin,
  progTime,
  progTimeStr,
  avgTeamDPS,
  avgTeamDmgTaken,
  avgTeamDPSTaken,
  avgAPUptime,
  avgBrandUptime,
  avgIdentityUptime,
  bestEncounter,
  avgBossBarsComplete;

if (!!selectedEncounter) {
  selectedBossNames = encounterDict[selectedEncounter.split(" - ")[0]]["names"];
  selectedBossBars = selectedBossNames.map((name) => hpBarMap[name]);
  selectedBossTotalBars = selectedBossBars
    .filter((bars) => !!bars)
    .reduce((a, b) => a + b, 0);

  avgPullMin =
    encounterInfos.map((enc) => enc.duration).reduce((a, b) => a + b, 0) /
    encounterInfos.length /
    60;

  progTime = encounterInfos
    .map((enc) => enc.duration)
    .reduce((a, b) => a + b, 0);
  progTimeStr = "";
  if (progTime > 60 * 60) {
    progTimeStr = `${Math.floor(progTime / 60 / 60)}h `;
    progTime %= 60 * 60;
  }
  progTimeStr += `${Math.floor(progTime / 60)}m ${Math.round(progTime % 60)}s`;

  avgTeamDPS =
    encounterInfos.map((enc) => enc.avgTeamDps).reduce((a, b) => a + b, 0) /
    encounterInfos.length;

  avgTeamDmgTaken =
    encounterInfos
      .map((enc) => enc.avgTeamDamageTaken)
      .reduce((a, b) => a + b, 0) / encounterInfos.length;
  avgTeamDPSTaken =
    encounterInfos
      .map((enc) => enc.avgTeamDPSTaken)
      .reduce((a, b) => a + b, 0) / encounterInfos.length;

  avgAPUptime =
    encounterInfos.map((enc) => enc.avgAPUptime).reduce((a, b) => a + b, 0) /
    encounterInfos.length;
  avgBrandUptime =
    encounterInfos.map((enc) => enc.avgBrandUptime).reduce((a, b) => a + b, 0) /
    encounterInfos.length;
  avgIdentityUptime =
    encounterInfos
      .map((enc) => enc.avgIdentityUptime)
      .reduce((a, b) => a + b, 0) / encounterInfos.length;

  bestEncounter = encounterInfos.reduce((a, b) =>
    a.barsComplete > b.barsComplete ? a : b
  );

  avgBossBarsComplete = Math.round(
    encounterInfos.map((enc) => enc.barsComplete).reduce((a, b) => a + b, 0) /
      encounterInfos.length
  );

  display(bestEncounter);
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

    const realDeath = encounterEnd - damageInfo["deathTime"] > 500;

    playerInfo.push({
      name: entity["name"],
      class: entity["class"],
      isSupport: supportClasses.includes(entity["class"]),
      party: Number(
        partyNumbers.filter((num) => partyInfo[num].includes(entity["name"]))[0]
      ),
      dps: damageInfo["dps"],
      supAPUptime: damageInfo["buffedBySupport"] / damageInfo["damageDealt"],
      supBrandUptime:
        damageInfo["debuffedBySupport"] / damageInfo["damageDealt"],
      supIdentityUptime:
        damageInfo["buffedByIdentity"] / damageInfo["damageDealt"],
      critPercent: damageInfo["critDamage"] / damageInfo["damageDealt"],
      frontPercent: damageInfo["frontAttackDamage"] / damageInfo["damageDealt"],
      backPercent: damageInfo["backAttackDamage"] / damageInfo["damageDealt"],
      damageTaken: damageInfo["damageTaken"],
      deaths: realDeath ? damageInfo["deaths"] : damageInfo["deaths"] - 1,
      deathTime: realDeath ? damageInfo["deathTime"] : 0,
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
    playerInfo
      .filter((player) => !player.isSupport)
      .map((player) => player.supAPUptime)
      .reduce((a, b) => a + b, 0) / nDPS;
  const avgBrandUptime =
    playerInfo
      .filter((player) => !player.isSupport)
      .map((player) => player.supBrandUptime)
      .reduce((a, b) => a + b, 0) / nDPS;
  const avgIdentityUptime =
    playerInfo
      .filter((player) => !player.isSupport)
      .map((player) => player.supIdentityUptime)
      .reduce((a, b) => a + b, 0) / nDPS;

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
if (!!filteredIDs) {
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
}

display(encounterInfos);
```

**Pulls**

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

const subBossFormat = {};
const subBossWidths = {};
let encounterTable;
if (!!selectedEncounter) {
  for (let i = 0; i < selectedBossNames.length; i++) {
    subBossFormat[selectedBossNames[i]] = sparkbar(selectedBossBars[i]);
    subBossWidths[selectedBossNames[i]] = 100;
  }

  encounterTable = encounterInfos.map((enc) => {
    const row = {
      ID: enc.id.toString(),
      "Bars Complete": enc.barsComplete,
      Duration: `${Math.floor(enc.duration / 60)}m ${Math.round(
        enc.duration % 60
      )}s`,
      DPS: `${Math.round(enc.avgTeamDps / 100000) / 10}M`,
      "Dmg Taken": `${Math.round(enc.avgTeamDamageTaken / 1000)}K`,
      "DPS Taken": `${Math.round(enc.avgTeamDPSTaken / 1000)}K`,
      "Sup. Perf.": `${Math.round(enc.avgAPUptime * 100)}/${Math.round(
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

  display(
    Inputs.table(encounterTable, {
      select: false,
      format: subBossFormat,
      width: subBossWidths,
      layout: "auto",
    })
  );
}
```

**Player Summaries**

```js player table
const dpsNames = encounterInfos
  .map((enc) =>
    enc.playerInfo
      .filter((player) => !supportClasses.includes(player["class"]))
      .map((player) => player.name)
  )
  .flat()
  .filter((name, i, arr) => arr.indexOf(name) === i);
const supNames = encounterInfos
  .map((enc) =>
    enc.playerInfo
      .filter((player) => supportClasses.includes(player["class"]))
      .map((player) => player.name)
  )
  .flat()
  .filter((name, i, arr) => arr.indexOf(name) === i);

const dpsTable = dpsNames.map((name) => {
  const playerInfo = encounterInfos
    .map((enc) => enc.playerInfo.filter((player) => player.name === name))
    .flat();

  const row = {
    Name: name,
    Class: playerInfo[0].class,
    "Last Party": playerInfo[playerInfo.length - 1].party,
    DPS:
      playerInfo.map((player) => player.dps).reduce((a, b) => a + b, 0) /
      playerInfo.length,
    "Crit Rate":
      playerInfo
        .map((player) => player.critPercent)
        .reduce((a, b) => a + b, 0) / playerInfo.length,
    "Front Attack":
      playerInfo
        .map((player) => player.frontPercent)
        .reduce((a, b) => a + b, 0) / playerInfo.length,
    "Back Attack":
      playerInfo
        .map((player) => player.backPercent)
        .reduce((a, b) => a + b, 0) / playerInfo.length,
    "Dmg Taken":
      playerInfo
        .map((player) => player.damageTaken)
        .reduce((a, b) => a + b, 0) / playerInfo.length,
    Deaths: playerInfo
      .map((player) => player.deaths)
      .reduce((a, b) => a + b, 0),
    Pulls: playerInfo.length,
  };

  return row;
});

const supTable = supNames.map((name) => {
  const playerEncs = encounterInfos.filter((enc) =>
    enc.playerInfo.map((player) => player.name).includes(name)
  );

  const playerAllies = [];
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

  const playerClass = player[0].class;
  const playerParty = player[player.length - 1].party;
  const playerDeaths = player
    .map((player) => player.deaths)
    .reduce((a, b) => a + b, 0);

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
          allies.map((ally) => ally.supBrandUptime).reduce((a, b) => a + b, 0) /
          allies.length
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

  const row = {
    Name: name,
    Class: playerClass,
    "Last Party": playerParty,
    "AP %": allyAPUptime,
    "Brand %": allyBrandUptime,
    "Identity %": allyIdentityUptime,
    "Dmg Taken":
      player.map((player) => player.damageTaken).reduce((a, b) => a + b, 0) /
      player.length,
    Deaths: playerDeaths,
    Pulls: player.length,
  };

  return row;
});

function formatPercent(x) {
  return Math.round(x * 1000) / 10 + "%";
}
display(
  Inputs.table(dpsTable, {
    select: false,
    sort: "Pulls",
    reverse: true,
    format: {
      DPS: (x) => Math.round(x / 100_000) / 10 + "M",
      "Crit Rate": formatPercent,
      "Front Attack": formatPercent,
      "Back Attack": formatPercent,
      "Dmg Taken": (x) => Math.round(x / 1000) + "K",
    },
  })
);
display(html`<hr />`);
display(
  Inputs.table(supTable, {
    select: false,
    sort: "Pulls",
    reverse: true,
    format: {
      "AP %": formatPercent,
      "Brand %": formatPercent,
      "Identity %": formatPercent,
      "Dmg Taken": (x) => Math.round(x / 1000) + "K",
    },
  })
);
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
