---
title: Raided Lost Ark
toc: false
---

<h1>Raided Lost Ark</h1>

<div class="warning">First pass data collection is ongoing. Data collection 
is going backwards starting from Aegir (Aegir should be up to date). If 
little/no data is available for a given encounter, it is likely because the data 
has not been collected yet. This dataset will focus on Ark Passive T4 content. 
Give your thanks to Snow for providing this data!
</div>

<div class="grid grid-cols-2" style="grid-auto-rows: auto;">
    <div class="card">
      <h1>Select a fight</h1>
      ${bossSelect}
      ${difficultyRadio}
      ${gateRadio}
      <br/>
      <details>
        <summary>Advanced Options</summary>
        Sort By
        ${sortSelect}
        <br/>
        ${dateStartSelect}
        ${dateEndSelect}
        Preset Patch
        ${patchSelect}
        <br/>
        Item Level Range
        ${iLevelMinRange}
        ${iLevelMaxRange}
        <br/>
        Duration Range (seconds)
        ${durationMinRange}
        ${durationMaxRange}
        <br/>
        ${filterArkToggle}
        ${unknownSpecToggle}
        ${filterDeadToggle}
        ${filterWeirdToggle}
        <sub>Princcess GL, weird support count, weird player count</sub>
        <br/>
        <br/>
        ${starToggle}
      </details>
    </div>
    <div>
      <details>
        <summary>Info</summary>
        Default advanced options are intended to show relevant logs from 
        characters at the right ilevel to do that content (not overleveled). You
        can click the stars to see the best log for each build. You can filter
        the builds shown in the chart using the class statistics table. Data
        is updated nightly.
      </details>
    </div>
</div>

```js queryString processor
const urlParams = new URLSearchParams(window.location.search);
```

```js boss selector
const guardians = ["Argeos"];

const raids = {
  Echidna: [1, 2],
  Behemoth: [1, 2],
  Aegir: [1, 2],
};
let bosses = [null, ...guardians, ...Object.keys(raids)];

const bossSelect = Inputs.select(bosses, {
  value: urlParams.get("boss"),
  label: "Boss",
});
const selectedBoss = Generators.input(bossSelect);
```

```js difficulty radio
const reqDiff =
  guardians.includes(selectedBoss) ||
  selectedBoss == "Behemoth" ||
  selectedBoss === null;

const diffValue = urlParams.get("difficulty")
  ? urlParams.get("difficulty")
  : selectedBoss == "Thaemine"
  ? "Hard"
  : selectedBoss == "Behemoth"
  ? "Normal"
  : reqDiff
  ? null
  : "Normal";

const difficulties = Object.keys(raids).includes(selectedBoss)
  ? ["Normal", "Hard"]
  : [];

const difficultyRadio = Inputs.radio(difficulties, {
  value: diffValue,
  label: "Difficulty",
  disabled: reqDiff,
});
const difficulty = Generators.input(difficultyRadio);
```

```js gates radio
const gates = Object.keys(raids).includes(selectedBoss)
  ? raids[selectedBoss]
  : [];
const gateRadio = Inputs.radio(gates, {
  value: urlParams.get("gate")
    ? Number(urlParams.get("gate"))
    : gates.length <= 1
    ? null
    : gates[0],
  label: "Gate",
  disabled: gates.length === 1,
});
const gate = Generators.input(gateRadio);
```

```js sort selector
const sortSelect = Inputs.select(
  new Map([
    ["Median (middle performance)", "Median"],
    ["Mean (alternate middle, good for small samples)", "Mean"],
    ["Upper (reasonable ceiling)", "Upper"],
    ["Lower (reasonable floor)", "Lower"],
    ["Max (the best!)", "Max"],
  ]),
  {
    value: urlParams.get("sort") ? urlParams.get("sort") : "Median",
    label: "",
  }
);
const selectedSort = Generators.input(sortSelect);
```

