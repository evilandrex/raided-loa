# Raided Lost Ark

<div class="warning">
  <p>This is a work in progress!</p>
  <p>
    TODO:
    <li>Add toggle to show best stars on plot</li>
    <li>Scrape Sonavel to fix TTH, Taijutsu, CO classifications</li>
    <li>Scrape Gargadeth to fix CO classifications</li>
    <li>Hide red errors from cells</li>
    <li>See if we can rename class data table columns to display</li>
    <li>Leverage selections from class data table</li>
    <li>Play with class colors</li>
    <li>Finish scraping other bosses</li>
    <li>Add info beside filters</li>
    <li>Add date and branding to plot with a hash of the filters</li>
    <li>Support light and dark mode</li>
    <li>Look into table options for records logs (sorting #1, disable selection)</li>
  </p>
  
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
        ${filterDeadToggle}
        ${filterWeirdToggle}
        <sub>Princcess GL, weird support count, weird player count</sub>
      </details>
    </div>
</div>

```js
const guardians = ["Sonavel", "Gargadeth", "Veskal"];

const raids = {
  Brelshaza: [1, 2, 3, 4, 5, 6],
  Kayangel: [1, 2, 3],
  Akkan: [1, 2, 3],
  Ivory: [1, 2, 3, 4],
  Thaemine: [1, 2, 3, 4],
};
let bosses = [null, ...guardians, ...Object.keys(raids)];

const bossSelect = Inputs.select(bosses, {
  value: null,
  label: "Boss",
});
const selectedBoss = Generators.input(bossSelect);
```

```js
const reqDiff =
  guardians.includes(selectedBoss) ||
  selectedBoss == "Kakul Saydon" ||
  selectedBoss == "Brelshaza" ||
  selectedBoss == "Kayangel" ||
  selectedBoss === null;

const diffValue =
  selectedBoss == "Kakul Saydon"
    ? "Normal"
    : selectedBoss == "Brelshaza"
    ? "Hard"
    : selectedBoss == "Kayangel"
    ? "Hard"
    : reqDiff
    ? null
    : "Normal";

const difficultyRadio = Inputs.radio(["Normal", "Hard"], {
  value: diffValue,
  label: "Difficulty",
  disabled: reqDiff,
});
const difficulty = Generators.input(difficultyRadio);
```

```js
const gates = Object.keys(raids).includes(selectedBoss)
  ? raids[selectedBoss]
  : ["No Gates"];
const gateRadio = Inputs.radio(gates, {
  value: gates.length <= 1 ? null : gates[0],
  label: "Gate",
  disabled: gates.length === 1,
});
const gate = Generators.input(gateRadio);
```

```js
const sortSelect = Inputs.select(
  new Map([
    ["Median (middle performance)", "median"],
    ["Upper (reasonable ceiling)", "upper"],
    ["Lower (reasonable floor)", "lower"],
    ["Max (the best!)", "max"],
  ]),
  {
    label: "",
  }
);
const selectedSort = Generators.input(sortSelect);
```

```js
const patchSelect = Inputs.select(
  new Map([
    ["April 2024 - Mage Balance (Current)", [`2024-04-17`, Date.now()]],
    ["March 2024 - Breaker", [`2024-03-20`, `2024-04-16`]],
    ["January 2024 - Major Balance", [`2023-11-14`, `2024-03-19`]],
    ["November 2023 - Souleater", [`2023-09-13`, `2023-11-13`]],
    ["September 2023 - Minor Balance", [`2023-08-16`, `2023-09-12`]],
    ["August 2023 - Aeromancer", [`2022-02-11`, `2023-08-15`]],
    ["All Patches", [`2022-02-11`, Date.now()]],
  ]),
  {
    label: "",
  }
);
const selectedPatch = Generators.input(patchSelect);
```

```js
const dateStartSelect = Inputs.date({
  label: "Start Date",
  value: selectedPatch[0],
});
const dateStart = Generators.input(dateStartSelect);

const dateEndSelect = Inputs.date({
  label: "End Date",
  value: selectedPatch[1],
});
const dateEnd = Generators.input(dateEndSelect);
```

```js
const iLevelMinRange = Inputs.range([1580, 1675], {
  value: 1580,
  step: 1,
});
const iLevelMin = Generators.input(iLevelMinRange);

const iLevelMaxRange = Inputs.range([1580, 1675], {
  value: 1675,
  step: 1,
});
const iLevelMax = Generators.input(iLevelMaxRange);
```

```js
const durationMinRange = Inputs.range([0, 3600], {
  value: 90,
  step: 1,
});
const durationMin = Generators.input(durationMinRange);

const durationMaxRange = Inputs.range([0, 3600], {
  value: 3600,
  step: 1,
});
const durationMax = Generators.input(durationMaxRange);
```

```js
const filterWeirdToggle = Inputs.toggle({
  label: "Filter Weird",
  value: true,
});
const filterWeird = Generators.input(filterWeirdToggle);
```

```js
const filterDeadToggle = Inputs.toggle({
  label: "Filter Dead",
  value: true,
});
const filterDead = Generators.input(filterDeadToggle);
```

## Aggregate Data

```js
const supportClasses = [
  "Blessed Aura",
  "Full Bloom",
  "Desperate Salvation",
  "Princess Maker",
];
let url =
  "https://raw.githubusercontent.com/evilandrex/raided-loa-scraper/main/data/";

// Check if boss is a guardian
if (guardians.includes(selectedBoss)) {
  url += `${selectedBoss}.csv`;
} else {
  url += `${selectedBoss}_G${gate}_${difficulty}.csv`;
}

// Load data from github
let data = await aq.loadCSV(url, {
  parse: {
    date: (d) => aq.op.parse_date(Number(d)),
    dead: (d) => d === "True",
    weird: (d) => d === "True",
  },
});

// Filter based on inputs
data = data
  .filter(aq.escape((d) => d.date >= dateStart && d.date <= dateEnd))
  .filter(aq.escape((d) => (filterWeird ? d.weird === false : true)))
  .filter(aq.escape((d) => (filterDead ? d.dead === false : true)))
  .filter(
    aq.escape((d) => d.gearScore >= iLevelMin && d.gearScore <= iLevelMax)
  )
  .filter(
    aq.escape(
      (d) =>
        d.duration >= durationMin * 1000 && d.duration <= durationMax * 1000
    )
  )
  .filter(aq.escape((d) => !aq.op.includes(supportClasses, d.class)))
  .reify();
```

```js
const width = Generators.width(document.querySelector("main"));
const plotHeight = 850;
const margins = { top: 10, right: 10, bottom: 10, left: 10 };
const xAxisHeight = 50;
const yAxisWidth = 250;
const height = plotHeight + margins.top + margins.bottom + xAxisHeight;
```

```js
const classSpecs = [
  ["Mayhem", "Berserker's Technique"],
  ["Rage Hammer", "Gravity Training"],
  ["Combat Readiness", "Lone Knight"],
  ["Blessed Aura", "Judgment"],
  ["Predator", "Punisher"],
  ["Order of the Emperor", "Empress's Grace"],
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

```js
// Create x-scale (based on dps)
const xScale = d3
  .scaleLinear()
  .domain([0, d3.max(classData.array("max"))])
  .range([margins.left + yAxisWidth, width - margins.right]);

// Create y-scale (categorical for each class)
const yScale = d3
  .scaleBand()
  .domain(classData.array("class"))
  .range([margins.top, height - margins.bottom - xAxisHeight])
  .padding(0.2);
```

```js
// Create SVG container
const svg = d3
  .create("svg")
  .attr("width", width)
  .attr("height", height)
  .style("background", "transparent");

const g = svg.append("g").selectAll("g").data(classData).join("g");

// Add main box
g.append("rect")
  .attr("x", (d) => xScale(d.q1))
  .attr("y", (d) => yScale(d.class))
  .attr("width", (d) => xScale(d.q3) - xScale(d.q1))
  .attr("height", yScale.bandwidth())
  .attr("fill", (d) => classColors.get(d.class.split(" (")[0]));

// Add median line
g.append("line")
  .attr("x1", (d) => xScale(d.median))
  .attr("x2", (d) => xScale(d.median))
  .attr("y1", (d) => yScale(d.class))
  .attr("y2", (d) => yScale(d.class) + yScale.bandwidth())
  .attr("stroke", "white");

// Add lower whisker
g.append("line")
  .attr("x1", (d) => xScale(d.lower))
  .attr("x2", (d) => xScale(d.q1))
  .attr("y1", (d) => yScale(d.class) + yScale.bandwidth() / 2)
  .attr("y2", (d) => yScale(d.class) + yScale.bandwidth() / 2)
  .attr("stroke", "white");

// Add whisker cap
g.append("line")
  .attr("x1", (d) => xScale(d.lower))
  .attr("x2", (d) => xScale(d.lower))
  .attr("y1", (d) => yScale(d.class) + yScale.bandwidth() / 4)
  .attr("y2", (d) => yScale(d.class) + (yScale.bandwidth() * 3) / 4)
  .attr("stroke", "white");

// Add upper whisker
g.append("line")
  .attr("x1", (d) => xScale(d.q3))
  .attr("x2", (d) => xScale(d.upper))
  .attr("y1", (d) => yScale(d.class) + yScale.bandwidth() / 2)
  .attr("y2", (d) => yScale(d.class) + yScale.bandwidth() / 2)
  .attr("stroke", "white");

// Add whisker cap
g.append("line")
  .attr("x1", (d) => xScale(d.upper))
  .attr("x2", (d) => xScale(d.upper))
  .attr("y1", (d) => yScale(d.class) + yScale.bandwidth() / 4)
  .attr("y2", (d) => yScale(d.class) + (yScale.bandwidth() * 3) / 4)
  .attr("stroke", "white");

// Add a star for the best
g.append("text")
  .attr("x", (d) => xScale(d.max))
  .attr("y", (d) => yScale(d.class) + yScale.bandwidth() / 2)
  .attr("dy", "0.35em")
  .attr("text-anchor", "middle")
  .attr("fill", "gold")
  .attr("font-size", "20px")
  .attr("opacity", "0.5")
  .text("★");

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
    `translate(${(width - yAxisWidth) / 2 + yAxisWidth}, ${
      height - margins.bottom - xAxisHeight / 2
    })`
  )
  .attr("dy", "1em")
  .attr("text-anchor", "middle")
  .attr("font-size", "16px")
  .attr("fill", "white")
  .text("DPS (millions)");

