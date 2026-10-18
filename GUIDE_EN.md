# English guide — static website and canonical BibTeX bibliography

## 1. Website structure

The website consists of eight static HTML pages. It requires no database, backend, or JavaScript framework. The header, navigation, footer, Open Graph metadata, and JSON-LD are shared and updated by `scripts/render_shared_layout.py`.

To preview the website locally:

```bash
python -m http.server 8000
```

Open <http://localhost:8000>. Styles are in `assets/css/style.css`; the shared header and footer are in `templates/header.html` and `templates/footer.html`. After changing a template, run:

```bash
python scripts/render_shared_layout.py
```

## 2. Assets to preserve

Before replacing an older version of the repository, download the original assets:

```bash
python scripts/download_assets.py
```

This command preserves the portrait, CV, materials, logos, and team photographs locally. Team portraits are optimized as 384×384 WebP files. If a historical asset cannot be downloaded, do not remove the old copy until the file has been backed up elsewhere.

## 3. Canonical publication sources

The single source of truth consists of:

- `bibliography/biblio_a.bib`: abstracts and additional works;
- `bibliography/biblio_b.bib`: book chapters;
- `bibliography/biblio_bb.bib`: books;
- `bibliography/biblio_c.bib`: conferences;
- `bibliography/biblio_j.bib`: journals;
- `bibliography/biblio_r.bib`: technical reports;
- `bibliography/biblio_t.bib`: theses;
- `bibliography/biblio_u.bib`: under-review manuscripts;
- `bibliography/biblio_w.bib`: workshops.

Conference papers must use `@inproceedings`, and journal papers must use `@article`. Do not manually edit `bibliography/biblio_all.bib`, `bibliography/biblio_top.bib`, `bibliography/downloads/`, or the generated publication cards in `publications.html`.

In addition to standard BibTeX fields, entries may use `rankCORE`, `rankSJR`, `rankGGS`, `acceptance`, `note`, `alphabetic`, `equalauthors`, `slides`, `poster`, `presentation`, `video`, `code`, `dblpkey`, `core_source_url`, `sjr_source_url`, `acceptance_source_url`, and `sjrcategory`.

The default SCImago category is **Artificial Intelligence**. Exceptions are configured in `data/sjr_categories.json` or through the `sjrcategory` field. An SJR edition newer than the paper may remain as a historical annotation, but it is not counted as a chronologically valid Q1 article.

## 4. Recommended offline build

Install the dependencies once:

```bash
python -m pip install -r requirements.txt
```

After changing any canonical BibTeX file, run:

```bash
python scripts/build_publications.py
```

This is the default, deterministic, and recommended mode. The command:

1. reads the canonical BibTeX files;
2. merges accidental duplicates while preserving keys and annotations;
3. validates entry types, required fields, and citation keys;
4. sorts records by year, status, and venue period;
5. generates `biblio_all.bib`, `biblio_top.bib`, and clean BibTeX downloads;
6. writes `data/reports/bibliography_report.json`;
7. rebuilds `publications.html`, the homepage preview, and structured metadata;
8. runs the complete regression suite.

The process stops at the first error. No bibliography JSON dataset is shipped to the browser: every publication is already rendered in the static HTML.

Under-review manuscripts remain in the BibTeX archive but are not displayed. The headline **Publications** metric is the sum of conference and journal papers only; workshops, abstracts, reports, books, chapters, and theses remain browsable but do not contribute to that total.

Downloadable BibTeX files contain citation fields only. Rankings, acceptance rates, notes, and supplementary materials are never exported.

## 5. Online download and enrichment — experimental

> **Warning:** online bibliographic data download is experimental. The offline build and the local BibTeX files remain authoritative.

To try it:

```bash
python scripts/build_publications.py --online --crossref-limit 35
```

The experimental mode queries:

- DBLP for new records and missing bibliographic fields;
- Crossref for DOI, volume, issue, and page information;
- CORE/ICORE for conference rankings;
- SCImago for historical, category-specific journal quartiles;
- OpenAccept and official sources for acceptance rates.

Updates are incremental: manually curated notes, citation keys, slides, posters, and annotations are not overwritten. Crossref records are accepted only after strict title and year matching, and unverifiable values are not invented.

External services may change their format, enforce rate limits, block automated requests, or lack complete historical editions. Always inspect the BibTeX diff and `data/reports/bibliography_report.json` after an online run. Any failure stops the build; no result should be published or committed before manual review.

## 6. Team

Team members, roles, links, and portrait sources are maintained in `data/team.json`; `team.html` is generated. After editing the manifest, run `python scripts/render_shared_layout.py`. Use `python scripts/download_assets.py` to refresh the images too. Personal websites are linked from the member's name; Scholar, GitHub, LinkedIn, and other profiles appear in the `person-links` row.

## 7. GitHub Pages and manual updates

Publish the project contents at the root of the GitHub Pages repository and configure Pages from the `main` branch root, or from the branch already used by the website.

The repository does not run scheduled or online bibliography updates and does not write directly to the publication branch. When a canonical BibTeX file changes on `main`, the **Build site from BibTeX** workflow runs the deterministic offline build on a dedicated branch and opens a pull request with the regenerated artifacts. It can also be started manually. Always review its diff and `data/reports/bibliography_report.json` before merging.
