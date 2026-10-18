#!/usr/bin/env python3
"""Build only explicitly selected public files; Python standard library only."""
import json
import shutil
from datetime import date
from collections import defaultdict
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"


def esc(value):
    return escape(str(value), quote=True)


def link(label, url):
    return f'<a href="{esc(url)}">{esc(label)}</a>'


def paper_html(paper, full=False):
    heading = "h3" if full else "h4"
    title = esc(paper["title"])
    title = (f'<a href="{esc(paper["links"][0]["url"])}">{title}</a>'
             if paper["links"] else f'<span>{title}</span>')
    authors = ""
    if full:
        names = [f'<strong>{esc(a)}</strong>' if a == paper["self_author"] else esc(a)
                 for a in paper["authors"]]
        authors = '<p class="authors">' + ", ".join(names) + '</p>'
    summary = f'<p class="paper-summary">{esc(paper["summary"])}</p>' if not full else ""
    status = f' <span class="status">{esc(paper["status"])}</span>' if paper["status"] else ""
    year = f' · {paper["year"]}' if str(paper["year"]) not in paper["venue"] else ""
    links = "".join(link(item["label"], item["url"]) for item in paper["links"])
    links = f'<span class="paper-links">{links}</span>' if links else ""
    return (f'<li class="paper" id="{esc(paper["id"])}"><p class="paper-meta"><span class="venue">{esc(paper["venue"])}{year}</span>{status}</p>'
            f'<{heading} class="paper-title">{title}</{heading}>{authors}{summary}'
            f'<div class="paper-resources">{links}</div></li>')