```js patch selector
const patches = new Map([
  ["October 2024 - T4 Release", [new Date(`2024-10-9`), Date.now()]],
]);

const patchSelect = Inputs.select(patches, {
  label: "",
});
const selectedPatch = Generators.input(patchSelect);
```

```js date selectors
const dateStartSelect = Inputs.date({
  label: "Start Date",
  value: urlParams.get("dateStart")
    ? Number(urlParams.get("dateStart"))
    : selectedPatch[0],
});
const dateStart = Generators.input(dateStartSelect);

const dateEndSelect = Inputs.date({
  label: "End Date",
  value: urlParams.get("dateEnd")
    ? Number(urlParams.get("dateEnd"))
    : selectedPatch[1],
});
const dateEnd = Generators.input(dateEndSelect);
```

```js ilevel ranges
const bossIlevelDefaults = {
  Argeos: [1640, 1750],
  Echidna: { Hard: [1630, 1750] },
  Behemoth: { Normal: [1620, 1750] },
  Aegir: { Normal: [1660, 1679], Hard: [1680, 1750] },
};

const iLevelDefaults = bossIlevelDefaults[selectedBoss]
  ? bossIlevelDefaults[selectedBoss][difficulty]
    ? bossIlevelDefaults[selectedBoss][difficulty]
    : bossIlevelDefaults[selectedBoss]
  : [1580, 1750];
const iLevelMinRange = Inputs.range([1580, 1750], {
  value: urlParams.get("iLevelMin")
    ? Number(urlParams.get("iLevelMin"))
    : iLevelDefaults[0],
  step: 1,
});
const iLevelMin = Generators.input(iLevelMinRange);

const iLevelMaxRange = Inputs.range([1580, 1750], {
  value: urlParams.get("iLevelMax")
    ? Number(urlParams.get("iLevelMax"))
    : iLevelDefaults[1],
  step: 1,
});
const iLevelMax = Generators.input(iLevelMaxRange);
```

```js duration ranges
const durationMinRange = Inputs.range([0, 3600], {
  value: urlParams.get("durationMin")
    ? Number(urlParams.get("durationMin"))
    : 60,
  step: 1,
});
const durationMin = Generators.input(durationMinRange);

const durationMaxRange = Inputs.range([0, 3600], {
  value: urlParams.get("durationMax")
    ? Number(urlParams.get("durationMax"))
    : 3600,
  step: 1,
});
const durationMax = Generators.input(durationMaxRange);
```

```js ark passive toggle
const filterArkToggle = Inputs.toggle({
  label: "Only Ark Passives",
  value: urlParams.get("filterArk")
    ? !urlParams.get("filterArk") === "false"
    : true,
});
const filterArk = Generators.input(filterArkToggle);
```

```js unknown spec toggle
const unknownSpecToggle = Inputs.toggle({
  label: "Include unknown specs",
  value: urlParams.get("hasSpec")
    ? !urlParams.get("hasSpec") === "false"
    : true,
});
const unknownSpec = Generators.input(unknownSpecToggle);
```

```js weird toggle
const filterWeirdToggle = Inputs.toggle({
  label: "Filter Weird",
  value: urlParams.get("filterWeird")
    ? !urlParams.get("filterWeird") === "false"
    : true,
});
const filterWeird = Generators.input(filterWeirdToggle);
```

```js dead toggle
const filterDeadToggle = Inputs.toggle({
  label: "Filter Dead",
  value: urlParams.get("filterDead")
    ? !urlParams.get("filterDead") === "false"
    : true,
});
const filterDead = Generators.input(filterDeadToggle);
```

```js star toggle
const starToggle = Inputs.toggle({
  label: "Show Best Logs",
  value: urlParams.get("showStars")
    ? !urlParams.get("showStars") === "false"
    : true,
});
const showStars = Generators.input(starToggle);
```

