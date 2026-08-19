# Budget Plan — OPS Management System, Phase 1

**Client budget:** 300,000 EGP
**Window:** 10 August – 20 November 2026 (15 weeks)
**Team:** 1 Backend, 1 Frontend, 1 DevOps (part-time)
**Engagement model:** In-house salaried
**Live model:** `02-Budget-Plan.xlsx` — edit the blue cells on the Assumptions sheet and everything
recalculates.

---

## 1. Headline

| | |
|---|---:|
| Client budget | **300,000 EGP** |
| Labour | 258,919 EGP (86.3%) |
| Infrastructure and tooling | 16,140 EGP (5.4%) |
| Contingency | 24,941 EGP (8.3%) |
| **Total** | **300,000 EGP** |
| Person-months funded | **8.29** |
| Cost per person-month | 31,250 EGP |

Contingency is the balancing figure — calculated as `budget − labour − infrastructure` — so the
model always totals exactly the client's budget whatever the input rates are changed to.

**What this buys:** the Phase 1 scope defined in §3.1 of the technical proposal, and nothing more.

---

## 2. Labour

| Role | Monthly (EGP) | FTE | Months | Total (EGP) | Share |
|---|---:|---:|---:|---:|---:|
| Backend engineer | 34,000 | 1.00 | 3.45 | 117,376 | 39.1% |
| Frontend engineer | 27,000 | 1.00 | 3.45 | 93,211 | 31.1% |
| DevOps engineer | 35,000 | 0.40 | 3.45 | 48,331 | 16.1% |
| **Labour subtotal** | | | | **258,919** | **86.3%** |

### Rate benchmark

Egyptian mid-level software engineering salaries in 2026 run **18,000–42,000 EGP/month**, with a
median around 27,000 and a software-house median near 26,000. At an average of 31,250 EGP per
person-month this budget sits **mid-band** — enough to hire and retain competent mid-level
engineers, not enough to hire seniors.

The backend rate is set highest of the two full-time roles deliberately. That role carries the
four integrations, item-level splitting, the financial engine and the returns module — it is the
role where a weak hire loses the timeline.

### Why DevOps is 0.4 FTE

Effort is front-loaded into Sprint 1 (environments, CI/CD, secrets, backups) and Sprint 5 (load
test), with light steady-state work in between. The recommended two-node deployment involves no
Kubernetes, no managed message broker and no multi-region work. Hours are better spent on the
integrations, which is where the delivery risk actually sits.

### A note on the frontend role

Under the recommended Laravel + Filament stack the frontend engineer is **not** building React
screens for the ops console — Filament generates those. Their scope is Filament theming and custom
pages, dashboards and charts, the vendor portal UX, Livewire/Alpine interaction work, AWB and
statement print layouts, and the Phase 1b customer returns portal.

**This matters for hiring.** A React-only specialist would be under-utilised for three months. The
right profile is someone comfortable with Blade, Livewire and Alpine.

---

## 3. Infrastructure and Tooling

Five months funded (August–December 2026), covering hypercare past Black Friday.
EUR converted at 55.00 EGP, USD at 50.25 EGP.

| Item | Spec | Native | EGP/month | Total (EGP) |
|---|---|---:|---:|---:|
| Application node | Hetzner CX43 — 8 vCPU / 16 GB | €15.99 | 879 | 4,397 |
| Data node | Hetzner CX33 — 4 vCPU / 8 GB | €8.49 | 467 | 2,335 |
| Staging | Hetzner CX23 — 2 vCPU / 4 GB | €5.49 | 302 | 1,510 |
| Automated backups | 20% of server cost | €5.99 | 329 | 1,647 |
| Object storage | Storage Box 1 TB | €5.00 | 275 | 1,375 |
| Source control / CI | GitHub Team, 3 seats | $12.00 | 603 | 3,015 |
| Transactional email | Amazon SES | $5.00 | 251 | 1,256 |
| DNS / TLS / WAF / CDN | Cloudflare free tier | — | 0 | 0 |
| Error tracking | Sentry free tier | — | 0 | 0 |
| Uptime monitoring | Uptime Kuma, self-hosted | — | 0 | 0 |
| Domain | Annual | — | 120 | 600 |
| **Total** | | | **3,108** | **16,140** |

At 5.4% of budget this is a deliberately small footprint. The workload — 3,223 items in the
busiest month to date — does not justify managed Kubernetes or a managed database, and every EGP
not spent on infrastructure is available for engineering.

### PDPL hosting fallback

