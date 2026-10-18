# Arun M. George — personal website

A small static academic website adapted from Minimal Light. Python 3.9+ is needed to rebuild it; there are no Python packages, Ruby gems, JavaScript dependencies, or remote fonts to install. The generated site works without JavaScript.

## Build and preview

From this website directory:

```sh
python3 scripts/build.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:8000. Stop the server with Ctrl+C. After editing content, rerun the build in another terminal and refresh the browser. The browser does not update automatically.

## Edit content

- `content/site.json`: profile, links, introduction, research themes, and the IDs of featured papers.
- `content/publications.json`: paper metadata, author order, concise summaries, and links. The homepage and Publications page use this same source.
- `content/patents.json`: verified U.S. patent grants, grant dates, inventors, and source links. The Patents page and homepage count share this record.
- `static/assets/site.css`: typography, colors, spacing, and responsive layout.
- `templates/page.html`: shared profile and page layout.

To add a paper, copy an existing object, give it a unique `id`, and fill in verified information. Add its ID to one theme's `papers` list if it should appear on the homepage. `self_author` must exactly match your name in that entry's author list. Keep the author's published name spelling in the record.

`year` must be a number. Empty `links` arrays are supported; they render no dead button. Accepted work should have `status: "Accepted"`. Preprints should be identified as preprints. Do not invent a future proceedings link.

For a portrait, place a photograph inside `static/assets/` and set `photo` to its path starting with `assets/`. The current draft uses the existing GitHub portrait. Set `email` to the address you want public; the current address was confirmed by Arun. Advisor and lab fields control the linked affiliation text. For the future public CV, put the approved PDF inside `static/files/` and set `cv` to `files/<filename>.pdf`. The builder copies only the configured CV. Keep old CVs in their separate workspace.

### Link the updated full CV when ready

Use the stable path `static/files/arun-m-george-cv.pdf` for the approved full academic CV, and set `cv` in `content/site.json` to `files/arun-m-george-cv.pdf`. Rebuild the site: a CV link then appears in the profile on every page. Replace the PDF at that same path for subsequent updates, so bookmarks continue to work. Keep targeted CVs separate unless a specific public version is deliberately chosen. Until the full CV is ready, leave `cv` empty; no placeholder or outdated download is shown.

Before launch, set `url` in `content/site.json` to the final HTTPS website address without a trailing slash. The builder adds page-specific canonical/social-preview URLs, a sitemap, and robots.txt when this field is set. During later updates, review time-sensitive biography text (such as Ph.D. year), paper acceptance/publication statuses, and CV freshness.

## GitHub Pages, when ready

1. Create a public repository named `<your-username>.github.io`. Its name follows the final GitHub username you choose.
2. Push the site source to its `main` branch. Do not push editorial notes or unpublished manuscripts.
3. In the repository, open Settings → Pages → Build and deployment → Source → GitHub Actions.
4. Run the “Build and deploy website” workflow from the Actions tab if necessary. Later pushes to `main` build and deploy automatically.
5. Open the URL reported by the deployment and verify it before sharing.

Only `dist/` is uploaded as the Pages artifact. This is separate from source-repository visibility: files committed to a public repository are public even when excluded from the Pages artifact. `.gitignore` excludes local editorial notes and generated output, but it cannot remove previously committed files. No repository has been created or pushed by this setup.

Navigation and asset paths are relative, so this draft also works under a project URL. Add a canonical URL and social-preview URL after the final website address is chosen.

## Design provenance

Layout and typography hierarchy adapted from [Minimal Light](https://github.com/yaoyao-liu/minimal-light), specifically the project's plain HTML version at commit `dd114c3fef2d97adc1c6b6d46901e0d96ab83a7c`. The original CC0 text is retained in `vendor/minimal-light-LICENSE.txt`. The customized stylesheet replaces the theme's external fonts, icon libraries, dark-mode rules, and sample tracking code.

## Current scope

The current version contains 16 public scholarly records, five granted U.S. patents, a portrait, advisor/lab links, email, and brief recognition/service details. The homepage selects six works plus a compact link to earlier event-camera research. The updated CV remains a future task. Anonymous submissions and unsubmitted manuscripts are not included. The DAC entry links the verified conference program rather than an unverified proceedings DOI.
