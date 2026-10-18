#!/usr/bin/env python3
"""Render shared header/footer, social metadata and JSON-LD into static pages."""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlparse

from bib_pipeline import export_model, load_entries, summary


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://albertometelli.github.io/"
ASSET_VERSION = "20261018"

PAGES = {
    "index.html": ("about", "Alberto Maria Metelli", "Academic profile of Alberto Maria Metelli, working on reinforcement learning, online learning, and sequential decision-making."),
    "research.html": ("research", "Research — Alberto Maria Metelli", "Research interests, funded projects, software, datasets, and selected recognitions."),
    "publications.html": ("publications", "Publications — Alberto Maria Metelli", "Scientific publications of Alberto Maria Metelli, generated from the local annotated bibliography."),
    "teaching.html": ("teaching", "Teaching — Alberto Maria Metelli", "Courses and teaching activities by academic year."),
    "team.html": ("team", "Team — Alberto Maria Metelli", "Faculty, postdoctoral researchers, Ph.D. students, and research assistants."),
    "positions.html": ("positions", "Open positions — Alberto Maria Metelli", "Open research positions in reinforcement learning and online learning."),
    "contacts.html": ("contacts", "Contact — Alberto Maria Metelli", "Contact details, office location, and directions."),
    "privacy.html": ("privacy", "Privacy & cookies — Alberto Maria Metelli", "Privacy and cookie information for this academic website."),
}

NAV = [
    ("about", "index.html", "About"),
    ("research", "research.html", "Research"),
    ("publications", "publications.html", "Publications"),
    ("teaching", "teaching.html", "Teaching"),
    ("team", "team.html", "Team"),
    ("positions", "positions.html", "Open positions"),
    ("contacts", "contacts.html", "Contact"),
]

HEADER_RE = re.compile(
    r"(?:<!-- shared-header:start -->.*?<!-- shared-header:end -->|"
    r'<a class="skip" href="#main">Skip to content</a>\s*<header class="topbar">.*?</header>)',
    re.S,
)
FOOTER_RE = re.compile(
    r"(?:<!-- shared-footer:start -->.*?<!-- shared-footer:end -->|"
    r'<footer class="site-footer">.*?</footer>)',
    re.S,
)
META_RE = re.compile(r"\n?<!-- shared-meta:start -->.*?<!-- shared-meta:end -->", re.S)
PUBLICATIONS_MAIN_RE = re.compile(r'<main id="main">.*?</main>', re.S)
HOME_PUBLICATIONS_RE = re.compile(
    r'(?:<!-- generated-home-publications:start -->\s*)?'
    r'<div class="home-pubs" id="home-publications">.*?</div>'
    r'(?:\s*<!-- generated-home-publications:end -->)?'
    r'(?=\s*</div></section>\s*<section class="section">)',
    re.S,
)
TEAM_MAIN_RE = re.compile(r'<main id="main">.*?</main>', re.S)

CATEGORIES = [
    ("conferences", "International conferences", "C"),
    ("journals", "Journal articles", "J"),
    ("workshops", "Workshop papers", "W"),
    ("abstracts", "Abstracts", "A"),
    ("reports", "Technical reports", "R"),
    ("books", "Books", "B"),
    ("chapters", "Book chapters", "BC"),
    ("theses", "Theses", "T"),
]


def clean_text(value: object, fallback: str = "") -> str:
    """Collapse whitespace before embedding bibliography fields in JSON-LD."""
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text or fallback


def navigation(active: str) -> str:
    links = []
    for key, href, label in NAV:
        current = ' aria-current="page"' if key == active else ""
        links.append(f'<a{current} href="{href}">{label}</a>')
    return "\n".join(links)


def person_schema() -> dict:
    return {
        "@type": "Person",
        "@id": f"{BASE_URL}#person",
        "name": "Alberto Maria Metelli",
        "url": BASE_URL,
        "image": f"{BASE_URL}assets/team/alberto-metelli.webp",
        "jobTitle": "Tenure-track Assistant Professor",
        "affiliation": {"@type": "CollegeOrUniversity", "name": "Politecnico di Milano", "url": "https://www.polimi.it/"},
        "sameAs": [
            "https://scholar.google.com/citations?user=R31IsPwAAAAJ&hl=en",
            "https://orcid.org/0000-0002-3424-5212",
            "https://dblp.org/pid/209/4941",
            "https://github.com/albertometelli",
            "https://www.linkedin.com/in/alberto-maria-metelli-01504214b/",
        ],
    }


