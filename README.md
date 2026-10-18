# Alberto Maria Metelli — Static academic website

Eight static HTML pages inspired by the graphical language of Marco Mussi's academic site. No runtime database, backend or JavaScript framework. Bibliography is maintained as an **incrementally enriched, locally versioned annotated BibTeX archive**. The Publications page and all clean citation downloads are generated directly from those BibTeX sources; no bibliography data is fetched by visitors' browsers.

## Local preview

```shell
python -m http.server 8000
```

Visit http://localhost:8000. For detailed deployment and data-provenance instructions see the [English guide](GUIDE_EN.md) or the [Italian guide](GUIDA_IT.md).

## Shared layout and metadata

The navigation header and footer are maintained in `templates/header.html` and `templates/footer.html`. After editing either template, regenerate every page with:

```shell
python scripts/render_shared_layout.py
```

The same command refreshes canonical URLs, Open Graph metadata, and page-specific JSON-LD (`Person`, `Course`, and recent `ScholarlyArticle` records). Use it for shared-layout or page-content changes; use the complete publications build below after changing bibliography data.

## One-command publications build

Install the development dependencies once:

```shell
python -m pip install -r requirements.txt
```

Then run the complete offline build whenever a canonical BibTeX file changes:

```shell
python scripts/build_publications.py
```

This deterministic offline command reads the canonical BibTeX files, validates and sorts them, refreshes clean citation downloads, renders the static Publications page and homepage preview, and runs the complete regression suite. It stops immediately if any stage fails.

## Experimental online enrichment

Online bibliographic download and enrichment are **experimental**. The canonical local BibTeX files and the deterministic offline build remain authoritative.

```shell
python -m pip install -r requirements.txt
python scripts/build_publications.py --online --crossref-limit 35
```

The GitHub Actions workflow never enables online enrichment. When a canonical BibTeX file changes on `main`—or when the workflow is started manually—it runs the deterministic offline build and opens a pull request containing only the regenerated site artifacts.

Canonical source files: `bibliography/biblio_{a,b,bb,c,j,r,t,u,w}.bib`. `biblio_top.bib` is a generated selection. Do **not** manually edit `publications.html`, `bibliography/biblio_all.bib`, or `bibliography/downloads/`; rebuild them with `scripts/build_publications.py`.

Output: full annotated `.bib` files, clean `.bib` exports suitable for citations, `data/reports/bibliography_report.json` for build auditing, and a fully rendered static Publications page. No publication dataset is shipped as JSON or loaded by the website. `@inproceedings` is used for conference papers. CORE/ICORE, SCImago category-specific quartiles, acceptance statistics and presentation links are shown on the website when available but excluded from citation downloads. Q1 coverage is time-checked.

Run `python scripts/download_assets.py` on a network-connected machine to refresh the original photograph, CV, local material assets, logos, and every team portrait. Team portraits are normalized to compact 384×384 WebP files; their sources and destinations are declared in `data/team.json`. Social icons are inline SVG and require no CDN; only the optional Google Maps embed requires a third-party connection.

All team members, roles, links, and portrait sources are maintained in `data/team.json`. Run `python scripts/render_shared_layout.py` after editing it. The renderer also applies the shared cache-busting version to the stylesheet and script on every page.

Maintained sources: [DBLP](https://dblp.org/pid/209/4941), [CORE](https://portal.core.edu.au/conf-ranks/), [SCImago](https://www.scimagojr.com/), [Crossref](https://www.crossref.org/), [OpenAccept](https://github.com/OpenAccept/openaccept-metadata).


### v7 content updates (October 2026)

- Page headers use title-only styling. The homepage includes aligned profile links and author names in recent publications.
- Research interests include *Stability in Reinforcement Learning*. Projects display acronym, official title, and funding on separate lines.
- Teaching is grouped by academic year with original course links to WeBeep (or historic Beep links for early classes).
- Team data and portrait sources are centralized in `data/team.json`; `scripts/download_assets.py` refreshes all portraits.
- Open positions uses a green status indicator; Publications removes the duplicate header count and automatic-update caption.

### v8 About refinements

- The **Recent publications** preview displays title, venue, and year only (without author names). The full Publications page is unchanged.
- The **Academic experience** and **Education** sections show one uninterrupted vertical timeline with date labels to the left, nodes, and descriptions to the right on desktop. On mobile, the timeline shifts left while maintaining the exact original text.
