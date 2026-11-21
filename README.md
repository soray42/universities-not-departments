# Universities, not departments: where academic prestige meets graduate pay

Haotian Yang, Bocconi University (haotian.yang@studbocconi.it)

Subject rankings rate a university's programme in a field partly by its academic standing. This repository
compares two orderings of the same university × field programmes, their academic standing and their graduates'
pay, in the United States (departments' ranks in the faculty-hiring network; College Scorecard and Census PSEO
earnings) and in the United Kingdom (REF research ratings; DfE LEO earnings). The two orderings agree substantially
across universities but much less among the departments of one university (correlation 0.45 against 0.05 in the
US, 0.62 against 0.10 in the UK), a contrast that survives a simulation test calibrated to each measure's noise.
The code here reproduces every number, table and figure of the paper and its Supplementary Information
(`paper/nhb/main.tex`, `paper/nhb/si.tex`) from public data.

## Reproduce

```
pip install -r requirements.txt     # Python 3.12
make all                            # = ./reproduce.sh all: data, analysis, paper
```

`make data` downloads every input listed in `data/sources.csv` from its official URL into `data/raw/` and
`data/orcid/` and checks the md5 of every file whose source is a fixed release. `make analysis` runs the scripts in
dependency order (`reproduce.sh` lists the steps); each Python process runs single-process under
`prlimit --as=3000000000`; `make analysis WORKERS=4` uses more worker processes where a script supports them (each
replicate has its own seed, so the results do not depend on the number of workers). `make paper` builds
`paper/nhb/si.pdf` and `paper/nhb/main.pdf` with `latexmk`.
Most scripts write their numbers to a `*_RESULT.md` file in the repository root and to tables in `data/interim/`;
scripts/80 and scripts/81 and the checks in `scripts/paper_checks/` print theirs to `logs/`, where every step's log
is kept. The figures of the paper are written to `outputs/figures/wapman2026/`.

`./reproduce.sh analysis --only 78` or `--from 78` runs a subset. `make data FROM_LOCAL=/path/to/data/raw`
symlinks the listed files from an existing copy instead of downloading them.

Requirements: Linux with `prlimit` (util-linux), Python 3.12, a LaTeX installation with `latexmk` and `bibtex`
for the paper.

Hardware and time: any Linux machine with 8 GB of RAM (no process exceeds the 3 GB cap) and about 11 GB of free
disk (4.5 GB downloaded; the ORCID archive and the ACS person files are extracted). Run in sequence with one
worker per script, the analysis takes about six hours, of which scripts/57 and scripts/84 take more than an hour each;
`make paper` takes a minute. `make check-urls` checks every source URL without downloading (a HEAD request, or a 1-byte request where a server
refuses HEAD).

### Manual steps

`make data` downloads everything except the NRC table, whose terms allow personal, non-commercial use only. Get
it yourself: on https://www.nap.edu/rdp/ download "Excel Data Table (revised 4/29/2011)", both the Mac and the
Windows workbook, and save them as `data/raw/nrc2010/ResDocTableMac8_4-29-11.xls` and
`data/raw/nrc2010/ResDocTableWin_4-29-11.xls`; then run `make all` again (finished downloads are kept).

Other sources need no manual step but can change:
- The US Bureau of Labor Statistics blocks scripted downloads, so the OES and SOC files come from Internet Archive
  copies with fixed timestamps; the CPI series comes from DBnomics and the state unemployment rates from FRED.
- The Survey of Earned Doctorates table has no download URL; `scripts/67_gradschool_timing.py` queries the NCSES
  table builder itself when the files are missing.
- The ORCID-derived edges are one 2.5 GB archive on Zenodo; `make data` extracts the 681 parquet shards
  (3.3 GB) with `py7zr`.
- Rows with `fixed` = no in `data/sources.csv` (the ABET, Nobel and FRED APIs, current AACSB and LEHD pages) are
  live resources: their md5 is that of the copy used in the paper and is reported, not enforced, and a revised
  copy can move the event-study and entry-condition numbers. Where a script checks the md5 of an input (REF
  results, Scorecard documentation, LEO, NRC, the BLS files, the SED tables), `fixed` = yes and a changed copy is
  reported by `make data` and stops that script.
- One such file has already changed at its source: the College Scorecard `InstitutionDataDocumentation.pdf` now
  served is not the copy used. The original (September 2025 version, a US Government work in the public domain) is
  bundled in `bundled/` and `make data` copies it into place.

## Data

No data file is redistributed here, apart from the one public-domain documentation file in `bundled/`. `data/sources.csv` lists every file with its URL, md5, size and terms; the
`section` column follows the provenance sections cited in the Supplementary Information (for example 10n for the
NRC table).

| Source | Used for | Licence / terms |
|---|---|---|
| Faculty-hiring ranks of Wapman et al.: 2026 regeneration (GitHub LarremoreLab/us-faculty-hiring-networks, commit 841e9c9) and the Zenodo v1 export (10.5281/zenodo.6941651, for institution names) | US ranks F and G | CC BY 3.0 US (Zenodo v1); the GitHub repository states no licence |
| College Scorecard field-of-study, institution and all-data files, June 2026 (US Department of Education) | US pay and selectivity | public domain (US Government) |
| PSEO V4.13.0 and V4.14.1, PSEO Flows V4.14.1, LEHD schema files (US Census Bureau) | careers, destinations | public domain (US Government) |
| ACS 2023 1-year PUMS (US Census Bureau) | graduate study, field demand | public domain (US Government) |
| IPEDS completions and directory files (NCES) | doctoral production, event studies | public domain (US Government) |
| Survey of Earned Doctorates by baccalaureate institution (NSF NCSES) | doctorate rate | public domain (US Government) |
| State unemployment rates (BLS LAUS via FRED); BLS OES national files and SOC crosswalks (Internet Archive copies); CPI-U (BLS via DBnomics) | entry conditions, demand index | BLS data public domain; FRED terms of use |
| LEO graduate outcomes, provider level (UK Department for Education) | UK pay and intake | Open Government Licence v3.0 |
| REF 2021 and REF 2014 results (UKRI) | UK department ratings | CC BY 4.0 |
| UCAS end-of-cycle provider × subject files | UK applications | UCAS terms of use |
| ORCID-derived academic mobility edges (Li 2026, Zenodo 10.5281/zenodo.19651302, version 20260419) | UK university rank G | CC BY 4.0 |
| ROR data dump v2.8 (Zenodo 10.5281/zenodo.20512981) | UK institution matching | CC0 1.0 |
| NRC Assessment of Research-Doctorate Programs, Excel data table, revised 29 April 2011 (National Academies Press) | positive control | personal, non-commercial use only; may not be posted or distributed; obtained manually and not redistributed; no programme-level value is written to any output |
| ABET accredited-programme search (public API), AACSB accreditation lists (Internet Archive captures and current pages), Nobel Prize API v2.1 | event studies | providers' public web content, used for counts; Nobel Prize API terms of use |

## Citation

```
@article{yang2026universities,
  author = {Yang, Haotian},
  title  = {Universities, not departments: where academic prestige meets graduate pay},
  year   = {2026},
  note   = {Code: https://github.com/soray42/universities-not-departments}
}
```

## Licence

The code is released under the MIT licence (`LICENSE`). The data remain under the terms of their providers (table
above).
