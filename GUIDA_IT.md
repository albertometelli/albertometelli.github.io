# Guida italiana — sito statico e bibliografia BibTeX

## 1. Struttura del sito

Il sito è composto da otto pagine HTML statiche. Non richiede database, backend o framework JavaScript. Header, navigazione, footer, metadati Open Graph e JSON-LD sono condivisi e vengono aggiornati da `scripts/render_shared_layout.py`.

Per visualizzarlo localmente:

```bash
python -m http.server 8000
```

Apri <http://localhost:8000>. Lo stile si trova in `assets/css/style.css`; header e footer in `templates/header.html` e `templates/footer.html`. Dopo aver modificato un template, esegui:

```bash
python scripts/render_shared_layout.py
```

## 2. Asset da preservare

Prima di sostituire una versione precedente del repository, scarica gli asset originali:

```bash
python scripts/download_assets.py
```

Il comando conserva localmente fotografia, CV, materiali, loghi e ritratti del team. I ritratti vengono ottimizzati in WebP 384×384. Se il download degli asset storici fallisce, non eliminare la vecchia copia finché i file non sono stati salvati altrove.

## 3. Fonte canonica delle pubblicazioni

La fonte unica è costituita da:

- `bibliography/biblio_a.bib`: abstract e lavori aggiuntivi;
- `bibliography/biblio_b.bib`: capitoli di libro;
- `bibliography/biblio_bb.bib`: libri;
- `bibliography/biblio_c.bib`: conferenze;
- `bibliography/biblio_j.bib`: journal;
- `bibliography/biblio_r.bib`: report tecnici;
- `bibliography/biblio_t.bib`: tesi;
- `bibliography/biblio_u.bib`: under review;
- `bibliography/biblio_w.bib`: workshop.

Le conferenze devono essere `@inproceedings`, i journal `@article`. Non modificare manualmente `bibliography/biblio_all.bib`, `bibliography/biblio_top.bib`, `bibliography/downloads/` o le schede generate in `publications.html`.

Oltre ai normali campi BibTeX si possono usare `rankCORE`, `rankSJR`, `rankGGS`, `acceptance`, `note`, `alphabetic`, `equalauthors`, `slides`, `poster`, `presentation`, `video`, `code`, `dblpkey`, `core_source_url`, `sjr_source_url`, `acceptance_source_url` e `sjrcategory`.

Per SCImago la categoria predefinita è **Artificial Intelligence**. Le eccezioni sono configurate in `data/sjr_categories.json` o nel campo `sjrcategory`. Un quartile SJR successivo alla pubblicazione può restare come annotazione storica, ma non viene conteggiato come Q1 temporalmente valido.

## 4. Build offline raccomandata

Installa una volta le dipendenze:

```bash
python -m pip install -r requirements.txt
```

Dopo ogni modifica ai BibTeX esegui:

```bash
python scripts/build_publications.py
```

Questa è la modalità predefinita, deterministica e raccomandata. Il comando:

1. legge i BibTeX canonici;
2. unisce duplicati accidentali preservando chiavi e annotazioni;
3. valida tipi, campi obbligatori e chiavi;
4. ordina i record per anno, stato e periodo della venue;
5. genera `biblio_all.bib`, `biblio_top.bib` e i BibTeX puliti in `bibliography/downloads/`;
6. produce `data/reports/bibliography_report.json`;
7. rigenera `publications.html`, l'anteprima della homepage e i metadati strutturati;
8. esegue tutti i test di regressione.

La procedura si interrompe al primo errore. Non viene prodotto alcun dataset bibliografico JSON per il browser: tutte le pubblicazioni sono già presenti nell'HTML statico.

Gli `under review` restano nell'archivio BibTeX ma non sono mostrati nella pagina. La metrica principale **Publications** è la somma di conferenze e journal; workshop, abstract, report, libri, capitoli e tesi rimangono consultabili ma non contribuiscono a quel totale.

I BibTeX scaricabili contengono soltanto campi di citazione. Ranking, acceptance rate, note e materiali aggiuntivi non vengono esportati.

## 5. Download e arricchimento online — sperimentale

> **Attenzione:** lo scaricamento online dei dati bibliografici è sperimentale. La modalità offline e i BibTeX locali restano il riferimento autorevole.

Per provarlo:

```bash
python scripts/build_publications.py --online --crossref-limit 35
```

La modalità sperimentale consulta:

- DBLP per nuovi record e campi bibliografici mancanti;
- Crossref per DOI, volume, numero e pagine;
- CORE/ICORE per i ranking delle conferenze;
- SCImago per i quartili storici specifici per categoria;
- OpenAccept e fonti ufficiali per gli acceptance rate.

Gli aggiornamenti sono incrementali: note, chiavi, slide, poster e annotazioni curate manualmente non vengono sovrascritti. Crossref viene accettato solo con corrispondenza stretta di titolo e anno; un dato non verificabile non viene inventato.

Le fonti esterne possono cambiare formato, applicare rate limit, bloccare richieste automatiche o non offrire edizioni storiche complete. Per questo ogni risultato online deve essere controllato tramite il diff dei BibTeX e `data/reports/bibliography_report.json`. Un errore interrompe la build; nessun risultato va pubblicato o registrato nel repository prima della revisione manuale.

## 6. Team

I membri, i ruoli, i collegamenti e le sorgenti dei ritratti sono mantenuti in `data/team.json`; `team.html` è generato. Dopo una modifica esegui `python scripts/render_shared_layout.py`. Per aggiornare anche le immagini usa `python scripts/download_assets.py`. I siti personali sono collegati al nome; Scholar, GitHub, LinkedIn e altri profili compaiono nella riga `person-links`.

## 7. GitHub Pages e aggiornamenti manuali

Pubblica il contenuto del progetto nella radice del repository GitHub Pages e configura Pages dalla root del branch `main`, o dal branch già utilizzato dal sito.

Il repository non esegue aggiornamenti bibliografici programmati o online e non scrive direttamente sul branch di pubblicazione. Quando cambia un BibTeX canonico su `main`, il workflow **Build site from BibTeX** esegue la build offline deterministica su un branch dedicato e apre una pull request con gli artefatti rigenerati. Può anche essere avviato manualmente. Prima del merge controlla sempre il diff e `data/reports/bibliography_report.json`.