def build():
    site = json.loads((ROOT / "content/site.json").read_text())
    site_url = site.get("url", "").rstrip("/")
    if site_url:
        parsed_url = urlsplit(site_url)
        if parsed_url.scheme != "https" or not parsed_url.netloc or parsed_url.query or parsed_url.fragment:
            raise ValueError("Site URL must be a full HTTPS address without a query or fragment")
    papers = json.loads((ROOT / "content/publications.json").read_text())
    patents = json.loads((ROOT / "content/patents.json").read_text())
    by_id = {p["id"]: p for p in papers}
    if len(by_id) != len(papers):
        raise ValueError("Publication IDs must be unique")
    for p in papers:
        if p["self_author"] not in p["authors"]:
            raise ValueError(f'Author mismatch in {p["id"]}')
    template = Template((ROOT / "templates/page.html").read_text())
    # No directory recursion from workspace: briefs, CVs, and manuscripts never enter dist.
    if OUT.is_symlink():
        raise ValueError("The generated output directory must not be a symbolic link")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "static/assets", OUT / "assets", dirs_exist_ok=True)
    (OUT / ".nojekyll").touch()

    profile_links = list(site["links"])
    if site["email"]:
        profile_links.insert(0, {"label": "Email", "url": "mailto:" + site["email"]})
    if site["cv"]:
        cv_path = ROOT / "static" / site["cv"]
        if not cv_path.is_file():
            raise ValueError("The configured CV file is missing")
        if cv_path.resolve().is_relative_to((ROOT / "static").resolve()) is False:
            raise ValueError("CV must be inside static")
        destination = OUT / site["cv"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(cv_path, destination)
        profile_links.append({"label": "CV", "url": site["cv"]})
    photo = ""
    if site["photo"]:
        photo_path = ROOT / "static" / site["photo"]
        if not photo_path.is_file() or not photo_path.resolve().is_relative_to((ROOT / "static/assets").resolve()):
            raise ValueError("Photo must exist inside static/assets")
        photo = f'<img class="portrait" src="{esc(site["photo"])}" alt="Portrait of {esc(site["name"])}" width="156" height="156">'

    def write_page(filename, title, content):
        navigation = "".join(
            f'<a href="{url}"' + (' aria-current="page"' if filename == target else '') + f'>{label}</a>'
            for target, url, label in [("index.html", "./", "Home"), ("publications.html", "publications.html", "Publications"), ("patents.html", "patents.html", "Patents")])
        values = {key: esc(site[key]) for key in ["name", "role", "department", "institution", "institution_url", "description"]}
        canonical_url = site_url + ("/" if filename == "index.html" else "/" + filename) if site_url else ""
        canonical = f'<link rel="canonical" href="{esc(canonical_url)}">\n  <meta property="og:url" content="{esc(canonical_url)}">' if canonical_url else ""
        values.update(title=esc(title), content=content, navigation=navigation, photo=photo, canonical=canonical, lab_link=link(site["lab"], site["lab_url"]),
                      links="".join(link(item["label"], item["url"]) for item in profile_links))
        (OUT / filename).write_text(template.substitute(values))

    intro = ''.join(f'<p>{esc(p)}</p>' for p in site["intro"][:2])
    intro += '<p class="advisor">Advised by ' + link(site["advisor"], site["advisor_url"]) + ' in the ' + link(site["lab"], site["lab_url"]) + '.</p>'
    intro += f'<p class="previously">{esc(site["intro"][2])}</p>'
    themes = []
    for theme in site["themes"]:
        entries = "".join(paper_html(by_id[key]) for key in theme["papers"])
        work_label = f'<p class="work-label">{esc(theme["work_label"])}</p>' if theme.get("work_label") else ""
        related = ""
        if theme.get("related"):
            related = '<p class="related">' + ' · '.join(link(a["label"], f'publications.html#{a["id"]}') for a in theme["related"]) + '</p>'
        themes.append(f'<section class="theme" aria-labelledby="{esc(theme["id"])}">'
                      f'<h3 id="{esc(theme["id"])}">{esc(theme["title"])}</h3>'
                      f'<p class="question">{esc(theme["question"])}</p>'
                      f'<p class="theme-description">{esc(theme["description"])}</p>{work_label}<ul class="papers">{entries}</ul>{related}</section>')
    home = (f'<section class="intro" aria-labelledby="about"><p class="eyebrow">About</p>'
            f'<h1 id="about">Adaptive and efficient AI</h1>{intro}</section>'
            f'<section class="research" aria-labelledby="research"><div class="section-heading"><h2 id="research">Research</h2><a href="publications.html">All publications <span aria-hidden="true">↗</span></a></div>{"".join(themes)}</section>'
            '<section class="beyond" aria-labelledby="beyond"><h2 id="beyond">Beyond papers</h2>'
            f'<div class="beyond-row"><h3>Recognition</h3><p>{esc(site["recognition"])}</p></div>'
            f'<div class="beyond-row"><h3>Patents</h3><p>Co-inventor on {len(patents)} granted U.S. patents from my work at TCS Research, spanning spike encoding and event-based sensing. <a href="patents.html">View patents <span aria-hidden="true">↗</span></a></p></div>'
            f'<div class="beyond-row"><h3>Community</h3><p>{esc(site["service"])}</p></div></section>'
            '<section class="contact" aria-labelledby="contact"><h2 id="contact">Get in touch</h2><p>I welcome conversations about continual learning, efficient inference, and hardware-aware AI. '
            + link(site["email"], "mailto:" + site["email"]) + '</p></section>')
    write_page("index.html", site["name"] + " | University of Notre Dame", home)
    years = defaultdict(list)
    for paper in papers:
        years[paper["year"]].append(paper)
    bibliography = "".join(f'<section aria-labelledby="year-{year}"><h2 class="publication-year" id="year-{year}">{year}</h2>'
                           '<ul class="papers publication-list">' + "".join(paper_html(p, full=True) for p in years[year]) + '</ul></section>'
                           for year in sorted(years, reverse=True))
    year_index = '<nav class="year-index" aria-label="Publication years">' + ''.join(link(str(y), f'#year-{y}') for y in sorted(years, reverse=True)) + '</nav>'
    publications = ('<p class="eyebrow">Writing &amp; research</p><h1>Publications</h1>'
                    '<p class="page-intro">Conference and journal papers, workshop papers, and preprints, listed by year. '
                    + link("Google Scholar", site["links"][0]["url"]) + ' · <a href="patents.html">Granted U.S. patents</a></p>' + year_index + bibliography)
    write_page("publications.html", "Publications | " + site["name"], publications)
    patent_entries = []
    for patent in patents:
        inventors = ', '.join(f'<strong>{esc(n)}</strong>' if n == 'Arun George' else esc(n) for n in patent["inventors"])
        granted = date.fromisoformat(patent["granted"]).strftime('%B %d, %Y').replace(' 0', ' ')
        patent_entries.append(f'<li class="paper"><p class="paper-meta"><span class="venue">{esc(patent["number"])}</span> <span class="status">Granted</span></p>'
                              f'<h2 class="paper-title">{link(patent["title"],patent["url"])}</h2><p class="authors">{inventors}</p>'
                              f'<p class="grant-date">Granted {granted} · Tata Consultancy Services</p></li>')
    patent_content = ('<p class="eyebrow">Research into practice</p><h1>Granted U.S. patents</h1>'
                      '<p class="page-intro">Inventions from my work at TCS Research on neuromorphic computing and event-based sensing. '
                      'Each entry below is a U.S. patent grant; applications and international family members are not counted separately.</p>'
                      '<ul class="papers patent-list">' + ''.join(patent_entries) + '</ul>')
    write_page("patents.html", "Patents | " + site["name"], patent_content)
    if site_url:
        urls = [site_url + path for path in ["/", "/publications.html", "/patents.html"]]
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{esc(url)}</loc></url>' for url in urls) + '</urlset>\n'
        (OUT / "sitemap.xml").write_text(sitemap)
        (OUT / "robots.txt").write_text(f'User-agent: *\nAllow: /\nSitemap: {site_url}/sitemap.xml\n')
    print(f"Built {len(papers)} publication entries, {len(patents)} patents, and 3 pages in {OUT}")


if __name__ == "__main__":
    build()