```js query string maker
let queryUrl = "https://raided.pro/loa-logs?";

// If a boss is selected
if (selectedBoss) {
  queryUrl += `boss=${selectedBoss}`;
  if (difficulty) {
    queryUrl += `&difficulty=${difficulty}`;
  }
  if (gate) {
    queryUrl += `&gate=${gate}`;
  }
}

// Add sort if not default
if (selectedSort !== "Median") {
  queryUrl += `&sort=${selectedSort}`;
}

// Add date if not default
const defaultPatch = patches.values().next();
if (
  Math.abs(dateStart.getTime() - patches.values().next().value[0].getTime()) >
  1000
) {
  queryUrl += `&dateStart=${dateStart.getTime()}`;
}

// Truncate the end date to just today
let today = new Date(patches.values().next().value[1]);
today.setHours(0, 0, 0, 0);

if (Math.abs(dateEnd.getTime() - today.getTime()) > 18000000) {
  queryUrl += `&dateEnd=${dateEnd.getTime()}`;
}

// Add ilevel range if not default
if (iLevelMin !== iLevelDefaults[0]) {
  queryUrl += `&iLevelMin=${iLevelMin}`;
}

if (iLevelMax !== iLevelDefaults[1]) {
  queryUrl += `&iLevelMax=${iLevelMax}`;
}

// Add weird toggle flag if not default
if (!filterWeird) {
  queryUrl += `&filterWeird=${filterWeird}`;
}

// Add dead toggle flag if not default
if (!filterDead) {
  queryUrl += `&filterDead=${filterDead}`;
}

// Add duration range if not default
if (durationMin !== 60) {
  queryUrl += `&durationMin=${durationMin}`;
}

if (durationMax !== 3600) {
  queryUrl += `&durationMax=${durationMax}`;
}

// Add star toggle flag if not default
if (!showStars) {
  queryUrl += `&showStars=${showStars}`;
}
```

```js get data
const supportClasses = [
  "Blessed Aura",
  "Full Bloom",
  "Desperate Salvation",
  "Princess",
];
let url =
  "https://raw.githubusercontent.com/evilandrex/raided-loa-scraper/main/data/";

// Check if boss is a guardian
if (selectedBoss == null) {
  url += "empty.parquet";
} else if (guardians.includes(selectedBoss)) {
  url += `${selectedBoss}.parquet`;
} else {
  url += `${selectedBoss}_G${gate}_${difficulty}.parquet`;
}

// Load data from github
const db = await DuckDBClient.of();
await db.sql`CREATE TABLE logs
  AS SELECT *
  FROM read_parquet(${url})`;

let data;
let filter;
if (selectedBoss != null) {
  // Add extra day to make sure we actually get everything
  const dateEndExtra = new Date(dateEnd);
  dateEndExtra.setDate(dateEndExtra.getDate() + 1);

  // Turn dates into numbers
  let startTimestamp = dateStart.getTime();
  let endTimestamp = dateEndExtra.getTime();

  filter = `WHERE timestamp >= ${startTimestamp} and timestamp <= ${endTimestamp} AND
    ${unknownSpec ? "" : "hasSpec = true AND"} 
    ${filterWeird ? "weird = false AND" : ""}
    ${filterDead ? "isDead = false AND" : ""}
    ${filterArk ? "arkPassiveActive = true AND" : ""}
    gearscore >= ${iLevelMin} AND gearscore <= ${iLevelMax} AND
    duration >= ${durationMin * 1000} AND duration <= ${durationMax * 1000} AND
    spec NOT IN (${supportClasses.map((d) => `'${d}'`).join(", ")})`;
}
```

```js log statistics
let latestLog;
let nLogs;
if (selectedBoss) {
  // Get unique IDs
  nLogs = await db.query(
    `SELECT COUNT(DISTINCT id) AS nLogs FROM logs ${filter}`
  );
  nLogs = nLogs.toArray()[0].nLogs;

  latestLog = await db.query(
    `SELECT MAX(timestamp) AS latest FROM logs ${filter}`
  );
  latestLog = new Date(latestLog.toArray()[0].latest);
}
```