def course_schema() -> list[dict]:
    courses = [
        ("Foundations of Computer Science", "Undergraduate", "https://webeep.polimi.it/course/view.php?id=24582"),
        ("Foundations of Artificial Intelligence", "Graduate", "https://webeep.polimi.it/course/view.php?id=25336"),
        ("Machine Learning", "Graduate", "https://webeep.polimi.it/course/view.php?id=19161"),
        ("Learning Theory", "Doctoral", "https://webeep.polimi.it/course/view.php?id=19029"),
        ("Reinforcement Learning", "Doctoral", "https://webeep.polimi.it/course/view.php?id=21020"),
    ]
    return [
        {
            "@type": "Course",
            "name": name,
            "educationalLevel": level,
            "url": url,
            "provider": {"@type": "CollegeOrUniversity", "name": "Politecnico di Milano", "url": "https://www.polimi.it/"},
            "instructor": {"@id": f"{BASE_URL}#person"},
        }
        for name, level, url in courses
    ]


def bibliography_records() -> list[dict]:
    bins, top, _ = load_entries()
    return [record for record in export_model(bins, top) if record.get("category") != "under-review"]


def article_schema(records: list[dict]) -> list[dict]:
    records = list(records)
    records.sort(key=lambda item: (int(item.get("year") or 0), item.get("title") or ""), reverse=True)
    articles = []
    for item in records[:25]:
        article = {
            "@type": "ScholarlyArticle",
            "headline": clean_text(item.get("title"), "Untitled"),
            "datePublished": clean_text(item.get("year")),
            "author": [
                {"@type": "Person", "name": clean_text(name)}
                for name in item.get("authors", [])
                if clean_text(name)
            ],
            "isPartOf": {
                "@type": "Periodical",
                "name": clean_text(item.get("venue"), "Publication"),
            },
        }
        url = item.get("paper_url") or item.get("url")
        if url:
            article["url"] = url
        if item.get("doi"):
            article["identifier"] = f"https://doi.org/{item['doi']}"
        articles.append(article)
    return articles


def metadata(filename: str, title: str, description: str, records: list[dict]) -> str:
    canonical = BASE_URL if filename == "index.html" else BASE_URL + filename
    graph = [person_schema()]
    if filename == "teaching.html":
        graph.extend(course_schema())
    elif filename == "publications.html":
        graph.extend(article_schema(records))
    structured = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    og_type = "profile" if filename == "index.html" else "website"
    canonical_attr = escape(canonical, quote=True)
    title_attr = escape(title, quote=True)
    description_attr = escape(description, quote=True)
    type_attr = escape(og_type, quote=True)
    return (
        "<!-- shared-meta:start -->\n"
        f'<link href="{canonical_attr}" rel="canonical"/>\n'
        f'<meta content="{title_attr}" property="og:title"/>\n'
        f'<meta content="{description_attr}" property="og:description"/>\n'
        f'<meta content="{type_attr}" property="og:type"/>\n'
        f'<meta content="{canonical_attr}" property="og:url"/>\n'
        '<meta content="Alberto Maria Metelli" property="og:site_name"/>\n'
        f'<meta content="{BASE_URL}assets/team/alberto-metelli.webp" property="og:image"/>\n'
        f'<script type="application/ld+json">{structured}</script>\n'
        "<!-- shared-meta:end -->"
    )


def safe_url(value: object) -> str:
    value = str(value or "").strip()
    return value if urlparse(value).scheme in {"http", "https"} else ""


def link(label: str, url: object, class_name: str = "") -> str:
    href = safe_url(url)
    if not href:
        return ""
    cls = f' class="{escape(class_name, quote=True)}"' if class_name else ""
    return f'<a{cls} href="{escape(href, quote=True)}" rel="noopener noreferrer" target="_blank">{escape(label)}</a>'


def authors_html(publication: dict) -> str:
    equal = {clean_text(name).casefold() for name in publication.get("equal_contribution_authors", [])}
    rendered = []
    for name in publication.get("authors", []):
        display = clean_text(name) + ("*" if clean_text(name).casefold() in equal else "")
        item = escape(display)
        if "alberto maria metelli" in clean_text(name).casefold():
            item = f"<strong>{item}</strong>"
        rendered.append(item)
    if len(rendered) == 2:
        return " and ".join(rendered)
    if len(rendered) > 2:
        return ", ".join(rendered[:-1]) + ", and " + rendered[-1]
    return "".join(rendered)