If legal counsel rejects EU hosting (see proposal §11), Egyptian local hosting is estimated at
3,000–8,000 EGP/month — an increase of roughly **4,000 to 28,500 EGP** over the window, which must
come from contingency. At the top of that range it would consume most of the contingency line.

This is an indicative range, not a quote. **Obtaining two firm local quotes is a Sprint 0 action
item**, and the hosting decision must be confirmed by end of Sprint 2. Migrating hosting later in
the project is not affordable in this timeline.

---

## 4. Cash Flow

| Month | Weeks | Backend | Frontend | DevOps | Infra | Monthly total | Cumulative |
|---|---:|---:|---:|---:|---:|---:|---:|
| Aug 2026 | 3.0 | 23,475 | 18,642 | 9,666 | 3,228 | 55,011 | 55,011 |
| Sep 2026 | 4.3 | 33,648 | 26,721 | 13,855 | 3,228 | 77,452 | 132,463 |
| Oct 2026 | 4.4 | 34,430 | 27,342 | 14,177 | 3,228 | 79,177 | 211,640 |
| Nov 2026 | 3.3 | 25,823 | 20,507 | 10,632 | 3,228 | 60,190 | 271,830 |
| Dec 2026 | 0.0 | — | — | — | 3,228 | 3,228 | 275,058 |
| **Committed** | **15.0** | **117,376** | **93,211** | **48,331** | **16,140** | **275,058** | |
| Contingency (undrawn) | | | | | | 24,941 | |
| **Reconciles to budget** | | | | | | **300,000** | |

August is lighter because the engagement begins on the 10th. December carries infrastructure only,
for hypercare.

---

## 5. Where the In-House Returns Module Costs More

Requirement §5 changed from integrating with E-stebdal to building the capability in-house. The
delta, in engineering days:

| Work item | Integration | In-house build | Delta |
|---|---:|---:|---:|
| Adapter / API client | 5 d | — | −5 d |
| Eligibility rules engine | — | 4 d | +4 d |
| Reason taxonomy + admin | 1 d | 2 d | +1 d |
| Approval workflow + console | 2 d | 6 d | +4 d |
| Reverse logistics | 2 d | 3 d | +1 d |
| Exchange fulfilment | 2 d | 5 d | +3 d |
| Refund ledger | 1 d | 4 d | +3 d |
| Warehouse QC receipt | — | 2 d | +2 d |
| **Total** | **13 d** | **26 d** | **+13 d (≈3 weeks)** |

**How it was absorbed:** the customer-facing self-service portal (~8 days) moved to Phase 1b, and
the risk contingency a no-public-API dependency would have required is no longer needed.

**What it cost:** Phase 1 now has **no schedule slack.** Any scope added after Sprint 0 must
displace something else. This is the single most important caveat in this budget, and it is stated
here rather than discovered in October.

---

## 5b. Scope Change — Authentication & Super Admin Console

Added after the first proposal draft. Phase 1 had no slack, so the cost is paid by displacement
rather than absorbed silently.

**Added to Phase 1** — the half you cannot operate through peak week without:

| Item | BE | FE | Cost (EGP) | Why it cannot wait |
|---|---:|---:|---:|---|
| Login, session policy, 2FA (Fortify) | 1.5 d | — | 2,429 | Gates everything else |
| User management + roles UI | 1.0 d | 0.5 d | 2,262 | Onboarding/offboarding during peak |
| Permission matrix editor | 0.5 d | 1.0 d | 2,095 | Role tuning without a deployment |
| Integrations console + credential rotation | 2.0 d | 1.0 d | 4,524 | Rotating a leaked key, webhook health |
| System health + dead-letter replay | 2.0 d | 0.5 d | 3,881 | Replaying a failed webhook at 2am |
| **Total added** | **7.0 d** | **3.0 d** | **15,190** | **10 engineering days** |

**Displaced to Phase 1b** — read-only surfaces that pay for it:

| Item | BE | FE | Cost (EGP) | Why it is safe to move |
|---|---:|---:|---:|---|
| Basic vendor scorecard (§10) | 2 d | 2 d | 5,810 | Read model over data captured from day one |
| Executive dashboard (§11) | 1 d | 2 d | 4,190 | Same — ships with full history |
| Vendor product submission (§8.1) | 2 d | 2 d | 5,810 | Vendors onboard through Ops today |
| **Total displaced** | **5 d** | **6 d** | **15,810** | **11 engineering days** |

**Net effect on Phase 1: −1 day, −619 EGP. The trade pays for itself.**

Nothing is lost retroactively. All three displaced surfaces are *views* over data the system
collects from go-live, so they arrive three weeks later carrying full history. Vendor product
submission is the only behavioural change, and vendors are onboarded through Ops today anyway.