```js plot dimensions
const width = Generators.width(document.querySelector("main"));
const plotHeight = 850;
const margins = { top: 10, right: 10, bottom: 10, left: 10 };
const xAxisHeight = 50;
const yAxisWidth = 250;
const minWidth = 550;
const height = plotHeight + margins.top + margins.bottom + xAxisHeight;
```

```js class colors
const classSpecs = [
  ["Mayhem", "Berserker Technique"],
  ["Rage Hammer", "Gravity Training"],
  ["Combat Readiness", "Lone Knight"],
  ["Blessed Aura", "Judgement", "Judgment"],
  ["Predator", "Punisher"],
  ["Order of the Emperor", "Grace of the Empress"],
  ["Master Summoner", "Communication Overflow"],
  ["Desperate Salvation", "True Courage"],
  ["Igniter", "Reflux"],
  ["Pinnacle", "Control"],
  ["Esoteric Skill Enhancement", "First Intention"],
  ["Ultimate Skill: Taijutsu", "Shock Training"],
  ["Energy Overflow", "Robust Spirit"],
  ["Deathblow", "Esoteric Flurry"],
  ["Asura's Path", "Brawl King Storm"],
  ["Surge", "Remaining Energy"],
  ["Demonic Impulse", "Perfect Suppression"],
  ["Lunar Voice", "Hunger"],
  ["Night's Edge", "Full Moon Harvester"],
  ["Death Strike", "Loyal Companion"],
  ["Enhanced Weapon", "Pistoleer"],
  ["Barrage Enhancement", "Firepower Enhancement"],
  ["Evolutionary Legacy", "Arthetinean Skill"],
  ["Peacemaker", "Time to Hunt"],
  ["Recurrence", "Full Bloom"],
  ["Wind Fury", "Drizzle"],
];

// Create a colorscale
const colorScale = d3
  .scaleOrdinal([
    "#ff7ba7",
    "#ae5751",
    "#ff7a59",
    "#ff4b17",
    "#ad5a23",
    "#ff8533",
    "#e58100",
    "#c88f00",
    "#836f1a",
    "#ab9b00",
    "#c0b34c",
    "#aeb682",
    "#11ab00",
    "#318033",
    "#6fc379",
    "#4d7a65",
    "#a5b4b6",
    "#3d7892",
    "#86b6e4",
    "#3873b2",
    "#5d63da",
    "#ac4dee",
    "#8c5ea6",
    "#dc95fd",
    "#fe4de7",
    "#746f72",
  ])
  .domain([0, classSpecs.length]);

// Map each class to a color, making its second spec slightly more saturated
const classColors = new Map(
  classSpecs
    .map((spec, i) => [spec[0], d3.rgb(colorScale(i))])
    .concat(classSpecs.map((spec, i) => [spec[1], d3.rgb(colorScale(i))]))
);
```