def publication_html(publication: dict, label: str) -> str:
    title = clean_text(publication.get("title"), "Untitled")
    venue = clean_text(publication.get("venue"), "Publication")
    year = clean_text(publication.get("year"))
    search = " ".join([title, venue, *publication.get("authors", [])])
    citation_parts = [", ".join(publication.get("authors", []))]
    if year:
        citation_parts.append(f"({year}).")
    citation_parts.extend([f"{title}.", f"{venue}."])
    citation_url = f'https://doi.org/{publication["doi"]}' if publication.get("doi") else publication.get("paper_url", "")
    citation = " ".join(filter(None, citation_parts)) + ((" " + citation_url) if citation_url else "")
    attrs = (
        f'data-category="{escape(publication.get("category", ""), quote=True)}" '
        f'data-year="{escape(year, quote=True)}" '
        f'data-search="{escape(search, quote=True)}"'
    )
    parts = [f'<article class="pub-item" {attrs}>', f'<span class="pub-serial">{escape(label)}</span>', f'<h3>{escape(title)}</h3>',
             f'<p class="pub-authors">{authors_html(publication)}</p>', f'<p class="pub-venue">{escape(venue)}']
    if year:
        parts.append(f'<span class="pub-year"> · {escape(year)}</span>')
    parts.append('</p>')
    if publication.get("note"):
        parts.append(f'<p class="pub-note">{escape(clean_text(publication["note"]))}</p>')
    tags = []
    if publication.get("alphabetical_order"):
        tags.append('<span class="order-tag">α–β order</span>')
    if publication.get("recognition"):
        tags.append(f'<span class="recognition-tag">{escape(clean_text(publication["recognition"]))}</span>')
    if publication.get("status"):
        tags.append(f'<span class="pub-status">{escape(clean_text(publication["status"]))}</span>')
    if publication.get("acceptance_rate"):
        text = clean_text(publication["acceptance_rate"])
        source = (publication.get("acceptance") or {}).get("source_url")
        tags.append(link(text, source, "rating-source acceptance-tag") or f'<span class="rating-label acceptance-tag">{escape(text)}</span>')
    for kind, record in (publication.get("ratings") or {}).items():
        if not record or not record.get("value") or (kind == "sjr" and record.get("chronologically_eligible") is False):
            continue
        if kind == "sjr":
            descriptor = f'SJR {record.get("source_year") or ""}: {record["value"]} · {record.get("category") or "Artificial Intelligence"}'
        elif kind == "core":
            descriptor = f'{record.get("scheme") or "CORE"} {record.get("source_year") or ""}: {record["value"]}'
        else:
            descriptor = str(record["value"])
        tags.append(link(descriptor, record.get("source_url"), "rating-source rating-tag") or f'<span class="rating-label rating-tag">{escape(descriptor)}</span>')
    if tags:
        parts.append('<p class="pub-metadata">' + "".join(tags) + '</p>')
    links = []
    primary_link_label = "Link ↗" if publication.get("category") in {"books", "chapters", "theses"} else "Paper ↗"
    links.append(link(primary_link_label, publication.get("paper_url")))
    for name, url in (publication.get("extra_links") or {}).items():
        if name.casefold() in {"slides", "poster", "presentation", "video", "arxiv", "code"}:
            links.append(link(name.capitalize() + " ↗", url))
    links = [item for item in links if item]
    bibtex = str(publication.get("bibtex_download") or "")
    if re.fullmatch(r'bibliography/downloads/entries/[A-Za-z0-9_.-]+\.bib', bibtex):
        links.append(f'<a class="bibtex-download" download href="{escape(bibtex, quote=True)}">BibTeX ↓</a>')
    links.append(f'<button aria-label="Copy citation for {escape(title, quote=True)}" class="citation-copy" data-citation="{escape(citation.strip(), quote=True)}" type="button">Copy citation</button>')
    parts.append('<div class="pub-links">' + "".join(links) + '</div></article>')
    return "".join(parts)


def metrics_html(records: list[dict]) -> str:
    counts = summary(records)
    values = [
        (counts["total"], "Publications"), (counts["conferences"], "Conference papers"),
        (counts["journals"], "Journal articles"), (counts["a_star_conference_papers"], "Papers in A* conferences · CORE/ICORE"),
        (counts["q1_journal_articles"], "Articles in Q1 journals · SCImago"),
    ]
    cards = "".join(f'<div class="metric"><strong>{escape(str(value))}</strong><span>{escape(label)}</span></div>' for value, label in values)
    def venue_counts(values: dict[str, int]) -> str:
        return " · ".join(f"{name} ({count})" for name, count in sorted(values.items(), key=lambda item: (-item[1], item[0].casefold()))) or "—"
    return cards, venue_counts(counts["selected_conferences"]), venue_counts(counts["selected_journals"])


