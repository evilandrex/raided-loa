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
    <div>
        Load your encounters.db to show analysis tools. This file can be found 
        in your database folder (e.g., C:\Users\[USER]\AppData\Local\LOA Logs). 
        You can also get to this folder from your settings of LOA Logs in the 
        database page.
    </div>
</div>

**${selectedEncounter ? selectedEncounter : ""}**

```js summary div
if (!!selectedEncounter) {
  display(html`<div class="grid grid-cols-3 card" style="grid-auto-rows: auto;">
    <div>
      Pulls: ${encounterInfos.length} (${formatDuration(avgPullDuration)} per
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
  totalDuration,
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
  selectedBossNames = encounterDict[selectedEncounter.split(" - ")[0]]["names"];
  selectedBossBars = selectedBossNames.map((name) => hpBarMap[name]);
  selectedBossTotalBars = selectedBossBars
    .filter((bars) => !!bars)
    .reduce((a, b) => a + b, 0);

  totalDuration = encounterInfos
    .map((enc) => enc.duration)
    .reduce((a, b) => a + b, 0);
  avgPullDuration = totalDuration / encounterInfos.length;

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

  // display(bestEncounter);
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

// display(encounterInfos);
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
  DPS: formatMillions,
  "Dmg Taken": formatThousands,
  "DPS Taken": formatThousands,
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
      ID: enc.id.toString(),
      "Bars Complete": enc.barsComplete,
      Duration: enc.duration,
      DPS: enc.avgTeamDps,
      "Dmg Taken": enc.avgTeamDamageTaken,
      "DPS Taken": enc.avgTeamDPSTaken,
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

  tableSelect = view(
    Inputs.table(encounterTable, {
      value: encounterTable,
      format: subBossFormat,
      width: subBossWidths,
      layout: "auto",
    })
  );
}
```

**${selectedEncounter ? "Player Summaries" : ""}**

```js player table
if (!!selectedEncounter) {
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

  display(
    Inputs.table(dpsTable, {
      select: false,
      sort: "Pulls",
      reverse: true,
      format: {
        DPS: formatMillions,
        "Crit Rate": formatPercent,
        "Front Attack": formatPercent,
        "Back Attack": formatPercent,
        "Dmg Taken": formatThousands,
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
        "Dmg Taken": formatThousands,
      },
    })
  );
}
```

<!-- # Dev preview

```js prog line plot dimensions
const width = Generators.width(document.querySelector("main"));
const plotHeight = tableSelect.length * 40;
const margins = { top: 10, right: 10, bottom: 10, left: 10 };
const xAxisHeight = 30;
const yAxisWidth = 50;
const height = plotHeight + margins.top + margins.bottom + xAxisHeight;
```

```js prog line plot
console.log(tableSelect);
// Create x-scale based on bars
const xScale = d3
  .scaleLinear()
  .domain([0, selectedBossTotalBars])
  .range([margins.left + yAxisWidth, width - margins.right]);

// Create y-scale based on encounters
const yScale = d3
  .scaleBand()
  .domain(tableSelect.map((d) => d.ID))
  .range([margins.top + xAxisHeight, height - margins.bottom])
  .paddingInner(0.3)
  .paddingOuter(0.25);

// Create SVG container
const svg = d3
  .create("svg")
  .attr("width", width)
  .attr("height", height)
  .style("background", "transparent");

const g = svg.append("g").selectAll("g").data(tableSelect).join("g");

// Add a rectangle for each encounter for each boss
// console.log(selectedBossNames.length);
for (let i = selectedBossNames.length - 1; i >= 0; i--) {
  const previousBosses = selectedBossNames.slice(0, i);
  // console.log(i);

  const bossBars = g
    .append("g")
    .attr("visibility", (d) => {
      return typeof d[selectedBossNames[i]] !== "undefined" &&
        d[selectedBossNames[i]] !== 0
        ? "visible"
        : "hidden";
    })
    .attr("transform", (d) => {
      const previousBarX = previousBosses
        .map((boss) => d[boss])
        .filter((x) => x)
        .reduce((a, b) => a + b, 0);
      return `translate(${xScale(previousBarX)}, 0)`;
    })
    .attr("id", selectedBossNames[i]);

  bossBars
    .append("rect")
    .attr("x", 0)
    .attr("y", (d) => yScale(d.ID))
    .attr("width", (d) => {
      return xScale(d[selectedBossNames[i]]) - xScale(0);
    })
    // .attr("width", 20)
    .attr("height", yScale.bandwidth())
    .attr("fill", "var(--theme-foreground-faintest)")
    .attr("stroke", "var(--theme-foreground)");

  bossBars
    .append("text")
    .attr("x", 2)
    .attr("y", (d) => yScale(d.ID) + yScale.bandwidth() - 6)
    .attr("dy", "0.35em")
    .attr("fill", "var(--theme-foreground)")
    .style("font", "10px/1.6 var(--sans-serif)")
    .text((d) => `${d[selectedBossNames[i]]} - ${selectedBossNames[i]}`);
}

// Draw an extra rectangle at the end to fill in the rest
g.append("rect")
  .attr("x", (d) => {
    const previousBarX = selectedBossNames
      .map((boss) => d[boss])
      .filter((x) => x)
      .reduce((a, b) => a + b, 0);
    return xScale(previousBarX);
  })
  .attr("y", (d) => yScale(d.ID))
  .attr("width", (d) => {
    return xScale(selectedBossTotalBars) - xScale(0);
  })
  .attr("height", yScale.bandwidth())
  .attr("fill", "var(--theme-background)");

// Add x-axis
const xAxis = d3.axisTop(xScale).tickFormat((d) => d + 1);
svg
  .append("g")
  .call(xAxis)
  .attr("transform", `translate(0, ${margins.top + xAxisHeight})`);
svg
  .append("text")
  .attr("x", width / 2)
  .attr("y", margins.top + xAxisHeight - 30)
  .attr("text-anchor", "middle")
  .attr("fill", "var(--theme-foreground)")
  .style("font", "10px/1.6 var(--sans-serif)")
  .text("Bars Remaining");

// Add y-axis
const yAxis = d3.axisLeft(yScale).tickFormat((d) => d);
svg.append("g").call(yAxis).attr("transform", `translate(${yAxisWidth}, 0)`);
svg
  .append("text")
  .attr("x", -height / 2)
  .attr("y", margins.left + yAxisWidth - 50)
  .attr("text-anchor", "middle")
  .attr("transform", "rotate(-90)")
  .attr("fill", "var(--theme-foreground)")
  .style("font", "10px/1.6 var(--sans-serif)")
  .text("Log ID");

display(svg.node());
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
``` -->