```js boxplot
// Create x-scale (based on dps)
const maxCol = showStars ? "Max" : "Upper";
const xLeft = width > minWidth ? yAxisWidth + margins.left : margins.left;
const xScale = d3
  .scaleLinear()
  .domain([0, d3.max(classData.toArray().map((d) => d[maxCol]))])
  .range([xLeft, width - margins.right]);

// Create y-scale (categorical for each class)
const yScale = d3
  .scaleBand()
  .domain(classData.toArray().map((d) => d.BuildAndCount))
  .range([margins.top, height - margins.bottom - xAxisHeight])
  .padding(0.2);

// Create SVG container
const svg = d3
  .create("svg")
  .attr("width", width)
  .attr("height", height)
  .style("background", "transparent");

if (selectedBoss) {

const g = svg.append("g").selectAll("g").data(classData.toArray()).join("g");

// Add main box
g.append("rect")
  .attr("x", (d) => {
    return xScale(d.Q1);
  })
  .attr("y", (d) => yScale(d.BuildAndCount))
  .attr("width", (d) => xScale(d.Q3) - xScale(d.Q1))
  .attr("height", yScale.bandwidth())
  .attr("fill", (d) => classColors.get(d.spec.split(" (")[0]));

// Add median line
g.append("line")
  .attr("x1", (d) => xScale(d.Median))
  .attr("x2", (d) => xScale(d.Median))
  .attr("y1", (d) => yScale(d.BuildAndCount))
  .attr("y2", (d) => yScale(d.BuildAndCount) + yScale.bandwidth())
  .attr("stroke", "white");

// Add mean dot
g.append("circle")
  .attr("cx", (d) => xScale(d.Mean))
  .attr("cy", (d) => yScale(d.BuildAndCount) + yScale.bandwidth() / 2)
  .attr("r", 3)
  .attr("fill", "white");

// Add lower whisker
g.append("line")
  .attr("x1", (d) => xScale(d.Lower))
  .attr("x2", (d) => xScale(d.Q1))
  .attr("y1", (d) => yScale(d.BuildAndCount) + yScale.bandwidth() / 2)
  .attr("y2", (d) => yScale(d.BuildAndCount) + yScale.bandwidth() / 2)
  .attr("stroke", "var(--theme-foreground)");

// Add whisker cap
g.append("line")
  .attr("x1", (d) => xScale(d.Lower))
  .attr("x2", (d) => xScale(d.Lower))
  .attr("y1", (d) => yScale(d.BuildAndCount) + yScale.bandwidth() / 4)
  .attr("y2", (d) => yScale(d.BuildAndCount) + (yScale.bandwidth() * 3) / 4)
  .attr("stroke", "var(--theme-foreground)");

// Add upper whisker
g.append("line")
  .attr("x1", (d) => xScale(d.Q3))
  .attr("x2", (d) => xScale(d.Upper))
  .attr("y1", (d) => yScale(d.BuildAndCount) + yScale.bandwidth() / 2)
  .attr("y2", (d) => yScale(d.BuildAndCount) + yScale.bandwidth() / 2)
  .attr("stroke", "var(--theme-foreground)");

// Add whisker cap
g.append("line")
  .attr("x1", (d) => xScale(d.Upper))
  .attr("x2", (d) => xScale(d.Upper))
  .attr("y1", (d) => yScale(d.BuildAndCount) + yScale.bandwidth() / 4)
  .attr("y2", (d) => yScale(d.BuildAndCount) + (yScale.bandwidth() * 3) / 4)
  .attr("stroke", "var(--theme-foreground)");

// Create x-axis
const xAxis = d3.axisBottom(xScale).ticks(10, "s");
svg
  .append("g")
  .attr("transform", `translate(0, ${height - margins.bottom - xAxisHeight})`)
  .call(xAxis);

// Add x-axis label
svg
  .append("text")
  .attr(
    "transform",
    `translate(${
      width > minWidth ? (width - yAxisWidth) / 2 + yAxisWidth : width / 2
    }, ${height - margins.bottom - xAxisHeight / 2})`
  )
  .attr("dy", "1em")
  .attr("text-anchor", "middle")
  .attr("font-size", "16px")
  .attr("font-family", "var(--sans-serif)")
  .attr("fill", "var(--theme-foreground)")
  .text("DPS (millions)");

// Create y-axis
const yAxis = d3.axisLeft(yScale);
svg
  .append("g")
  .attr("visibility", width > minWidth ? "visible" : "hidden")
  .attr("transform", `translate(${margins.left + yAxisWidth}, 0)`)
  .attr("pointer-events", "none")
  .call(yAxis)
  .selectAll("text")
  .attr("font-size", "14px")
  .attr("visibility", "visible")
  .attr("opacity", width > minWidth ? 1 : 0.25)
  .attr("text-anchor", width > minWidth ? "end" : "start")
  .attr("transform", width > minWidth ? "" : `translate(${-yAxisWidth}, 0)`)
  .text((d) => (width > minWidth ? d : d.split(" (")[0]));

// Add y axis label
svg
  .append("text")
  .attr("visibility", width > minWidth ? "visible" : "hidden")
  .attr(
    "transform",
    `translate(${margins.left}, ${plotHeight / 2}) rotate(-90.1)`
  )
  .attr("dy", "1em")
  .attr("text-anchor", "middle")
  .attr("font-size", "16px")
  .attr("fill", "var(--theme-foreground)")
  .attr("font-family", "var(--sans-serif)")
  .text("Build (Logs)");

// Add branding at the bottom right
let brandString = `Raided.pro Lost Ark - ${new Date().toLocaleDateString()} - ${selectedBoss}`;
if (difficulty) {
  brandString += ` - ${difficulty[0]}M - G${gate}`;
}
// Add ilevel
brandString += ` - ${iLevelMin}-${iLevelMax}`;
svg
  .append("text")
  .attr(
    "transform",
    `translate(${width > minWidth ? yAxisWidth + 25 : width - margins.left}, ${
      height - xAxisHeight - margins.bottom - 5
    }) rotate(-90.1)`
  )
  .attr("text-anchor", "start")
  .attr("font-family", "var(--sans-serif)")
  .attr("font-size", "12px")
  .attr("fill", "var(--theme-foreground-faintest)")
  .attr("pointer-events", "none")
  .text(brandString);

// Prepare tooltip
const tooltip = d3
  .select("main")
  .append("div")
  .attr("class", "tooltip")
  .style("position", "absolute")
  .style("opacity", 0);

// Draw vertical line following mouse
svg
  .append("rect")
  .attr("class", "mouseLine")
  .attr("fill", "black")
  .attr("pointer-events", "none");

// Add invisible box to support mouse over
g.append("rect")
  .attr("class", "rowMouseBox")
  .attr("x", (d) => xScale.range()[0] - yAxisWidth + 25)
  .attr("y", (d) => yScale(d.BuildAndCount))
  .attr("width", (d) => xScale.range()[1] - xScale.range()[0] + yAxisWidth - 25)
  .attr("height", yScale.bandwidth())
  .attr("fill", "transparent")
  .on("mouseover", (event, d) => {
    tooltip.style("opacity", 1).html(`
      <div class="card" style="padding: 7px;">
        <div>Rank ${
          classData
            .toArray()
            .map((x) => x.spec)
            .indexOf(d.spec) + 1
        }/${classData.toArray().length}</div>
        <div>${d.spec}</div>
        <div>${d.Logs} logs</div>
        <br/>
        <div>Worst: ${d3.format(".3s")(d.Min)}</div>
        <div>Floor: ${d3.format(".3s")(d.Lower)}</div>
        <div>Q1: ${d3.format(".3s")(d.Q1)}</div>
        <div>Median: ${d3.format(".3s")(d.Median)}</div>
        <div>Mean: ${d3.format(".3s")(d.Mean)}</div>
        <div>Q3: ${d3.format(".3s")(d.Q3)}</div>
        <div>Ceiling: ${d3.format(".3s")(d.Upper)}</div>
        <div>Best: ${d3.format(".3s")(d.Max)}</div>
      </div>
    `);
    // Darken row
    d3.select(event.target)
      .attr("fill", "var(--theme-foreground-muted)")
      .attr("opacity", "0.25");

    // Change mouse
    d3.select(this).style("cursor", "pointer");

    // Keep updating line
    svg.selectAll(".mouseLine").attr("visibility", "visible");
  })
  .on("mouseout", () => {
    d3.selectAll(".tooltip").attr("opacity", 0).style("left", "-9999px");

    // Lighten row
    g.selectAll(".rowMouseBox").attr("fill", "transparent");
  })
  .on("mousemove", (event) => {
    if (event.offsetX > width / 2) {
      tooltip.style("left", event.offsetX - 140 + "px");
    } else {
      tooltip.style("left", event.offsetX + 30 + "px");
    }

    tooltip.style("top", event.pageY - 30 + "px");
  });

g.append("path")
  .attr("d", d3.symbol(d3.symbolStar).size(60))
  .attr(
    "transform",
    (d) =>
      `translate(${xScale(d.Max)}, ${
        yScale(d.BuildAndCount) + yScale.bandwidth() / 2
      })`
  )
  .attr("fill", "var(--theme-foreground-focus)")
  .attr("opacity", "0.5")
  .attr("visibility", (d) => (showStars ? "visible" : "hidden"))
  .style("cursor", "pointer")
  .on("mouseover", (event, d) => {
    d3.select(event.target).attr("opacity", "1");

    // Find the link to the best log
    let bestLink = "https://logs.snow.xyz/logs/";
    bestLink += d.BestLog;
    tooltip.style("opacity", 1).html(`
      <div class="card" style="padding: 7px;">
        <div>${d.spec}</div>
        <div>Item Level: ${d3.format("4.0d")(d.BestGearscore)}</div>
        <div>${d3.format(".3s")(d.Max)} DPS</div>
        <div>${bestLink}</div>
      </div>
    `);
  })
  .on("mouseout", (event, d) => {
    d3.select(event.target).attr("opacity", "0.5");
    d3.select(this).style("cursor", "");

    // Hide tooltip
    d3.selectAll(".tooltip").attr("opacity", 0).style("left", "-9999px");
  })
  .on("mousemove", (event) => {
    if (event.offsetX > width / 2) {
      tooltip.style("left", event.offsetX - 140 + "px");
    } else {
      tooltip.style("left", event.offsetX + 30 + "px");
    }

    tooltip.style("top", event.pageY - 30 + "px");
  })
  .on("click", (event, d) => {
    window.open(`https://logs.snow.xyz/logs/${d.BestLog}`, "_blank");
  });