def publications_main(records: list[dict]) -> str:
    counts = {key: sum(p.get("category") == key for p in records) for key, _, _ in CATEGORIES}
    tabs = [f'<button aria-pressed="true" class="pub-tab active" data-filter="all" type="button">All <span class="count">{len(records)}</span></button>']
    tabs.extend(f'<button aria-pressed="false" class="pub-tab" data-filter="{key}" type="button">{escape(title.replace("International ", "").replace(" articles", "s").replace(" papers", "s").capitalize())} <span class="count">{counts[key]}</span></button>' for key, title, _ in CATEGORIES)
    years = sorted({str(p.get("year")) for p in records if p.get("year")}, key=int, reverse=True)
    year_options = "".join(f'<option value="{escape(year)}">{escape(year)}</option>' for year in years)
    groups = []
    for key, title, prefix in CATEGORIES:
        publications = [p for p in records if p.get("category") == key]
        if not publications:
            continue
        body = []
        last_year = None
        for index, publication in enumerate(publications):
            year = str(publication.get("year") or "Undated")
            if year != last_year:
                body.append(f'<h3 class="pub-group-year" data-year-divider="{escape(year, quote=True)}">{escape(year)}</h3>')
                last_year = year
            body.append(publication_html(publication, f"{prefix}{len(publications) - index}"))
        groups.append(
            f'<section class="pub-group" data-group="{key}">\n'
            f'<div class="pub-group-heading"><h2>{escape(title)}</h2><span><b>{len(publications)}</b> records</span></div>\n\n'
            + "\n\n".join(body)
            + '\n</section>'
        )
    cards, selected_conferences, selected_journals = metrics_html(records)
    return f'''<main id="main"><header class="page-intro"><div class="wrap"><h1>Publications</h1></div></header>
<section aria-labelledby="pub-summary-title" class="section pub-metrics-section"><div class="wrap section-body"><div class="section-heading"><h2 class="section-title" id="pub-summary-title">Scientific productivity</h2></div><div class="metric-grid">{cards}</div><p class="metric-breakdown"><strong>Selected conferences: </strong>{escape(selected_conferences)}</p><p class="metric-breakdown"><strong>Selected journals: </strong>{escape(selected_journals)}</p></div></section>
<section class="section band"><div class="wrap section-body"><div class="section-heading"><h2 class="section-title">Browse papers</h2></div><nav aria-label="Publication types" class="pub-index">{"".join(tabs)}</nav><div class="pub-tools"><label class="search-box" for="pub-search"><span class="visually-hidden">Search publications</span><input autocomplete="off" id="pub-search" placeholder="Search titles, authors or venues…" type="search"/></label><label class="select-wrap" for="pub-year"><span>Year</span><select id="pub-year"><option value="all">All years</option>{year_options}</select></label></div><div class="pub-legend"><p><strong>How to read the author list:</strong> Unless explicitly marked otherwise, the first author is the main contributor. An asterisk (*) identifies authors who contributed equally; <strong>α–β order</strong> means authors are listed alphabetically.</p><p><strong>Venue information:</strong> <a href="https://portal.core.edu.au/conf-ranks/" rel="noopener noreferrer" target="_blank">CORE/ICORE</a> and <a href="https://www.scimagojr.com/" rel="noopener noreferrer" target="_blank">SCImago SJR</a> scores and quartiles show an applicable rating edition <em>at the publication year</em>, not today’s ranking. Missing values are not estimated.</p></div><div id="publications-list">\n{"\n\n".join(groups)}\n</div><p class="empty-state" hidden id="pub-empty">No publications found. Try a different search or year.</p></div></section></main>'''


def home_publications(records: list[dict]) -> str:
    selected = [p for p in records if p.get("category") in {"conferences", "journals"}][:5]
    items = []
    for publication in selected:
        title = escape(clean_text(publication.get("title"), "Untitled"))
        title_link = link(clean_text(publication.get("title"), "Untitled"), publication.get("paper_url")) or title
        items.append(f'<article class="home-pub"><span class="home-pub-year">{escape(str(publication.get("year") or ""))}</span><h3>{title_link}</h3><p class="home-pub-venue">{escape(clean_text(publication.get("venue")))}</p></article>')
    return ('<!-- generated-home-publications:start -->\n'
            '<div class="home-pubs" id="home-publications">' + "".join(items) + '</div>\n'
            '<!-- generated-home-publications:end -->')


