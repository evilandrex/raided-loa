---
title: Raided Lost Ark
toc: false
---

<h1>Raided Lost Ark</h1>

<div class="warning">
  <p>This is a work in progress!</p>
  <p>
    TODO:
    <li>Make best stars clickable as links</li>
    <li>Look into better display of difficulty/gate selectors</li>
    <li>Scrape Sonavel to fix TTH, Taijutsu, CO classifications</li>
    <li>Scrape Gargadeth to fix CO classifications</li>
    <li>Play with class colors</li>
    <li>Finish scraping other bosses</li>
    <li>Add info beside filters</li>
    <li>Maybe find a way to encrypt/decrypt filters efficiently</li>
    <li>Make opinionated defaults for each advanced option per boss</li>
    <li>Look into table options for records logs (sorting #1, disable selection)</li>
    <li>Query strings for filters</li>
    <li>Check if we can mouseover the class labels and still have highligh</li>
    <li>Customize theme</li>
    <li>Customize logo</li>
    <li>Add animation??</li>
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
        <br/>
        <br/>
        ${starToggle}
      </details>
    </div>
</div>

```js boss selector
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

```js difficulty radio
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

```js gates radio
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

```js sort selector
const sortSelect = Inputs.select(
  new Map([
    ["Median (middle performance)", "Median"],
    ["Upper (reasonable ceiling)", "Upper"],
    ["Lower (reasonable floor)", "Lower"],
    ["Max (the best!)", "Max"],
  ]),
  {
    label: "",
  }
);
const selectedSort = Generators.input(sortSelect);
```

```js patch selector
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

```js date selectors
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

```js ilevel ranges
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

```js duration ranges
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

```js weird toggle
const filterWeirdToggle = Inputs.toggle({
  label: "Filter Weird",
  value: true,
});
const filterWeird = Generators.input(filterWeirdToggle);
```

```js dead toggle
const filterDeadToggle = Inputs.toggle({
  label: "Filter Dead",
  value: true,
});
const filterDead = Generators.input(filterDeadToggle);
```

```js star toggle
const starToggle = Inputs.toggle({
  label: "Show Best Logs",
  value: true,
});
const showStars = Generators.input(starToggle);
```

## ${selectedBoss ? "Aggregate Data" : ""}

```js get data
const supportClasses = [
  "Blessed Aura",
  "Full Bloom",
  "Desperate Salvation",
  "Princess Maker",
];
let url =
  "https://raw.githubusercontent.com/evilandrex/raided-loa-scraper/main/data/";

// Check if boss is a guardian
if (selectedBoss == null) {
  url += "empty.csv";
} else if (guardians.includes(selectedBoss)) {
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

if (selectedBoss != null) {
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

```js boxplot
// Create x-scale (based on dps)
const maxCol = showStars ? "Max" : "Upper";
const xLeft = width > minWidth ? yAxisWidth + margins.left : margins.left;
const xScale = d3
  .scaleLinear()
  .domain([0, d3.max(selectedClasses.map((d) => d[maxCol]))])
  .range([xLeft, width - margins.right]);

// Create y-scale (categorical for each class)
const yScale = d3
  .scaleBand()
  .domain(selectedClasses.map((d) => d.Build))
  .range([margins.top, height - margins.bottom - xAxisHeight])
  .padding(0.2);

// Create SVG container
const svg = d3
  .create("svg")
  .attr("width", width)
  .attr("height", height)
  .style("background", "transparent");

const g = svg.append("g").selectAll("g").data(selectedClasses).join("g");

// Add main box
g.append("rect")
  .attr("x", (d) => xScale(d.Q1))
  .attr("y", (d) => yScale(d.Build))
  .attr("width", (d) => xScale(d.Q3) - xScale(d.Q1))
  .attr("height", yScale.bandwidth())
  .attr("fill", (d) => classColors.get(d.Build.split(" (")[0]));

// Add median line
g.append("line")
  .attr("x1", (d) => xScale(d.Median))
  .attr("x2", (d) => xScale(d.Median))
  .attr("y1", (d) => yScale(d.Build))
  .attr("y2", (d) => yScale(d.Build) + yScale.bandwidth())
  .attr("stroke", "white");

// Add lower whisker
g.append("line")
  .attr("x1", (d) => xScale(d.Lower))
  .attr("x2", (d) => xScale(d.Q1))
  .attr("y1", (d) => yScale(d.Build) + yScale.bandwidth() / 2)
  .attr("y2", (d) => yScale(d.Build) + yScale.bandwidth() / 2)
  .attr("stroke", "var(--theme-foreground)");

// Add whisker cap
g.append("line")
  .attr("x1", (d) => xScale(d.Lower))
  .attr("x2", (d) => xScale(d.Lower))
  .attr("y1", (d) => yScale(d.Build) + yScale.bandwidth() / 4)
  .attr("y2", (d) => yScale(d.Build) + (yScale.bandwidth() * 3) / 4)
  .attr("stroke", "var(--theme-foreground)");

// Add upper whisker
g.append("line")
  .attr("x1", (d) => xScale(d.Q3))
  .attr("x2", (d) => xScale(d.Upper))
  .attr("y1", (d) => yScale(d.Build) + yScale.bandwidth() / 2)
  .attr("y2", (d) => yScale(d.Build) + yScale.bandwidth() / 2)
  .attr("stroke", "var(--theme-foreground)");

// Add whisker cap
g.append("line")
  .attr("x1", (d) => xScale(d.Upper))
  .attr("x2", (d) => xScale(d.Upper))
  .attr("y1", (d) => yScale(d.Build) + yScale.bandwidth() / 4)
  .attr("y2", (d) => yScale(d.Build) + (yScale.bandwidth() * 3) / 4)
  .attr("stroke", "var(--theme-foreground)");

// Add a star for the best
g.append("text")
  .attr("x", (d) => xScale(d.Max))
  .attr("y", (d) => yScale(d.Build) + yScale.bandwidth() / 2)
  .attr("dy", "0.35em")
  .attr("text-anchor", "middle")
  .attr("fill", "var(--theme-foreground-focus)")
  .attr("font-size", "20px")
  .attr("opacity", "0.5")
  .attr("visibility", (d) => (showStars ? "visible" : "hidden"))
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
    `translate(${margins.left}, ${plotHeight / 2}) rotate(-90)`
  )
  .attr("dy", "1em")
  .attr("text-anchor", "middle")
  .attr("font-size", "16px")
  .attr("fill", "var(--theme-foreground)")
  .attr("font-family", "var(--sans-serif)")
  .text("Build (Logs)");

// Add branding at the bottom right
svg
  .append("text")
  .attr("x", width - margins.right)
  .attr("y", height - xAxisHeight - margins.bottom - yScale.bandwidth() / 2)
  .attr("text-anchor", "end")
  .attr("font-family", "var(--sans-serif)")
  .attr("font-size", "12px")
  .attr("fill", "var(--theme-foreground-faintest)")
  .text(`Raided Lost Ark - ${new Date().toLocaleDateString()}`);

// Prepare tooltip
const tooltip = d3
  .select("main")
  .append("div")
  .style("position", "absolute")
  .style("opacity", 0);

// Add invisible box to support mouse over
g.append("rect")
  .attr("class", "rowMouseBox")
  .attr("x", (d) => xScale.range()[0] - yAxisWidth + 25)
  .attr("y", (d) => yScale(d.Build))
  .attr("width", (d) => xScale.range()[1] - xScale.range()[0] + yAxisWidth - 25)
  .attr("height", yScale.bandwidth())
  .attr("fill", "transparent")
  .on("mouseover", (event, d) => {
    tooltip.style("opacity", 1).html(`
      <div class="card" style="padding: 7px;">
        <div>${d.Build.split(" (")[0]}</div>
        <div>${d.Build.split(" (")[1].replace(")", "")} logs</div>
        <br/>
        <div>Worst: ${d3.format(".3s")(d.Min)}</div>
        <div>Floor: ${d3.format(".3s")(d.Lower)}</div>
        <div>Q1: ${d3.format(".3s")(d.Q1)}</div>
        <div>Median: ${d3.format(".3s")(d.Median)}</div>
        <div>Q3: ${d3.format(".3s")(d.Q3)}</div>
        <div>Ceiling: ${d3.format(".3s")(d.Upper)}</div>
        <div>Best: ${d3.format(".3s")(d.Max)}</div>
      </div>
    `);
    // Darken row
    d3.select(event.target)
      .attr("fill", "var(--theme-foreground-muted)")
      .attr("opacity", "0.25");
  })
  .on("mouseout", () => {
    tooltip.style("opacity", 0);
    // Move tooltip really really far away
    tooltip.style("left", "-9999px");
    // Lighten row
    g.selectAll(".rowMouseBox").attr("fill", "transparent");
  })
  .on("mousemove", (event) => {
    tooltip.style("left", event.offsetX - 140 + "px");
    tooltip.style("top", event.pageY - 30 + "px");
  });

if (selectedBoss) {
  display(svg.node());
}
```

## ${selectedBoss ? "Class Data Table" : ""}

```js class data table
const classData = data
  .groupby("class")
  .rollup({
    Logs: aq.op.count(),
    Q1: aq.op.quantile("dps", 0.25),
    Median: aq.op.median("dps"),
    Mean: aq.op.mean("dps"),
    Q3: aq.op.quantile("dps", 0.75),
    Min: aq.op.min("dps"),
    Max: aq.op.max("dps"),
  })
  .derive({
    IQR: (d) => d.Q3 - d.Q1,
  })
  .derive({
    Lower: (d) => d.Q1 - 1.5 * d.IQR,
    Upper: (d) => d.Q3 + 1.5 * d.IQR,
  })
  .derive({
    Lower: (d) => Math.max(d.Min, d.Lower),
    Upper: (d) => Math.min(d.Max, d.Upper),
  })
  .derive({
    class: (d) => d.class + ` (${d.Logs})`,
  })
  .rename({ class: "Build" })
  .orderby(aq.desc(selectedSort))
  .reify();

const classTable = Inputs.table(classData, {
  format: {
    Build: (d) => d.split(" (")[0],
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
    return htl.html`<a href="${logLinkStub}${d[0]}" target="_blank">${d3.format(
      ".3s"
    )(d[1])}</a>`;
  } else {
    return "No log";
  }
}

if (selectedBoss) {
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
}
```
