# Church in Cagayan de Oro — Website

A simple, static website for the local church in Cagayan de Oro City, Philippines.
Plain HTML/CSS, no build step, deployable directly on GitHub Pages.

## Pages

- `index.html` — Home
- `hwmr.html` — HWMR (opening text drafted in `temp/HWMR/`)
- `about.html` — About Us
- `beliefs.html` — What We Believe
- `announcements.html` — Announcements / News (the "quick terminal" for saints)
- `meetings.html` — Meeting schedule & how to visit
- `resources.html` — Bible, ministry, and other local church links
- `contact.html` — Contact info

## Look & feel

Styling follows the LSM Online Publications site (deep-green nav bar, green
links/buttons, cream and tan neutrals, square corners). Colors are defined as
variables at the top of `css/style.css`.

- **Font:** Inter, self-hosted in `assets/fonts/` (Latin subset, variable
  weight, SIL OFL license included). No external font service is used, so it
  looks the same for every visitor. If it ever fails to load, a metric-matched
  system fallback takes over.
- **Logos:** web-ready versions live in `assets/web/` (seal, text logo in dark
  green and light, favicons, LSM mark). The large originals in `assets/` are source
  files only and are not loaded by the pages.
- `js/site.js` handles the footer year and the mobile menu.

## HWMR page

The reading area of `hwmr.html` is generated, not hand-edited. `tools/build_hwmr.py`
builds it from the files in `temp/HWMR/` (which is git-ignored):

- `Opening-text.txt` — the opening text (collapsible groups)
- one saved "Prophesying Reference" page per message (the week card and its tiles)

To add or update a message (for example Message Eleven), save its page into
`temp/HWMR/` and run `python tools/build_hwmr.py` (needs `pip install lxml`).
The week card's training name and location are set at the top of that script.
Each message can be linked directly, e.g. `hwmr.html#msg-3`.

## Editing announcements

Open `announcements.html` and copy an existing `<article class="announcement">`
block, paste it near the top (newest first), and edit the date, tag, title,
and text. No tooling required — just save and commit.

## Placeholders to fill in

Several details are still placeholders and should be updated with real info:

- Meeting times & address in `meetings.html`
- Contact email in `contact.html`
- Ministry/resource links in `resources.html`

## Local preview

Just open `index.html` in a browser — no server or build step needed.

## Deployment (GitHub Pages)

This repo is set up to deploy via GitHub Pages from the `main` branch root.
In the GitHub repo settings, under **Pages**, set the source to
`Deploy from a branch` → `main` → `/ (root)`.
