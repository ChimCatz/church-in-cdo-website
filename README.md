# Church in Cagayan de Oro — Website

A simple, static website for the local church in Cagayan de Oro City, Philippines.
Plain HTML/CSS, no build step, deployable directly on GitHub Pages.

## Pages

- `index.html` — Home
- `about.html` — About Us
- `beliefs.html` — What We Believe
- `announcements.html` — Announcements / News (the "quick terminal" for saints)
- `meetings.html` — Meeting schedule & how to visit
- `resources.html` — Bible, ministry, and other local church links
- `contact.html` — Contact info

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
