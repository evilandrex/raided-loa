# Raided Lost Ark

Select boss

```js
const guardians = ["Caliligos", "Hanumatan", "Sonavel", "Gargadeth", "Veskath"];

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

const selectedBoss = view(Inputs.select(bosses), {
  value: null,
  label: "Boss",
});
```

```js
const reqDiff =
  guardians.includes(selectedBoss) ||
  selectedBoss == "Kakul Saydon" ||
  selectedBoss === null;

const difficulty = view(
  Inputs.radio(["Normal", "Hard"], {
    value: reqDiff ? null : "Normal",
    label: "Difficulty",
    disabled: reqDiff,
  })
);
```

```js
const gates = Object.keys(raids).includes(selectedBoss)
  ? raids[selectedBoss]
  : ["No Gates"];
const gate = view(
  Inputs.radio(gates, {
    value: gates.length <= 1 ? null : gates[0],
    label: "Gate",
    disabled: gates.length === 1,
  })
);
```

```js
const button = view(
  Inputs.button("Submit", { value: null, reduce: () => new Date() })
);
```

```js
let filter;
if (selectedBoss === null) {
  filter = {};
} else {
  filter = Object.keys(raids).includes(selectedBoss)
    ? {
        raids: { [selectedBoss]: { gates: gate, difficulties: difficulty } },
      }
    : {
        guardians: [selectedBoss],
      };
}
```

```js
let response;
if (button === null) {
  response = null;
} else {
  response = fetch(
    "https://corsproxy.io/?https://logs.fau.dev/api/logs?scope=arkesia&order=recent%20clear",
    {
      method: "POST",
      mode: "cors",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(filter),
    }
  )
    .then((response) => response.json())
    .then((data) => display(data));
}
```

```js
button;
```