svg
  .on("mousemove", (event) => {
    const x = event.offsetX;
    const y = event.offsetY;

    // Update line
    svg
      .selectAll(".mouseLine")
      .attr("x", x + 1)
      .attr("y", margins.top)
      .attr("width", 1)
      .attr("height", height - xAxisHeight - margins.bottom)
      .attr("fill", "var(--theme-foreground-muted)")
      .attr("opacity", 0.5)
      .attr("visibility", x > yAxisWidth ? "visible" : "hidden");
  })
  .on("mouseout", () => {
    svg.selectAll(".mouseLine").attr("visibility", "hidden");
  });

// Add latest log date string
svg
  .append("text")
  .attr(
    "transform",
    `translate(${width - margins.right}, ${height - margins.bottom - 5})`
  )
  .attr("text-anchor", "end")
  .attr("font-family", "var(--sans-serif)")
  .attr("font-size", "12px")
  .attr("fill", "var(--theme-foreground-faintest)")
  .text(`Latest log: ${latestLog.toLocaleDateString()}`);

// Add total logs string
svg
  .append("text")
  .attr(
    "transform",
    `translate(${width - margins.right}, ${height - margins.bottom - 20})`
  )
  .attr("text-anchor", "end")
  .attr("font-family", "var(--sans-serif)")
  .attr("font-size", "12px")
  .attr("fill", "var(--theme-foreground-faintest)")
  .text(`Total logs: ${nLogs}`);

