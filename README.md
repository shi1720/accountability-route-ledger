# Borrowed Standards, Delegated Review

Research artifact for **Shivam Gupta, “Borrowed Standards, Delegated Review: Complaint Routing and Evidentiary Participation in Central Asia’s Infrastructure Transition”**, 16 October 2026.

The study reconstructs two AIIB public cofinancing registers and traces the published record of EBRD IPAM case 2024/05 (Shokpar). The main findings describe recorded institutional arrangements. They are **not estimates of human-rights harm, legal eligibility determinations, or measures of remedy effectiveness**.

## Contents

- `paper/paper.pdf`, `paper/paper.tex`, `paper/references.bib`: manuscript and sources.
- `data/register_2024.csv`, `data/register_2025.csv`: all 136 and 152 numbered entries, respectively, retaining page, row, and source hash.
- `data/regional_2025.csv`: all 26 entries for the five Central Asian republics and Mongolia.
- `data/regional_check.csv`: separate check fixture transcribed against rendered pages; a second pass by the same study, not independent coding.
- `data/shokpar_events.json`: source-located events with exact dates or explicit date intervals.
- `data/sources.json`: source URLs, retrieval date, hashes, and document locators.
- `src/`: extraction, analysis, figures, and a source-carrying lookup CLI.
- `tests/`: twelve audit tests, including an exhaustive independent lookup oracle.
- `results/summary.json`: generated exact counts and decimal sums.
- `docs/`: methodology, prior-work positioning, practical applications, and submission text.

## Reproduce offline analysis

Python 3.9 or later is required. The analysis and tests use the standard library. Figure generation needs the packages in `requirements.txt`.

```sh
python3 src/analyze.py
python3 -m unittest discover -s tests -v
python3 src/figures.py
python3 src/ledger.py --snapshot 2025 --row 67
```

For a clean figure/extraction environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/figures.py
```

Build the manuscript with Tectonic (a multi-file LaTeX project containing four generated PDF figures and a bibliography):

```sh
cd paper
tectonic paper.tex
```

## Reconstruct from original PDFs

Original third-party source documents are not relicensed or bundled here. Download the two register PDFs listed in `data/sources.json` to a local `sources/` directory. `src/fetch_registers.py` does this and checks the frozen SHA-256 values. If the institution has changed a file, the script refuses to silently replace the study version.

```sh
python3 src/fetch_registers.py
python3 src/extract.py sources/aiib_cofinance_2024.pdf data/register_2024.csv --expected 136
python3 src/extract.py sources/aiib_cofinance_2025.pdf data/register_2025.csv --expected 152
python3 src/analyze.py
```

Extraction requires `pdftotext` from Poppler on PATH, in addition to PyMuPDF. The table extractor and Poppler independently agree on the critical amount, date, reference, policy, and IAM cells for all 288 row observations. Original PDF layout is not needed for offline reanalysis.

## Principal reproducible results

- End-2025 register: 152 entries; 26 satisfy the explicit regional definition.
- Regional listed AIIB financing: USD 5,417.78 million; 23 partner-IAM designations total USD 4,740.28 million.
- The best deterministic lookup using only the published applicable-policy label disagrees with at least 14 of the 152 IAM designations. Its financing-weighted optimum is USD 1,162.70 million.
- All 136 earlier entries match uniquely using member, full title, approval date, and financing. None changes its policy or IAM label. Five added regional operations produce the regional compositional change.
- Shokpar: 16 days from AIIB receipt to IPAM referral; 162 days to registration. These are calendar intervals, not findings of unlawful delay.
- The closure report records four reports delivered to IPAM and EBRD management, while requesters received summaries. Problem solving ended without agreement; the retrieved registry shows the case open at compliance assessment.

## Interpretation and rights

The single IAM column is **AIIB’s designation**, not an exhaustive inventory of every cofinancier’s, domestic, judicial, or other remedial route. Register labels abbreviate policy versions. A row’s presence does not establish current complaint eligibility. A missing project is not a project with no cofinanciers. Monetary shares are financing descriptions, not risk or harm scores. January 2026 PPM rules are not retroactively imposed on the May 2024 Shokpar submission.

Original code is MIT licensed. Original manuscript and figures are CC BY 4.0. Extracted factual data are offered under CC0 to the extent the author holds rights; source attribution and hashes remain supplied. Third-party materials retain their own terms. Please cite the manuscript and the original AIIB/EBRD sources when using the data.

Contact: shivam1720406@gmail.com.
