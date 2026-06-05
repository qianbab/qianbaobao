#!/usr/bin/env node
// Fetch fuller visible text for Serenity status pages through an already logged-in
// Chromium/Edge instance exposing a local CDP endpoint, e.g. --remote-debugging-port=9222.

import fs from "node:fs/promises";

let chromium;
try {
  ({ chromium } = await import("playwright"));
} catch (error) {
  console.error("Missing dependency: install the Node package 'playwright' before running this script.");
  console.error("Example: npm install playwright");
  process.exit(1);
}

const AUTHOR = "aleabitoreddit";
const CDP_URL = process.env.CDP_URL || "http://127.0.0.1:9222";
const LIMIT = Number(process.env.LIMIT || "0");
const WAIT_MS = Number(process.env.WAIT_MS || "2500");

function parseArgs(argv) {
  const args = { input: "", out: "serenity_x_status_details.csv" };
  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--out") args.out = argv[++i];
    else if (!args.input) args.input = arg;
  }
  if (!args.input) {
    throw new Error("Usage: node fetch_status_details_cdp.mjs input.csv --out status_details.csv");
  }
  return args;
}

function csvCell(value) {
  return `"${String(value ?? "").replaceAll('"', '""')}"`;
}

function parseCsvLine(line) {
  const cells = [];
  let cur = "";
  let quoted = false;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if (quoted && ch === '"' && line[i + 1] === '"') {
      cur += '"';
      i += 1;
    } else if (ch === '"') {
      quoted = !quoted;
    } else if (ch === "," && !quoted) {
      cells.push(cur);
      cur = "";
    } else {
      cur += ch;
    }
  }
  cells.push(cur);
  return cells;
}

async function readInputCsv(path) {
  const text = await fs.readFile(path, "utf8");
  const lines = text.split(/\r?\n/).filter(Boolean);
  const headers = parseCsvLine(lines[0]);
  return lines.slice(1).map((line) => {
    const cells = parseCsvLine(line);
    return Object.fromEntries(headers.map((header, index) => [header, cells[index] || ""]));
  });
}

async function main() {
  const args = parseArgs(process.argv);
  const inputRows = await readInputCsv(args.input);
  const urls = inputRows
    .map((row) => row.x_url || row.url)
    .filter((url) => url && url.includes(`/${AUTHOR}/status/`));
  const selected = LIMIT > 0 ? urls.slice(0, LIMIT) : urls;

  const browser = await chromium.connectOverCDP(CDP_URL);
  const context = browser.contexts()[0];
  const page = context.pages().find((p) => p.url().includes("x.com")) || await context.newPage();
  const output = [];

  for (const url of selected) {
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 45000 }).catch(() => {});
    await page.waitForTimeout(WAIT_MS);
    const record = await page.evaluate((author) => {
      const article = document.querySelector("article");
      const time = article?.querySelector("time")?.getAttribute("datetime") || "";
      const text = article?.innerText || document.body?.innerText || "";
      const authorLink = article?.querySelector(`a[href="/${author}"]`)?.getAttribute("href") || "";
      const statusLinks = [...document.querySelectorAll('a[href*="/status/"]')]
        .map((a) => a.href)
        .filter((href) => href.includes(`/${author}/status/`));
      return {
        posted_at_detail: time,
        detail_text: text.replace(/\s+/g, " ").trim(),
        author_confirmed: authorLink === `/${author}` ? "yes" : "unknown",
        status_links_visible: [...new Set(statusLinks)].join(";"),
      };
    }, AUTHOR);
    output.push({ x_url: url, ...record });
    console.log(`${output.length}/${selected.length} ${url}`);
  }

  const headers = ["x_url", "posted_at_detail", "author_confirmed", "detail_text", "status_links_visible"];
  const csv = [headers.map(csvCell).join(","), ...output.map((row) => headers.map((h) => csvCell(row[h])).join(","))].join("\n");
  await fs.writeFile(args.out, csv, "utf8");
  await browser.close();
  console.log(JSON.stringify({ count: output.length, out: args.out }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