// Add button to copy url to clipboard
svg
  .append("text")
  .attr("transform", `translate(${margins.left}, ${height - margins.bottom})`)
  .attr("text-anchor", "start")
  .attr("font-family", "var(--sans-serif)")
  .attr("fill", "var(--theme-foreground-focus)")
  .attr("font-size", "12px")
  .text("Share: Copy URL")
  .style("cursor", "pointer")
  .on("click", (event) => {
    navigator.clipboard.writeText(queryUrl);

    // Change our text to "copied"
    d3.select(event.target).text("Share: Copied!");
  });

  display(svg.node());
}
```

## ${selectedBoss ? "Class Statistics" : ""}

```js class data table
const classData = db.query(`
  SELECT spec, COUNT(*) AS Logs,
    quantile(dps, 0.25) AS Q1,
    median(dps) AS Median,
    mean(dps) AS Mean,
    quantile(dps, 0.75) AS Q3,
    min(dps) AS Min,
    max(dps) AS Max,
    Q3 - Q1 AS IQR,
    IF(Q1 - 15/10 * IQR < Min, Min, Q1 - 15/10 * IQR) AS Lower,
    IF(Q3 + 15/10 * IQR > Max, Max, Q3 + 15/10 * IQR) AS Upper,
    spec || ' (' || COUNT(*) || ')' AS BuildAndCount,
    CAST(list(id ORDER BY dps DESC)[1] AS VARCHAR) AS BestLog,
    CAST(list(gearscore ORDER BY dps DESC)[1] AS VARCHAR) AS BestGearscore,
  FROM logs
  ${filter}
  GROUP BY spec
  ORDER BY ${selectedSort} DESC
`);

