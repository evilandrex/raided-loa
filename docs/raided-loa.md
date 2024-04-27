# Raided Lost Ark

<div class="grid grid-cols-2" style="grid-auto-rows: auto;">
    <div class="card">
      <h1>Select a fight</h1>
      ${bossSelect}
      ${difficultyRadio}
      ${gateRadio}
      <br/>
      <details>
        <summary>Advanced Options</summary>
        ${dateStartSelect}
        ${dateEndSelect}
        Preset Patch
        ${patchSelect}
        <br/>
        Item Level Range
        ${iLevelMinRange}
        ${iLevelMaxRange}
        <br/>
        ${filterWeirdToggle}
        <sub>Princcess GL, double support, super short duration</sub>
      </details>
      <br/>
      ${submitButton}
    </div>

</div>

```js
const guardians = ["Caliligos", "Hanumatan", "Sonavel", "Gargadeth", "Veskal"];

const raids = {
  Valtan: [1, 2],
  Vykas: [1, 2, 3],
  "Kakul Saydon": [1, 2, 3],
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
  selectedBoss === null;

const difficultyRadio = Inputs.radio(["Normal", "Hard"], {
  value: reqDiff ? null : "Normal",
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
const iLevelMinText = Inputs.text({
  label: "Min iLevel",
  value: 1,
  type: "number",
});
const iLevelMin = Generators.input(iLevelMinText);

const iLevelMaxText = Inputs.text({
  label: "Max iLevel",
  value: 1680,
  type: "number",
});
const iLevelMax = Generators.input(iLevelMaxText);
```

```js
const iLevelMinRange = Inputs.range([1, 1680], {
  value: 1,
  step: 1,
});
const iLevelMin = Generators.input(iLevelMinRange);

const iLevelMaxRange = Inputs.range([1, 1680], {
  value: 1680,
  step: 1,
});
const iLevelMax = Generators.input(iLevelMaxRange);
```

```js
const filterWeirdToggle = Inputs.toggle({
  label: "Filter Weird",
  value: true,
});
const filterWeird = Generators.input(filterWeirdToggle);
```

```js
let filter;
if (selectedBoss === null) {
  filter = {};
} else {
  filter = Object.keys(raids).includes(selectedBoss)
    ? {
        raids: {
          [selectedBoss]: { gates: [gate], difficulties: [difficulty] },
        },
      }
    : {
        guardians: [selectedBoss],
      };
}
```

```js
async function getLogs(filter, maxLogs = 300) {
  let logs = [];

  let fetching = true;
  let newLogs;
  while (fetching) {
    newLogs = await fetch(
      "https://corsproxy.io/?https://logs.fau.dev/api/logs?scope=arkesia&order=recent%20clear",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(filter),
      }
    ).then((response) => response.json());

    // Add new logs to logs
    logs = logs.concat(newLogs["encounters"]);

    if (!newLogs["more"] || logs.length >= maxLogs) {
      fetching = false;
    }
  }

  return logs;
}

const submitButton = Inputs.button("Submit", {
  value: null,
  reduce: () => getLogs(filter),
});
const data = Generators.input(submitButton);
```

```js
display(data);
```