### Why not fund it from contingency

| Option | Cost | Contingency left | Verdict |
|---|---:|---:|---|
| **1. Displace 11 days of read-only UI** | 0 | 24,941 | **Recommended** |
| 2. Draw on contingency | 15,190 | 9,751 | Too thin — risk R1 (PDPL hosting fallback) alone could need 28,500 |
| 3. Increase the budget | ~16,000–20,000 | 24,941 | Client's call — keeps every Phase 1 surface |

---

## 6. Phase 1b and Phase 2 — Not Funded by This Budget

Presented so the client can plan; neither is covered by the 300,000 EGP.

### Phase 1b — 23 November to 11 December 2026

| Deliverable | BE | FE | Ops | Cost (EGP) |
|---|---:|---:|---:|---:|
| Customer self-service returns portal | 4 d | 8 d | 1 d | 18,429 |
| Returns analytics dashboard | 4 d | 3 d | — | 10,333 |
| E-stebdal parallel-run validation | 2 d | 1 d | 1 d | 6,190 |
| Super Admin: business rules engine UI | 3 d | 2 d | — | 7,429 |
| Super Admin: report builder + scheduling | 2 d | 2 d | — | 5,810 |
| Basic vendor scorecard *(displaced from P1)* | 2 d | 2 d | — | 5,810 |
| Executive dashboard *(displaced from P1)* | 1 d | 2 d | — | 4,190 |
| Vendor product submission *(displaced from P1)* | 2 d | 2 d | — | 5,810 |
| **Total** | **20 d** | **22 d** | **2 d** | **64,000** |

Phase 1b has grown from 3 weeks of work to roughly 44 engineering days. **That no longer fits the
23 Nov – 11 Dec window at the current team size** — expect it to run into January alongside the
E-stebdal cutover, or to need prioritising down. Flagged here rather than discovered in December.

### Phase 2 — from January 2027

| Deliverable | Requirement | BE | FE | Ops | Cost (EGP) |
|---|---|---:|---:|---:|---:|
| Raw fabric inventory, BOM, forecasting | 7.2 | 15 d | 6 d | — | 32,000 |
| Second courier adapter | 3.1 | 10 d | 3 d | 1 d | 21,714 |
| Advanced vendor scorecard and penalties | 10 | 10 d | 6 d | — | 23,905 |
| Executive BI dashboard | 11 | 8 d | 6 d | — | 20,667 |
| Automated Paymob Send disbursement | 8.6 | 8 d | 2 d | 1 d | 17,190 |
| Automated recall / win-back workflows | — | 7 d | 4 d | — | 16,476 |
| **Total** | | **58 d** | **27 d** | **2 d** | **131,952** |

### Combined programme

| Phase | Cost (EGP) |
|---|---:|
| Phase 1 | 300,000 |
| Phase 1b | 64,000 |
| Phase 2 | 131,952 |
| **Total** | **495,952** |

---

## 7. Sensitivity

### Budget

| Scenario | Budget (EGP) | Person-months | Δ | Scope consequence |
|---|---:|---:|---:|---|
| −20% | 240,000 | 6.53 | −1.76 | Loses settlement automation **and** vendor scorecard |
| −10% | 270,000 | 7.41 | −0.88 | Vendor scorecard deferred to Phase 1b |
| **As proposed** | **300,000** | **8.29** | — | **Full Phase 1 scope. Zero slack.** |
| +10% | 330,000 | 9.17 | +0.88 | Restores ~3 weeks of slack — the highest-value addition |
| +20% | 360,000 | 10.05 | +1.76 | Pulls the customer returns portal into Phase 1 |

Given that Phase 1 currently carries no slack, **+10% buys risk reduction rather than features** —
and on a fixed external deadline that is usually the better purchase.

### Engagement model

This is the assumption the whole budget rests on.

| Model | Rate multiple | Person-months | Verdict |
|---|---:|---:|---|
| **In-house salaried** | 1.0× | **8.29** | **Phase 1 scope is achievable** |
| Freelance / contractor | 1.5× | 5.52 | Two thirds the capacity — Phase 1 must shed settlement, scorecard and vendor portal |
| Agency / software house | 2.5× | 3.31 | Under half — 300,000 EGP funds an MVP only: Shopify sync, item splitting, shipping. Returns and the financial engine would not fit |

If the engagement model changes, this budget must be rebuilt, not adjusted.

### Schedule levers