// Create y-axis
const yAxis = d3.axisLeft(yScale);
svg
  .append("g")
  .attr("transform", `translate(${margins.left + yAxisWidth}, 0)`)
  .call(yAxis)
  .selectAll("text")
  .attr("font-size", "14px");

// Add y axis label
svg
  .append("text")
  .attr(
    "transform",
    `translate(${margins.left}, ${plotHeight / 2}) rotate(-90)`
  )
  .attr("dy", "1em")
  .attr("text-anchor", "middle")
  .attr("font-size", "16px")
  .attr("fill", "white")
  .text("Build (Logs)");

// Prepare tooltip
const tooltip = d3
  .select("main")
  .append("div")
  .style("position", "absolute")
  .style("opacity", 0);

// Add invisible box to support mouse over
g.append("rect")
  .attr("class", "rowMouseBox")
  .attr("x", (d) => xScale.range()[0])
  .attr("y", (d) => yScale(d.class))
  .attr("width", (d) => xScale.range()[1] - xScale.range()[0])
  .attr("height", yScale.bandwidth())
  .attr("fill", "transparent")
  .on("mouseover", (event, d) => {
    tooltip.style("opacity", 1).html(`
      <div class="card" style="padding: 7px;">
        <div>${d.class.split(" (")[0]}</div>
        <div>${d.class.split(" (")[1].replace(")", "")} logs</div>
        <br/>
        <div>Worst: ${d3.format(".3s")(d.min)}</div>
        <div>Floor: ${d3.format(".3s")(d.lower)}</div>
        <div>Q1: ${d3.format(".3s")(d.q1)}</div>
        <div>Median: ${d3.format(".3s")(d.median)}</div>
        <div>Q3: ${d3.format(".3s")(d.q3)}</div>
        <div>Ceiling: ${d3.format(".3s")(d.upper)}</div>
        <div>Best: ${d3.format(".3s")(d.max)}</div>
      </div>
    `);
    // Darken row
    d3.select(event.target).attr("fill", "rgba(255, 255, 255, 0.1)");
  })
  .on("mouseout", () => {
    tooltip.style("opacity", 0);
    // Move tooltip really really far away
    tooltip.style("left", "-9999px");
    // Lighten row
    g.selectAll(".rowMouseBox").attr("fill", "transparent");
  })
  .on("mousemove", (event) => {
    console.log(event);
    tooltip.style("left", event.offsetX - 140 + "px");
    tooltip.style("top", event.pageY - 40 + "px");
  });