def team_main() -> str:
    """Render every team card from the single canonical team manifest."""
    model = json.loads((ROOT / "data" / "team.json").read_text(encoding="utf-8"))
    sections = []
    for section in model["sections"]:
        cards = []
        for person in section["members"]:
            name = escape(person["name"])
            homepage = str(person.get("homepage") or "")
            if homepage:
                external = urlparse(homepage).scheme in {"http", "https"}
                extra = ' rel="noopener noreferrer" target="_blank"' if external else ""
                arrow = "↗" if external else "→"
                heading = (f'<a href="{escape(homepage, quote=True)}"{extra}>{name} '
                           f'<span aria-hidden="true">{arrow}</span></a>')
            else:
                heading = name
            profile_links = "".join(
                f'<a href="{escape(url, quote=True)}" rel="noopener noreferrer" target="_blank">{escape(label)}</a>'
                for label, url in person.get("links", {}).items()
            )
            cards.append(
                f'<article class="person"><div aria-hidden="true" class="person-avatar"><img alt="" height="128" '
                f'loading="lazy" onerror="this.hidden=true;this.nextElementSibling.hidden=false" '
                f'src="{escape(person["photo"], quote=True)}" width="128"/>'
                f'<span hidden="">{escape(person["initials"])}</span></div><div><h3>{heading}</h3>'
                f'<p>{escape(person["role"])}</p><div class="person-links">{profile_links}</div></div></article>'
            )
        count = len(section["members"])
        noun = "person" if count == 1 else "people"
        hidden = " hidden" if section.get("hidden") else ""
        sections.append(
            f'<section class="{escape(section["class"], quote=True)}"{hidden}><div class="wrap section-body">'
            f'<div class="section-heading"><h2 class="section-title">{escape(section["title"])}</h2>'
            f'<span class="section-suffix">{count} {noun}</span></div>'
            f'<div class="people-grid">{"".join(cards)}</div></div></section>'
        )
    return ('<main id="main"><header class="page-intro"><div class="wrap"><h1>Team</h1></div></header>'
            + "".join(sections) + "</main>")


def render_page(path: Path, page_id: str, title: str, description: str, header_template: str, footer_template: str, records: list[dict]) -> None:
    html = path.read_text(encoding="utf-8")
    if path.name == "publications.html":
        html, count = PUBLICATIONS_MAIN_RE.subn(lambda _: publications_main(records), html, count=1)
        if count != 1:
            raise RuntimeError("Unable to locate publications content")
    if path.name == "team.html":
        html, count = TEAM_MAIN_RE.subn(team_main(), html, count=1)
        if count != 1:
            raise RuntimeError("Unable to locate team content")
    elif path.name == "index.html":
        html, count = HOME_PUBLICATIONS_RE.subn(lambda _: home_publications(records), html, count=1)
        if count != 1:
            raise RuntimeError("Unable to locate recent publications content")
    header = header_template.replace("{{NAV_LINKS}}", navigation(page_id))
    html, header_count = HEADER_RE.subn(header, html, count=1)
    html, footer_count = FOOTER_RE.subn(footer_template, html, count=1)
    if header_count != 1 or footer_count != 1:
        raise RuntimeError(f"Unable to locate shared layout in {path.name}")
    meta = metadata(path.name, title, description, records)
    if META_RE.search(html):
        # A callable replacement preserves JSON escape sequences such as ``\n``.
        html = META_RE.sub(lambda _: "\n" + meta, html, count=1)
    else:
        html = html.replace('<meta content="#fcfcfd"', meta + '\n<meta content="#fcfcfd"', 1)
    html = re.sub(r'assets/css/style\.css(?:\?v=\d+)?', f'assets/css/style.css?v={ASSET_VERSION}', html)
    html = re.sub(r'assets/js/site\.js(?:\?v=\d+)?', f'assets/js/site.js?v={ASSET_VERSION}', html)
    path.write_text(html, encoding="utf-8")


def main() -> None:
    records = bibliography_records()
    header_template = (ROOT / "templates" / "header.html").read_text(encoding="utf-8").strip()
    footer_template = (ROOT / "templates" / "footer.html").read_text(encoding="utf-8").strip()
    for filename, (page_id, title, description) in PAGES.items():
        path = ROOT / filename
        if not path.exists():
            raise FileNotFoundError(path)
        render_page(path, page_id, title, description, header_template, footer_template, records)
        print(f"Rendered {filename}")


if __name__ == "__main__":
    main()
