# Deliverables — OPS Management System

Proposal pack for replacing the manual Google Sheet operation with an automated Operations
Management System, delivered before Black Friday (27 November 2026).

## What to open first

| If you are… | Start with |
|---|---|
| The client, in a meeting | `03-Prototype/index.html` — click through the screens |
| The client, reviewing offline | `01-Technical-Proposal.docx` and `02-Budget-Plan.xlsx` |
| An engineer picking up the build | `01-Technical-Proposal.md` §4–§6, then `diagrams/` |
| Finance | `02-Budget-Plan.xlsx` — edit the blue cells on the Assumptions sheet |

## Contents

```
01-Technical-Proposal.md      Engineering source of truth — HLD, LLD, hosting, timeline, risks
01-Technical-Proposal.docx    Client-ready Word version, 24 diagrams embedded, with a TOC
02-Budget-Plan.md             Budget narrative and sensitivity analysis
02-Budget-Plan.xlsx           Live budget model — 157 formulas, totals exactly 300,000 EGP
03-Prototype/index.html       Self-contained clickable demo, 29 screens across 6 roles, no server needed
diagrams/                     24 diagrams as .mmd source, .svg and 2x .png
data/                         Extracted and anonymised profiles of the client's workbook
```

### The Word document's table of contents

Word populates TOC page numbers on demand. On first open, right-click the contents table and
choose **Update Field → Update entire table**.

### The budget workbook

Formulas are written without cached values, so **open it in Excel or Numbers** — both recalculate
on open. Lightweight preview tools may show blank cells until then. Contingency is the balancing
figure (`budget − labour − infrastructure`), so the total always lands on the client budget
exactly, whatever the input rates are changed to.

### The prototype

One file, no server, no internet. Open `03-Prototype/index.html` in any browser. It is seeded with
**600 real item rows** sampled from the client's own workbook, so vendors, SKUs, statuses,
governorates and return reasons are all genuine.

**Sign in with any of the six role chips on the login screen** — no password needed. Each role sees
a different set of screens, enforced by the same rules as the built system: sign in as **CS Agent**
and deep-link to `#/financial` to watch the guard refuse it. **Super Admin** additionally sees the
Configuration group. Super Admin and Finance pass through a two-factor step; any six digits work.
The **Requirements Coverage** screen walks the traceability matrix.

Free-text customer and CS notes are redacted; everything else is the client's own business data.

## Three things worth knowing before the meeting

1. **The business case is recovered revenue, not saved data entry.** 6,102 items failed delivery or
   returned to origin in seven months — roughly 5.5M EGP of GMV that shipped and came back. Only
   23% were worked through the recall queue, at a 19.1% recovery rate. Systematising that queue is
   worth an estimated 686,000–1,372,000 EGP of recovered GMV a year against a 300,000 EGP build.

2. **Returns are built in-house, replacing E-stebdal.** This removes the largest integration risk
   in the project (E-stebdal publishes no public API) and unlocks analytics no generic SaaS returns
   app provides. It costs about three person-weeks more than the integration it replaces, absorbed
   by moving the customer self-service portal to Phase 1b.

3. **Phase 1 has no schedule slack, and PDPL is a hard external date.** Egypt's Personal Data
   Protection Law reaches full enforcement on 31 October 2026, four weeks before Black Friday. The
   cross-border transfer licence application must start in Sprint 0 — the client needs it for
   Shopify regardless of where this system is hosted.

## Reproducing everything

All artifacts are generated. The source workbook is read-only and never modified.

```bash
python3 scripts/extract_data.py      # workbook -> data/*.json
python3 scripts/build_budget.py      # -> 02-Budget-Plan.xlsx
python3 scripts/verify_budget.py     # checks references + arithmetic
python3 scripts/build_prototype.py   # template + data -> 03-Prototype/index.html
node    scripts/build_docx.js        # 01-Technical-Proposal.md -> .docx
```

Diagrams are rendered from `diagrams/*.mmd` with mermaid-cli:

```bash
cd deliverables/diagrams && for f in *.mmd; do mmdc -i "$f" -o "${f%.mmd}.svg" -b transparent; mmdc -i "$f" -o "${f%.mmd}.png" -b white -s 2; done
```
