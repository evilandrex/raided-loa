// See https://observablehq.com/framework/config for documentation.
export default {
  // The project’s title; used in the sidebar and webpage titles.
  title: "Raided Lost Ark",

  // The pages and sections in the sidebar. If you don’t specify this option,
  // all pages will be listed in alphabetical order. Listing pages explicitly
  // lets you organize them into sections and have unlisted pages.
  pages: [
    {name: "Logs", path: "/loa-logs"},
    {name: "Analysis", path: "/loa-analysis"},
  ],

  // Content to add to the head of the page, e.g. for a favicon:
  head: '<link rel="icon" href="AndrexTransparentSquare.png" type="image/png" sizes="32x32">',

  // Some additional configuration options and their defaults:
  theme: ["cotton", "ink"], // try "light", "dark", "slate", etc.
  // header: "", // what to show in the header (HTML)
  footer: "A Raided Project",
  toc: false, // whether to show the table of contents
  // pager: true, // whether to show previous & next links in the footer
  // root: "docs", // path to the source root for preview
  // output: "dist", // path to the output root for build
  search: false, 
};