const classTable = Inputs.table(classData, {
  columns: [
    "spec",
    "Logs",
    "Q1",
    "Median",
    "Mean",
    "Q3",
    "Min",
    "Max",
    "IQR",
    "Lower",
    "Upper",
  ],
  header: {
    spec: "Build",
  },
  format: {
    Q1: d3.format(".3s"),
    Median: d3.format(".3s"),
    Mean: d3.format(".3s"),
    Q3: d3.format(".3s"),
    IQR: d3.format(".3s"),
    Min: d3.format(".3s"),
    Max: d3.format(".3s"),
    Lower: d3.format(".3s"),
    Upper: d3.format(".3s"),
  },
  layout: "auto",
  sort: "spec",
  select: false,
});

const selectedClasses = Generators.input(classTable);

if (selectedBoss) {
  display(classTable);
}
```

## ${selectedBoss ? "Record Logs" : ""}

```js record logs table
// Unnest class specs
const allSpecs = classSpecs
  .flatMap((spec) => spec)
  .filter((d) => !supportClasses.includes(d));

// For each spec, find the top 5 logs
const logLinkStub = "https://logs.snow.xyz/logs/";
let topLogs = await db.query(`
  SELECT spec,
  [CAST(list(id ORDER BY dps DESC)[1] AS VARCHAR),  CAST(list(dps ORDER BY dps DESC)[1] AS BIGINT)] AS log1,
  [CAST(list(id ORDER BY dps DESC)[2] AS VARCHAR),  CAST(list(dps ORDER BY dps DESC)[2] AS BIGINT)] AS log2,
  [CAST(list(id ORDER BY dps DESC)[3] AS VARCHAR),  CAST(list(dps ORDER BY dps DESC)[3] AS BIGINT)] AS log3,
  [CAST(list(id ORDER BY dps DESC)[4] AS VARCHAR),  CAST(list(dps ORDER BY dps DESC)[4] AS BIGINT)] AS log4,
  [CAST(list(id ORDER BY dps DESC)[5] AS VARCHAR),  CAST(list(dps ORDER BY dps DESC)[5] AS BIGINT)] AS log5,
  FROM logs
  ${filter}
  GROUP BY spec
`);

function idToLog(d) {
  d = d.toArray();
  if (d[0]) {
    return htl.html`<a href="${logLinkStub}${d[0]}" target="_blank">${d3.format(
      ".3s"
    )(d[1])}</a>`;
  } else {
    return "No log";
  }
}

if (selectedBoss) {
  display(
    Inputs.table(topLogs, {
      header: {
        spec: "Build",
        log1: "#1",
        log2: "#2",
        log3: "#3",
        log4: "#4",
        log5: "#5",
      },
      format: {
        log1: idToLog,
        log2: idToLog,
        log3: idToLog,
        log4: idToLog,
        log5: idToLog,
      },
      sort: "spec",
      layout: "auto",
      select: false,
    })
  );
}
```