| Lever | Cash cost | Time recovered | Preference |
|---|---:|---|---|
| 1. Cut scope — defer settlement automation and scorecard to Phase 1b | 0 | ~2 weeks | **Preferred** |
| 2. Extend timeline — go live in December, after Black Friday | 0 | Unlimited | Second |
| 3. Add a 2nd backend engineer for Sprints 4–6 | ~102,000 | ~3 weeks | Least effective |

Lever 3 only works if committed by **mid-September**. Later than that, onboarding drag exceeds the
capacity added.

---

## 8. Return on Investment

The case for this system is recovered revenue, not saved data entry.

### Baseline, from the client's own data

| Measure | Value |
|---|---:|
| Item rows analysed (1 Jan – 8 Aug 2026) | 18,341 |
| Failed delivery (`FD Allow Open Shipment`) | 3,743 |
| Returned to origin (RTO) | 2,359 |
| **Total failed items** | **6,102** |
| Average item value | 897 EGP |
| **GMV that shipped and came back** | **~5,473,000 EGP** |
| Failed items actually worked (`Send messages`) | 1,430 (23%) |
| Recovered into new orders | 273 |
| **Current recovery rate** | **19.1%** |
| **Failed items never worked** | **4,672** |

### Recovery scenarios, annualised

| Scenario | Recovered items / yr | Recovered GMV / yr | Assumption |
|---|---:|---:|---|
| **Conservative** | ~765 | **~686,000 EGP** | Half the current recovery rate, applied only to items never worked |
| At parity | ~1,529 | ~1,372,000 EGP | Current 19.1% rate across all failed items, net of what is recovered today |

**Conservative recovered GMV is 2.3× the Phase 1 build cost.**

The conservative case is deliberately pessimistic: it halves the team's own demonstrated recovery
rate, on the reasonable assumption that the 1,430 items they chose to work were the most promising
ones.

### Honest framing

These are **GMV figures, not profit.** The platform realises commission and margin on recovered
orders, not the full order value. At any plausible commission rate the conservative case still
exceeds the build cost within the first year — and unlike a one-off saving, the recall queue is a
permanent operational capability.

### Recurring offsets, not counted above

| Offset | Value |
|---|---|
| E-stebdal subscription retired at January 2027 cutover | **Client to confirm** — enter on the ROI sheet of the workbook |
| Manual data entry displaced | ~118 rows/day across 32 columns, with cross-system lookups per row |
| Flex-shipping reconciliation automated | 3,181 compensations over 7 months, ~15 per working day matched by hand |

---

## 9. Assumptions and Their Sources

| Assumption | Value | Basis |
|---|---|---|
| Client budget | 300,000 EGP | Client-stated |
| Engagement model | In-house salaried | **Client-confirmed** |
| Project window | 10 Aug – 20 Nov 2026 | 7 days before Black Friday |
| Weeks per month | 4.345 | 52 ÷ 12 |
| USD / EGP | 50.25 | Market rate, August 2026 |
| EUR / EGP | 55.00 | Derived at EURUSD ≈ 1.09 |
| Working days per month | 21 | Used for Phase 1b/2 day-rate conversions |
| Salary band reference | 18,000–42,000 EGP/month | Egyptian mid-level market, 2026 |
| Hetzner CX pricing | €15.99 / €8.49 / €5.49 | Published pricing, August 2026 |

### Two pricing notes worth flagging

**Hetzner repriced in June 2026.** The CPX and CCX lines rose 113–175% — CCX13 went from €15.99 to
€42.99. The **CX line is now the value option**, and any cost model built on older CPX pricing is
out of date. This budget uses current CX pricing.

**The Egyptian local hosting range is not a quote.** Providers in this segment do not publish
comparable pricing. The 3,000–8,000 EGP/month figure is indicative and must be replaced with firm
quotes in Sprint 0.

---

## 10. What This Budget Does Not Cover

Stated explicitly to avoid ambiguity later:

- Phase 1b and Phase 2 (§6) — 195,952 EGP combined
- E-stebdal subscription through the parallel-run period to January 2027
- PDPL legal fees, licence application costs, or the Data Protection Officer appointment
- Third-party integration fees charged by Shopify, Bosta or Paymob
- Hardware for warehouse QC stations
- Ops team training time and the two weeks of duplicated effort during the parallel run
- Any scope added after Sprint 0 — see §5

---

*Model: `02-Budget-Plan.xlsx`. Built by `scripts/build_budget.py`, checked by
`scripts/verify_budget.py` (157 formulas, references resolved, arithmetic confirmed, total lands
on 300,000 EGP exactly). Operational figures derive from `POC - Youssey Excelsheet.xlsx` via
`scripts/extract_data.py`.*
