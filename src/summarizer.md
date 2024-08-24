---
title: Raided Lost Ark Log Summarizer
toc: false
---

<h1>Raided Lost Ark Log Summarizer</h1>
Locally summarize your runs!

```js uploader
const file = view(Inputs.file());
```

```js sqlite
let db = undefined;
if (!!file) {
  db = await file.sqlite();
  display(db);
}
```

```js sql tester
if (!!db) {
  const table = db.sql`SELECT * FROM encounter_preview`;

  display(Inputs.table(table, { select: false }));
}
```