display(svg.node());
```

## Record Logs

```js
// Unnest class specs
const allSpecs = classSpecs
  .flatMap((spec) => spec)
  .filter((d) => !supportClasses.includes(d));

// For each spec, find the top 5 logs
const logLinkStub = "https://logs.fau.dev/log/";
const topLogs = {
  spec: allSpecs,
  log1: [],
  log2: [],
  log3: [],
  log4: [],
  log5: [],
};
for (const spec of allSpecs) {
  const specIDs = data
    .filter(aq.escape((d) => d.class === spec))
    .orderby(aq.desc("dps"))
    .array("id");
  const bestDPS = data
    .filter(aq.escape((d) => d.class === spec))
    .orderby(aq.desc("dps"))
    .array("dps");

  topLogs.log1.push([specIDs[0], bestDPS[0]]);
  topLogs.log2.push([specIDs[1], bestDPS[1]]);
  topLogs.log3.push([specIDs[2], bestDPS[2]]);
  topLogs.log4.push([specIDs[3], bestDPS[3]]);
  topLogs.log5.push([specIDs[4], bestDPS[4]]);
}

const topLogsTable = aq.table(topLogs).rename({
  spec: "Build",
  log1: "#1",
  log2: "#2",
  log3: "#3",
  log4: "#4",
  log5: "#5",
});

function idToLog(d) {
  if (d[0]) {
    return htl.html`<a href="${logLinkStub}${d[0]}">${d3.format(".3s")(
      d[1]
    )}</a>`;
  } else {
    return "No log";
  }
}

display(
  Inputs.table(topLogsTable, {
    format: {
      "#1": idToLog,
      "#2": idToLog,
      "#3": idToLog,
      "#4": idToLog,
      "#5": idToLog,
    },
    sort: "Build",
    layout: "auto",
  })
);
```

## Data Table

```js
const classData = data
  .groupby("class")
  .rollup({
    nLogs: aq.op.count(),
    q1: aq.op.quantile("dps", 0.25),
    median: aq.op.median("dps"),
    mean: aq.op.mean("dps"),
    q3: aq.op.quantile("dps", 0.75),
    min: aq.op.min("dps"),
    max: aq.op.max("dps"),
  })
  .derive({
    iqr: (d) => d.q3 - d.q1,
  })
  .derive({
    lower: (d) => d.q1 - 1.5 * d.iqr,
    upper: (d) => d.q3 + 1.5 * d.iqr,
  })
  .derive({
    lower: (d) => Math.max(d.min, d.lower),
    upper: (d) => Math.min(d.max, d.upper),
  })
  .derive({
    class: (d) => d.class + ` (${d.nLogs})`,
  })
  .orderby(aq.desc(selectedSort))
  .reify();

display(Inputs.table(classData));
```
