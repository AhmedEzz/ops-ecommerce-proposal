# Operations Management System
## Technical Proposal — HLD, LLD, Delivery Plan

**Prepared for:** Marketplace Operations
**Version:** 1.0
**Date:** 8 August 2026
**Target go-live:** 20 November 2026 (7 days before Black Friday, 27 November 2026)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State Analysis](#2-current-state-analysis)
3. [Scope](#3-scope)
4. [High-Level Design](#4-high-level-design)
5. [Low-Level Design](#5-low-level-design)
6. [The In-House Returns & Exchanges Module](#6-the-in-house-returns--exchanges-module)
7. [Technology Stack Selection](#7-technology-stack-selection)
8. [Hosting & Infrastructure](#8-hosting--infrastructure)
9. [Delivery Plan & Timeline](#9-delivery-plan--timeline)
10. [Risks & Mitigations](#10-risks--mitigations)
11. [Data Protection & PDPL Compliance](#11-data-protection--pdpl-compliance)
12. [Requirements Traceability Matrix](#12-requirements-traceability-matrix)
13. [Appendix — Diagram Index](#13-appendix--diagram-index)

---

## 1. Executive Summary

### 1.1 What this proposal covers

A centralised, event-driven Operations Management System that replaces the manually-maintained
Google Sheet currently used to run marketplace back-office operations. The system automates data
synchronisation with Shopify, Bosta and Paymob, introduces item-level operational control, brings
returns and exchanges in-house, adds a self-service vendor portal, and produces auditable
item-level financials.

### 1.2 The finding that should drive this investment

The business case here is not data-entry savings. It is recovered revenue.

Analysis of the client's own operational data — 18,341 item-level rows spanning 1 January to
8 August 2026 — shows that **only 49.3% of dispatched items are delivered**. The remainder:

| Outcome | Items | Share |
|---|---:|---:|
| Delivered | 9,036 | 49.3% |
| Failed Delivery (`FD Allow Open Shipment`) | 3,743 | 20.4% |
| RTO (returned to origin) | 2,359 | 12.9% |
| Cancelled | 1,307 | 7.1% |
| Returned / Under Return | 627 | 3.4% |
| In flight or unclassified | 1,269 | 6.9% |

**6,102 items failed delivery or were returned to origin in seven months.** At an average item
value of 897 EGP, that is roughly **5.5M EGP of GMV that left the warehouse and came back**.

The sheet shows a recovery process already exists but is applied inconsistently. Of those 6,102
failed items, only **1,430 (23%) were worked** through the recall workflow (`Send messages`), and
of those, **273 converted into new orders — a 19.1% recovery rate**. The other 4,672 failed items
were never systematically worked at all.

**The single highest-value function of this system is turning that ad-hoc recall into a managed
queue.** Applying the team's own demonstrated recovery rate to the unworked population:

| Scenario | Assumption | Recovered items / yr | Recovered GMV / yr |
|---|---|---:|---:|
| Conservative | Half the current recovery rate (9.5%) on unworked items | ~760 | **~683,000 EGP** |
| At parity | Current 19.1% rate applied to all failed items | ~1,530 | **~1,370,000 EGP** |

These are GMV figures, not profit — the platform realises commission and margin on them, not the
full value. But against a **300,000 EGP** build cost, even the conservative case recovers more than
twice the investment in GMV within the first year, and the queue is a permanent capability
thereafter.

Secondary, harder-to-quantify returns: elimination of ~118 rows/day of manual multi-system data
entry across 32 columns, retirement of the E-stebdal subscription, and the end of manual
reconciliation of 3,181 flex-shipping compensations.

### 1.3 Four decisions embedded in this proposal

**Returns and exchanges are built in-house, not integrated.** The client is retiring E-stebdal.
This removes the largest integration risk in the project — E-stebdal publishes no public API, so
any integration would have been reverse-engineered and fragile — and converts it into scoped,
estimable build work. It also unlocks analytics no generic SaaS returns app can provide, because
the team already maintains a 56-value return-reason taxonomy with stakeholder attribution.
Returns are not an edge case here: **6,705 items (36.6%) pass through a return or RTO path.**

**The recommended stack is Laravel 11 + Filament 3 on PostgreSQL.** Scored against NestJS/Next.js,
Django/React and .NET/Blazor (§7), it wins decisively on the criterion that dominates a 13-week,
two-developer delivery: how fast a heavy-CRUD operations console and vendor portal can be built.

**The platform is administered, not hand-tuned.** Six roles behind a real login, with two-factor
mandatory for the two roles that can move money, and a Super Admin console covering integrations,
users, permissions and system health. The principle throughout is that ops staff must be able to
rotate a credential or replay a failed webhook during peak week without an engineer. See §5.11.

**Hosting is recommended in the EU (Hetzner) at ~2,255 EGP/month, with a mandatory parallel legal
workstream.** Egypt's PDPL enforcement begins 31 October 2026 and a cross-border transfer licence
is required by 2 November 2026 — four weeks before Black Friday. The client already has this
exposure through Shopify, so the licence is required regardless of where this system is hosted.
This must start in Sprint 0. See §11.

### 1.4 Budget and timeline position — stated plainly

The 300,000 EGP budget funds approximately **8.3 person-months** at Egyptian mid-level salary
rates. That is enough for the Phase 1 scope defined in §3 and nothing more.

Bringing returns in-house is roughly **three person-weeks larger** than the E-stebdal integration
it replaces. That has been absorbed by moving the *customer-facing* self-service returns portal to
Phase 1b (23 November – 11 December), after code freeze and before the December return peak. The
CS-operated returns console — which matches how the team already works — remains in Phase 1.

**The consequence: Phase 1 has no remaining schedule slack.** Any scope added after Sprint 0 must
displace something else. This is stated now rather than discovered in October, and §9.5 sets out
the three levers available if it becomes a problem.

That rule has already been applied once. Adding authentication and the Super Admin console (§5.11)
costs **~10 days inside Phase 1**, and rather than quietly absorb it, three read-only surfaces move
to Phase 1b to pay for it: the basic vendor scorecard, the executive dashboard and vendor product
submission. All three are screens over data the system collects from day one, so they lose no
history — they simply arrive three weeks after go-live. The alternative, funding the console from
contingency, would leave too little against the PDPL hosting risk in §11.

---

## 2. Current State Analysis

Every figure in this section is derived from `POC - Youssey Excelsheet.xlsx` by the extraction
script at `scripts/extract_data.py`. Raw profiles are in `deliverables/data/`.

### 2.1 Volume and scale

| Measure | Value |
|---|---|
| Period covered | 1 Jan 2026 – 8 Aug 2026 (~7 months) |
| Item-level rows | 18,341 |
| Unique customer orders | 12,219 |
| Active vendors | 82 |
| Gross merchandise value | 16,452,697 EGP |
| Shipping fees collected | 1,153,350 EGP |
| Average item value | 897 EGP |
| Items per order | 1.50 |
| Multi-vendor orders | 4,110 items (22.4%) |

Monthly run-rate has grown from 1,692 items in January to a 3,223-item peak in June — roughly
**90% growth in six months**. Black Friday volume should be planned at 3–5× the current monthly
peak, i.e. **10,000–16,000 items in November**.

| Month | Items | GMV (EGP) | Delivered | Delivery rate |
|---|---:|---:|---:|---:|
| 2026-01 | 1,692 | 2,175,867 | 840 | 49.7% |
| 2026-02 | 1,651 | 1,870,827 | 879 | 53.2% |
| 2026-03 | 2,117 | 1,844,341 | 1,168 | 55.2% |
| 2026-04 | 2,526 | 2,243,500 | 1,291 | 51.1% |
| 2026-05 | 3,074 | 2,634,423 | 1,649 | 53.6% |
| 2026-06 | 3,223 | 2,634,201 | 1,724 | 53.5% |
| 2026-07 | 2,581 | 2,522,311 | 1,336 | 51.8% |
| 2026-08 (partial) | 507 | 527,227 | 149 | 29.4% |

### 2.2 The manual process being replaced

The `Copy of Orders` sheet carries 32 columns per item, populated by hand from four systems:

- **From Shopify** — order date, order number, SKU, item name, item price, shipping fees, payment
  method, line-item quantity, governorate, area
- **From Bosta** — AWB state, AWB creation date, pickup date, delivery date, final status, flex
  shipping status
- **Computed by hand** — CS SLA, FM SLA, delivery SLA, return SLA, vendor/customer order mapping,
  multi-vs-single classification
- **Entered by ops judgement** — stakeholder attribution, reason, vendor penalty, penalty date,
  comments, recall status, QC checkbox

At ~118 rows per working day across 32 columns, with cross-system lookups for each, this is a
sustained multi-hour daily workload split across the CS and ops team — and it is the source of the
data-quality problems in §2.5.

### 2.3 Vendor performance varies enormously — and is invisible today

This is the second-strongest argument for the system. Delivery rate by vendor, top 12 by volume:

| Vendor | Items | GMV (EGP) | Delivery rate | RTO |
|---|---:|---:|---:|---:|
| MALABISY | 2,942 | 2,734,738 | 50% | 479 |
| Xo style | 2,897 | 3,482,894 | **45%** | 376 |
| Onda | 1,431 | 383,909 | **71%** | 157 |
| Hoolt | 1,392 | 674,065 | 64% | 166 |
| Leocansa | 1,318 | 1,817,980 | 51% | 188 |
| Carinawear | 998 | 599,308 | 55% | 124 |
| Clue | 639 | 664,118 | 45% | 89 |
| Mr.joe | 564 | 881,487 | 52% | 75 |
| Shoeroom | 514 | 730,233 | 58% | 77 |
| Libra | 509 | 769,615 | 51% | 64 |
| Aida | 439 | 522,332 | 50% | 58 |
| Menaksha | 431 | 184,630 | 56% | 61 |

**Onda delivers 71% of what it ships. Xo style delivers 45% — on 2,897 items and 3.48M EGP of
GMV.** A 26-point spread between two high-volume vendors is a commercial lever worth more than the
entire cost of this project, and today it is not visible to anyone without manual analysis. The
Vendor Score Card (§12, requirement 10) makes it a standing metric.

### 2.4 Returns, exchanges and the reason taxonomy

| Measure | Value |
|---|---:|
| Items with a return date or RTO/Returned status | 6,705 (36.6%) |
| Explicit customer return requests | 773 |
| Exchange-tagged items | 1,612 |
| Distinct return/failure reasons in use | **56** |
| Items with a vendor penalty applied | 319 |
| Flex shipping compensations | 3,181 applied, 141 rejected |

Reasons are already attributed to an owning stakeholder — this is a mature operational practice
that the new system should preserve exactly, not replace:

| Stakeholder | Distinct reasons | Items |
|---|---:|---:|
| Commercial | 33 | 2,881 |
| Marketing | 24 | 2,599 |
| Customer Behavior | 23 | 1,831 |
| No Answer | 1 | 501 |
| Ops | 5 | 308 |
| CS | 3 | 179 |
| Tech | 2 | 28 |
| 3PL | 2 | 11 |

The highest-frequency reasons point directly at fixable causes:

| Reason | Count | What it implies |
|---|---:|---|
| No Answer – No Response Received | 1,647 | Contactability problem — recall queue |
| Open Shipping – No Response Received | 1,354 | Open-package policy friction |
| Size Issue – Returned (No Exchange) | 1,058 | **Lost sale that should have been an exchange** |
| Refused – No Clear Reason | 760 | Data-capture gap at the doorstep |
| Material Quality Below Expectation | 488 | Vendor QC / listing accuracy |
| OOS | 409 | Stock visibility |
| Size Issue – Exchange Created | 280 | The successful path — only 21% of size issues |
| Customer Changed Mind | 282 | Genuine attrition |
| Refused – Policy Not Available | 142 | **Policy not findable at the doorstep** |
| Missing size chart | 127 | **One-line catalogue fix** |
| Defected Item – Vendor Fault | 115 | Chargeable to vendor |

Two of these are worth calling out. **`Size Issue – Returned (No Exchange)` at 1,058 against
`Size Issue – Exchange Created` at 280** means roughly four out of five size problems end as a
lost sale rather than a retained one — almost certainly because replacement stock availability
isn't visible at the moment the customer calls. The in-house exchange flow (§6) makes that check
the first step. And **`Missing size chart` at 127** is a catalogue defect that a required field at
vendor upload would largely eliminate.

### 2.5 Data quality problems the new system must eliminate

Manual entry has produced inconsistencies that make reliable reporting impossible:

- **Vendor names are not controlled.** `Xo style` and `Xo Style` are recorded separately. 91 raw
  distinct values normalise to 82 real vendors.
- **Stakeholder values are not controlled.** `Customer Behavior` and `Customer behavior` are
  separate values.
- **Payment method has 13 spellings** for what are really 6 tenders, including
  `cash on Delivery (COD)` (8 rows) and `CAsh on Delivery (COD)` (2 rows). Two rows contain a
  *date* in the payment method column.
- **970 rows (5.3%) have no final status at all** and are effectively invisible to any status
  report.
- **5,495 rows (30%) have no governorate**, so geographic performance analysis is unreliable.
- **SLA columns contain stray values** — a `Return SLA` of 39,453 appears where a date serial was
  pasted into a day-count column.
- **Roughly a third of product names are double-encoded.** Names such as
  `Faux Suede Knit Ankle Ugg Boots â€“ Beige` show a UTF-8 en-dash that has been read back as
  cp1252 — the signature of copy-pasting between Shopify and the sheet. It is repairable
  programmatically (the migration script does so), but it means product names cannot currently be
  matched reliably by string comparison.

Every one of these disappears when the values become foreign keys to lookup tables populated by
integration rather than typed by hand. They are not criticisms of the ops team — they are the
unavoidable result of maintaining 32 columns by hand across four systems, and they are precisely
what the migration in Sprint 6 has to normalise.

### 2.6 Payment profile

**16,460 of 18,341 items (89.7%) are Cash on Delivery.** This is the single most important
architectural constraint in the financial design:

- The money is collected by **Bosta**, not by the payment gateway. Reconciliation must be
  three-way (Shopify ↔ Paymob ↔ Bosta COD remittance), not two-way.
- Revenue cannot be recognised at checkout. It is recognised on **delivery confirmation**.
- Refunds cannot be automated through the gateway for COD orders. They are manual settlements via
  wallet, InstaPay or bank transfer — which is why §6 models a refund as a *ledger obligation*
  rather than a payment instruction.
- Combined tenders exist and must be split at item level: 45 `Gift Card + COD`,
  25 `Paymob + COD`, 15 `Paymob + Gift Card`.

### 2.7 Geographic concentration

Cairo (7,585 items), Giza (2,821) and Alexandria (993) account for **89% of items with a recorded
governorate** (11,399 of 12,846). Delivery performance and courier selection should be modelled per governorate;
the long tail of 30 governorates behaves differently and currently has no separate SLA.

### 2.8 Supporting sheets

| Sheet | Rows | Value | Becomes |
|---|---:|---:|---|
| `Copy of Vendor Penalty` | 51 | 66,633 EGP | `penalties` + ledger entries |
| `Copy of Bosta Compensation` | 70 | 83,000 EGP | Flex-ship compensation events |
| `Copy of Return Bosta` | 22 | 26,306 EGP | `refunds` |
| `Copy of Staff Orders` | 4 | 4,722 EGP | Order channel flag |
| `OOS Orders` | 478 | — | OOS workflow (376 pure OOS + vendor delay reasons) |

The `OOS Orders` sheet also names specific vendors as delay causes (`Runes delay` 30,
`Hesper delay` 27, `Katee delay` 13), which belongs in the vendor scorecard rather than a
free-text column.

---

## 3. Scope

### 3.1 Phase 1 — live before Black Friday (target 20 November 2026)

Everything on the critical path of taking, shipping, and getting paid for a Black Friday order.

**Integration & data**
- Shopify synchronisation: orders, line items, statuses, fulfilments, via webhooks + Admin API
- Bosta integration: per-item AWB creation, status webhooks, reverse pickup, flex-ship detection
- Paymob integration: transaction sync (read-only), HMAC callback handling
- Webhook inbox with idempotency, retry and dead-letter handling
- Migration of all 18,341 historical rows with normalised vendor/status/reason vocabularies

**Order operations**
- Item-level order splitting (`#30537-1`, `#30537-2`, …) with the customer still seeing one order
- Per-item vendor assignment, fulfilment location resolution, business-model classification
- Item-level status state machine covering all four lifecycle scenarios
- OOS / cancellation workflow with partial-order handling
- Failed-delivery recall queue (the §1.2 revenue case)

**Returns & exchanges — in-house**
- CS-operated returns console
- Per-vendor eligibility rules engine
- 56-value reason taxonomy with stakeholder attribution, ported verbatim
- Approval workflow, Bosta reverse pickup, warehouse QC receipt
- Exchange order creation with original-snapshot carry-over
- Refund ledger with manual settlement step
- Vendor balance adjustment on return (requirement 8.7)

**Financial**
- Item-level margin engine across all three business models
- Append-only financial snapshots (requirement 6.3)
- Vendor ledger: commissions, penalties, adjustments, bonuses, return reversals
- Settlement calculation with statement generation
- Three-way payment reconciliation with exception queue

**Interfaces**
- Ops console replicating every Google Sheet column, with filters and export
- Vendor portal v1: login, order list, AWB PDF to dashboard and email, stock/price update,
  payout view, bank details
- Order, financial and inventory dashboards
- RBAC and full audit trail (requirement 12.4)

**Platform administration** *(see §5.11)*
- Authentication: email + password, with mandatory 2FA for Super Admin and Finance
- Super Admin console: Integrations & Keys, Users & Access, Roles & Permissions, System Health

### 3.2 Phase 1b — 23 November to 11 December 2026

After code freeze, before the December return peak.

- Customer-facing self-service return/exchange portal (order number + phone lookup, no account)
- Returns analytics dashboard by reason, vendor and stakeholder
- E-stebdal parallel-run validation
- **Super Admin: Business Rules and Reports screens** (§5.11)
- **The three surfaces displaced to fund the Phase 1 console** — basic vendor scorecard (§10),
  executive dashboard (§11) and vendor product submission (§8.1)

**On the displaced surfaces.** Data capture for all three continues from day one — only the screens
move. The scorecard and executive dashboard are read models over data the system is already
collecting, so nothing is lost retroactively and both light up with full history when they ship
three weeks after go-live. Vendor product submission is deferred because vendors are onboarded
through Ops today anyway, so the manual path already exists.

### 3.3 Phase 2 — after cutover (January 2027 onward)

- Raw fabric inventory, BOM and consumption tracking with depletion forecasting (req 7.2)
- Automated Paymob Send disbursement (req 8.6)
- Second courier adapter and per-item courier selection (req 3.1)
- Advanced vendor scorecard and automated penalty workflows (req 10)
- Executive BI dashboard (req 11)
- Automated recall/win-back campaign workflows

### 3.4 Why the scope is split this way

Phase 1 contains the CS-operated returns console rather than the customer portal because **CS
already performs this function manually today** — scenario 3 in the requirements explicitly has a
`Confirm Return (CS)` step. Digitising an existing human workflow is low-risk. Introducing a new
customer-facing self-service channel during peak week is not, and returns volume peaks in
December, not on Black Friday. Phase 1b lands it before that peak while leaving peak week frozen.

Raw fabric (req 7.2) is deferred because it has a complete manual fallback today and touches no
Black Friday order path. It is the largest single item in Phase 2.

The Super Admin console splits on the same principle. Integrations, users and system health are in
Phase 1 because **you cannot operate the platform through peak week without them** — replaying a
failed webhook, rotating a leaked credential, onboarding a temporary CS agent. Editing business
rules and building reports are in Phase 1b because Phase 1 ships those rules seeded by migration
and a fixed set of built-in reports, so the capability exists even before the editing UI does.

---

## 4. High-Level Design

### 4.1 System context

![System Context](diagrams/hld-01-system-context.svg)

The OPS system becomes the **system of record for operations**. Shopify remains the system of
record for the storefront and the customer-facing order. Bosta remains the system of record for
physical shipment state. Paymob remains the system of record for electronic payment.

The critical change from the original requirement: **Istibdal/E-stebdal is retired.** The OPS
system becomes the system of record for returns and exchanges and writes outcomes *into* Shopify,
rather than reading them out of a third-party app.

### 4.2 Container view

![Containers](diagrams/hld-02-containers.svg)

Five application-tier containers:

| Container | Responsibility | Why separate |
|---|---|---|
| Web / API | HTTP, authentication, RBAC, both portals | User-facing latency budget |
| Webhook Receiver | Signature verification, persist, return 200 fast | Must never block on business logic |
| Queue Workers | All integration, financial and notification work | Isolates slow/failing external calls |
| Scheduler | Reconciliation, settlement runs, SLA sweeps | Time-driven, not event-driven |
| Domain modules | Business logic, shared by all of the above | Single implementation of every rule |

The webhook receiver is deliberately thin. Its only job is to verify the signature, persist the
raw payload, and return HTTP 200 within a few hundred milliseconds. Every external provider
retries or disables endpoints that respond slowly; doing business logic inline is the most common
way integrations break under load — exactly when Black Friday traffic arrives.

### 4.3 Event architecture

![Event Architecture](diagrams/hld-03-event-architecture.svg)

The system is event-driven end to end (requirement 12.3). Three design rules:

**Idempotency at the boundary.** `integration_events` carries a unique constraint on
`(source, external_id)`. Providers re-deliver webhooks routinely; the unique index makes a
duplicate delivery a no-op rather than a duplicate AWB or a double ledger posting.

**Ordering is not assumed.** Couriers deliver status events out of order. The item state machine
rejects illegal transitions rather than trusting arrival sequence, and logs the anomaly.

**Failure is visible, not silent.** After N retries an event moves to a dead-letter queue that
alerts ops. The raw payload is retained so the event can be replayed after a fix — no data is lost
to a transient bug.

### 4.4 Deployment topology

![Deployment](diagrams/hld-04-deployment.svg)

A deliberately modest two-node footprint plus staging. At a 3,200 item/month run-rate — even at 5×
Black Friday load — this workload does not justify Kubernetes, managed message brokers or
multi-region. Every DevOps hour spent on infrastructure sophistication is an hour not spent on the
integrations that carry the actual risk.

---

## 5. Low-Level Design

### 5.1 Entity-relationship model

![ERD](diagrams/hld-05-erd.svg)

### 5.2 Three design decisions that define the system

These are the points where this system is easy to get wrong, and where a wrong choice is expensive
to reverse after go-live.

#### 5.2.1 `order_items` is the aggregate root, not `orders`

Requirement 2.1 asks for item-level operations. The temptation is to model orders as the primary
entity and hang items off them. That fails the moment a three-vendor order needs three different
statuses, three AWBs and three margin calculations — which, at 4,110 multi-vendor item rows, is
22% of volume.

Every status, cost, margin, commission, shipment, return and ledger entry attaches to
`order_items`. The customer-facing order number is a **presentation concern**: the customer sees
`#30537`, the system operates on `30537-1`, `30537-2`, `30537-3`.

The practical consequence is that an OOS item from one vendor no longer blocks the other two — see
`act-02-oos-cancellation`.

#### 5.2.2 `financial_snapshots` is append-only

Requirement 6.3 is explicit: if margin changes tomorrow, historical orders keep their original
values. The implementation rule is absolute — **never UPDATE a snapshot row.** Write a new row with
an `effective_at` timestamp and a `reason`, and read the row that was current as of the order date.

This is what makes flex-shipping compensation (§6, `act-07`) work correctly: a compensation
confirmed six weeks after the sale appends a new snapshot dated to the confirmation, leaving the
item's margin at time of sale intact and attributing the improvement to a date.

#### 5.2.3 Returns post reversing ledger entries and never mutate the original snapshot

Requirements 6.3 (immutable history) and 8.7 (deduct returned items from vendor balance) appear to
conflict. They do not, if returns are modelled as **double-entry reversals**.

When a return is accepted, the system posts a new `vendor_ledger_entries` row of type
`return_reversal` with a negative amount and a `reverses_entry_id` pointing at the original `sale`
entry. The original sale entry and the original financial snapshot are untouched. The vendor's
current balance is the sum of signed entries, so the deduction appears immediately; historical
margin reporting reads snapshots and is unaffected.

Getting this wrong in either direction is costly: mutating snapshots destroys historical
reporting, while omitting reversals means vendors are overpaid on returned goods.

### 5.3 Item status state machine

| State | Set by | Legal next states |
|---|---|---|
| `new` | Shopify webhook | `confirmed`, `cancelled_customer` |
| `confirmed` | CS action | `ready_to_ship`, `cancelled_oos` |
| `ready_to_ship` | Vendor / Ops | `shipped`, `cancelled_oos` |
| `shipped` | Bosta webhook | `out_for_delivery`, `failed_delivery`, `rto` |
| `out_for_delivery` | Bosta webhook | `delivered`, `failed_delivery` |
| `failed_delivery` | Bosta webhook | `out_for_delivery` (retry), `rto` |
| `delivered` | Bosta webhook | `return_requested`, `exchange_requested`, `closed` |
| `return_requested` | CS / customer | `ready_to_pick`, `rejected` |
| `ready_to_pick` | CS confirmation | `under_return` |
| `under_return` | Bosta webhook | `returned_wh` |
| `returned_wh` | Warehouse QC | `closed` |
| `rto` | Bosta webhook | `closed` |
| `cancelled_customer`, `cancelled_oos` | CS / Vendor | `closed` |

Transitions not in this table are rejected and logged. This is the guard against out-of-order
courier webhooks described in §4.3.

### 5.4 Financial engine

#### Business model formulas

Requirement 6.2 defines three models. Each item carries a `business_model` discriminator resolved
at ingestion.

**Vendor item**
```
vendor_payable    = selling_price − platform_commission
platform_commission = selling_price × vendor.commission_rate
net_margin        = platform_commission − allocated_shipping_cost − adjustments
```

**Private label item**
```
total_cost   = manufacturing_cost + operational_cost_allocation
net_profit   = selling_price − total_cost − allocated_shipping_cost
```

**Retail item**
```
total_cost   = purchase_cost + operational_cost_allocation
net_profit   = selling_price − total_cost − allocated_shipping_cost
```

Shipping is **allocated per item** pro-rata by item value where an order ships as one consignment,
and charged directly where each item has its own AWB. Because AWBs are created per item (req 3.2),
direct attribution is the normal case.

#### Snapshot write triggers

A new `financial_snapshots` row is appended — never updated — on each of:

| Trigger | `reason` |
|---|---|
| Order item created | `initial` |
| Delivered (revenue recognised) | `delivery_confirmed` |
| Flex-ship compensation confirmed | `flex_ship_compensation` |
| Return accepted at QC | `return_accepted` |
| Exchange delta settled | `exchange_delta` |
| Manual finance adjustment | `manual_adjustment` |

#### Vendor ledger entry types

| Type | Sign | Posted when |
|---|---|---|
| `sale` | + | Item delivered |
| `commission` | − | Item delivered |
| `shipping` | − | Shipping charged to vendor |
| `penalty` | − | Penalty confirmed |
| `return_reversal` | − | Return accepted at QC |
| `exchange_delta` | ± | Exchange settled |
| `flex_compensation` | + | Compensation passed through |
| `adjustment` / `bonus` | ± | Manual finance action |

Vendor balance is always `SUM(amount) WHERE settled_at IS NULL`. There is no separately maintained
balance field to drift out of sync.

### 5.5 Webhook inbox and idempotency

```
POST /webhooks/{provider}
  ├─ verify HMAC signature ......................... reject 401 on failure, alert
  ├─ INSERT INTO integration_events
  │    (source, external_id, payload, status='pending')
  │    ON CONFLICT (source, external_id) DO NOTHING   ← idempotency boundary
  └─ return 200 OK                                    ← target < 500ms
```

Processing is asynchronous. Each handler is individually idempotent as a second line of defence —
creating an AWB uses the `order_item` id as the provider idempotency key, so a retry after a
network timeout cannot produce a second label.

Retry schedule: 1m, 5m, 15m, 1h, 6h, then dead-letter with an ops alert.

### 5.6 API surface (Phase 1)

**Inbound webhooks**

| Endpoint | Source | Events |
|---|---|---|
| `POST /webhooks/shopify` | Shopify | `orders/create`, `orders/updated`, `orders/cancelled`, `fulfillments/*`, `refunds/create` |
| `POST /webhooks/bosta` | Bosta | Shipment state transitions, reverse pickup, flex ship |
| `POST /webhooks/paymob` | Paymob | Transaction processed, refund, (Phase 2) disbursement |

**Outbound integration calls**

| Target | Purpose |
|---|---|
| Shopify Admin GraphQL | Product publish, inventory set, price update, `returnCreate`, `refundCreate`, replacement draft order |
| Bosta REST | Create delivery, create reverse pickup, fetch AWB PDF, cancel |
| Paymob | Transaction lookup, refund, (Phase 2) Send disbursement |

**Vendor portal API** — session-authenticated, vendor-scoped: products, inventory, orders,
shipments, scorecard, settlements, bank details.

### 5.7 RBAC matrix

Six roles. The `Admin` column of earlier drafts is now **Super Admin**, and carries the platform
configuration capabilities in the lower block.

| Capability | Super Admin | Ops | CS | QC | Finance | Vendor |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| View all orders / items | ● | ● | ● | ● | ● | own only |
| Confirm / cancel item | ● | ● | ● | | | |
| Create / switch AWB | ● | ● | | | | |
| Add / remove shipping charge | ● | ● | | | ● | |
| Approve return / exchange | ● | ● | ● | | | |
| Warehouse QC receipt | ● | | | ● | | |
| Approve vendor product | ● | | | ● | | |
| Apply vendor penalty | ● | ● | | | ● | |
| Run / approve settlement | ● | | | | ● | |
| Record refund payment | ● | | | | ● | |
| View item-level margin | ● | ● | | | ● | own only |
| Manage users / roles | ● | | | | | |
| View audit trail | ● | ● | | | ● | |
| Update own stock / price | | | | | | ● |
| Submit product for approval | | | | | | ● |
| Manage own bank details | ● | | | | | ● |
| **Manage integrations and keys** | ● | | | | | |
| **Replay a dead-lettered event** | ● | | | | | |
| **Edit business rules** | ● | | | | | |
| **Define and schedule reports** | ● | | | | | |
| **Reset another user's 2FA** | ● | | | | | |

### 5.8 Audit trail

Requirement 12.4. Every mutation to orders, items, financial values, inventory, vendors, products
and settlements writes an `audit_log` row capturing user, timestamp, entity, old value and new
value as JSON. Integration-driven changes record the originating `integration_events` id as the
actor, so an automated change is as traceable as a human one.

### 5.9 Sequence diagrams

| # | Flow | Diagram |
|---|---|---|
| 1 | Order ingestion and item-level splitting | `seq-01-order-ingestion` |
| 2 | Per-item AWB creation and vendor label delivery | `seq-02-item-level-awb` |
| 3 | Shipment status sync and financial posting | `seq-03-shipment-status` |
| 4 | Return: request → CS approval → reverse pickup → QC → refund | `seq-04-return-flow` |
| 5 | Exchange: replacement order and snapshot carry-over | `seq-05-exchange-flow` |
| 6 | Vendor settlement and payout | `seq-06-vendor-settlement` |
| 7 | Vendor product upload and QC approval | `seq-07-vendor-product-approval` |
| 8 | Three-way payment reconciliation | `seq-08-payment-reconciliation` |


![Figure 6 — Order ingestion and item-level splitting](diagrams/seq-01-order-ingestion.svg)

*Figure 6 — Order ingestion and item-level splitting*

![Figure 7 — Per-item AWB creation and vendor label delivery](diagrams/seq-02-item-level-awb.svg)

*Figure 7 — Per-item AWB creation and vendor label delivery*

![Figure 8 — Shipment status sync and financial posting](diagrams/seq-03-shipment-status.svg)

*Figure 8 — Shipment status sync and financial posting*

![Figure 9 — Return: request, CS approval, reverse pickup, QC, refund](diagrams/seq-04-return-flow.svg)

*Figure 9 — Return: request, CS approval, reverse pickup, QC, refund*

![Figure 10 — Exchange: replacement order and snapshot carry-over](diagrams/seq-05-exchange-flow.svg)

*Figure 10 — Exchange: replacement order and snapshot carry-over*

![Figure 11 — Vendor settlement and payout](diagrams/seq-06-vendor-settlement.svg)

*Figure 11 — Vendor settlement and payout*

![Figure 12 — Vendor product upload and QC approval](diagrams/seq-07-vendor-product-approval.svg)

*Figure 12 — Vendor product upload and QC approval*

![Figure 13 — Three-way payment reconciliation](diagrams/seq-08-payment-reconciliation.svg)

*Figure 13 — Three-way payment reconciliation*

### 5.10 Activity diagrams

| # | Workflow | Diagram |
|---|---|---|
| 1 | Order lifecycle — all four scenarios | `act-01-order-lifecycle` |
| 2 | OOS and cancellation, with partial-order handling | `act-02-oos-cancellation` |
| 3a | Return intake, eligibility and reverse logistics | `act-03a-return-intake` |
| 3b | Return financial posting and vendor attribution | `act-03b-return-financial` |
| 4a | Exchange intake, stock check and dual shipping legs | `act-04a-exchange-intake` |
| 4b | Exchange QC and financial treatment | `act-04b-exchange-financial` |
| 5 | Vendor settlement cycle | `act-05-settlement-cycle` |
| 6 | Raw fabric consumption and replenishment (Phase 2) | `act-06-raw-fabric` |
| 7 | Flex shipping compensation handling | `act-07-flex-shipping` |


![Figure 14 — Order lifecycle, all four scenarios](diagrams/act-01-order-lifecycle.svg)

*Figure 14 — Order lifecycle, all four scenarios*

![Figure 15 — OOS and cancellation with partial-order handling](diagrams/act-02-oos-cancellation.svg)

*Figure 15 — OOS and cancellation with partial-order handling*

![Figure 16 — Return intake, eligibility and reverse logistics](diagrams/act-03a-return-intake.svg)

*Figure 16 — Return intake, eligibility and reverse logistics*

![Figure 17 — Return financial posting and vendor attribution](diagrams/act-03b-return-financial.svg)

*Figure 17 — Return financial posting and vendor attribution*

![Figure 18 — Exchange intake, stock check and dual shipping legs](diagrams/act-04a-exchange-intake.svg)

*Figure 18 — Exchange intake, stock check and dual shipping legs*

![Figure 19 — Exchange QC and financial treatment](diagrams/act-04b-exchange-financial.svg)

*Figure 19 — Exchange QC and financial treatment*

![Figure 20 — Vendor settlement cycle](diagrams/act-05-settlement-cycle.svg)

*Figure 20 — Vendor settlement cycle*

![Figure 21 — Raw fabric consumption and replenishment (Phase 2)](diagrams/act-06-raw-fabric.svg)

*Figure 21 — Raw fabric consumption and replenishment (Phase 2)*

![Figure 22 — Flex shipping compensation handling](diagrams/act-07-flex-shipping.svg)

*Figure 22 — Flex shipping compensation handling*

### 5.11 Platform configuration & administration

A back-office platform is only as good as the ops team's ability to run it without an engineer.
This section covers authentication and the Super Admin console.

#### 5.11.1 Authentication

Email and password for every user, via Laravel Fortify. **TOTP two-factor is mandatory for Super
Admin and Finance and optional for everyone else.**

The asymmetry is deliberate. Super Admin holds the Paymob credentials and Finance approves
settlements — those two roles can move money, and the friction is proportionate there. Imposing a
second factor on a CS agent processing a hundred returns a day would cost more in lost throughput
than it buys in security.

| Control | Setting |
|---|---|
| 2FA — Super Admin, Finance | Mandatory, enforced before first sign-in |
| 2FA — Ops, CS, QC | Optional, self-enrolled |
| Idle session timeout | 60 minutes |
| Failed-login lockout | 5 attempts per 15 minutes |
| Password policy | 12 characters minimum, checked against known-breach lists |
| Sign-in messages | Generic — never reveal whether an account exists or is suspended |

![Figure 23 — Authentication and two-factor verification](diagrams/seq-09-auth-2fa.svg)

*Figure 23 — Authentication and two-factor verification*

**The navigation is generated from the same capability set the guard enforces**, so a link can
never appear that the guard would then refuse. A refused deep-link renders an explicit "not
permitted" panel and writes the attempt to the audit trail — never a blank page, which reads as a
bug and generates a support ticket.

**Accounts are suspended, never deleted.** Deleting a user would orphan every order confirmation,
return approval and settlement they touched, breaking the audit trail that requirement 12.4 asks
for. Suspension revokes sessions and API tokens immediately and reassigns open work, while the
history stays intact.

![Figure 24 — User lifecycle from invitation to offboarding](diagrams/act-08-user-lifecycle.svg)

*Figure 24 — User lifecycle from invitation to offboarding*

#### 5.11.2 The Super Admin console

| Area | Contents | Phase |
|---|---|:-:|
| **Integrations & Keys** | Credential status and rotation, webhook health, event log, dead-letter replay, sync cursors | 1 |
| **Users & Access** | Staff accounts, role assignment, 2FA state, active sessions, security policy | 1 |
| **Roles & Permissions** | The §5.7 matrix as an editable grid | 1 |
| **System Health** | Queue depth, DLQ with replay, webhook success rates, scheduled jobs | 1 |
| **Business Rules** | Commission, SLA thresholds, return policies, reason taxonomy, penalty triggers, couriers | 1b |
| **Reports** | Saved definitions, field picker, schedule and recipients | 1b |

**Credentials are write-only.** A secret can be replaced but never read back — the stored value is
encrypted and is not returned to the browser under any circumstance. Every rotation is audited.

**Super Admin cannot be de-privileged from the permissions grid.** Removing the last administrative
capability from your own role is the classic way an organisation locks itself out of its own
system, so those cells are fixed. Changing *who holds* the role is done under Users & Access.

#### 5.11.3 Config, not code

Everything in the Business Rules area exists today as a number in a spreadsheet or a convention in
someone's head: commission rates, SLA thresholds, per-vendor return windows, which reasons charge
the vendor. Moving them into a `settings` table with `effective_from` dating means a rate change is
a form submission with an audit record, not a code change and a deployment.

Two consequences worth stating:

- **Rules are dated, not overwritten.** A commission change carries an effective date, so a
  settlement recomputed later still uses the rate that applied at the time — the same discipline as
  the financial snapshots in §5.2.2.
- **The 56-value reason taxonomy is data.** Adding a reason, or re-attributing one from Marketing to
  Commercial, is an admin action. The vocabulary belongs to the ops team, not to the codebase.

#### 5.11.4 Why the split across phases

The Phase 1 half is what you cannot operate without during peak week: replaying a failed webhook at
2am on Black Friday, rotating a leaked key, or onboarding a temporary CS agent. The Phase 1b half —
editing rules and building reports — has a working substitute in Phase 1, because rules ship seeded
by migration from the current sheet and a fixed set of built-in reports covers the questions the
spreadsheet answers today.

---

## 6. The In-House Returns & Exchanges Module

This section covers the change from the original requirement §5. The client is retiring E-stebdal
and building this capability in-house.

### 6.1 Why this is the right decision

**It removes the project's largest integration risk.** E-stebdal publishes no public API. An
integration would have depended on reverse-engineered endpoints or scraping, with no contract, no
versioning guarantee, and no support path — the single most likely component to break under Black
Friday load or to be silently changed by a third party.

**Returns are core volume, not an edge case.** 6,705 items (36.6%) pass through a return or RTO
path. A third of operational volume should not depend on a black box.

**The analytics are the real asset.** The team's 56-value reason taxonomy with stakeholder
attribution is a mature operational practice that no generic SaaS returns app models. Owning the
module means return data feeds the vendor scorecard, penalty workflow and catalogue quality loop
directly.

**It ends a recurring subscription.** Quantified in the budget as a recurring offset.

The cost is roughly three additional person-weeks versus the integration it replaces (§9.4).

### 6.2 Direction of data flow inverts

Under the original design, E-stebdal owned returns and OPS would read them. Now:

- **OPS is the system of record** for return requests, eligibility, approvals, QC outcomes,
  refunds and exchange linkage.
- **OPS writes into Shopify** via `returnCreate`, `refundCreate` and replacement draft orders, so
  the storefront and customer order history stay correct.
- **Shopify remains** the customer-facing order of truth and the catalogue master.

### 6.3 Components

| Component | Phase | Description |
|---|---|---|
| Request intake — CS console | 1 | CS creates requests on the customer's behalf, matching today's process |
| Request intake — customer portal | 1b | Order number + phone lookup, no account required |
| Eligibility rules engine | 1 | Return window, category exclusions, prior-return check, delivery check — **configurable per vendor**, since policies differ across 82 vendors |
| Reason taxonomy | 1 | 56 reasons + stakeholder attribution, ported verbatim |
| Approval workflow | 1 | `Requested → Confirm Return (CS) → Ready-To-Pick → Under Return (3PL) → Returned (WH)` |
| Reverse logistics | 1 | Bosta reverse pickup, reusing the forward shipping adapter |
| Warehouse QC | 1 | Accept / reject / damaged, with escalation path |
| Exchange fulfilment | 1 | Replacement order into Shopify, original snapshot carried |
| Refund ledger | 1 | Obligation + manual settlement, with proof capture |
| Vendor balance adjustment | 1 | Reversing ledger entry (req 8.7) |
| Returns analytics | 1b | Rate and reason breakdown by vendor, category, SKU |

### 6.4 Design decisions specific to this module

**Refunds are ledger obligations, not payment instructions.** With 89.7% of orders on COD, most
refunds settle manually via wallet, InstaPay or bank transfer. Modelling a refund as an automatic
payment would be wrong for nine out of ten refunds. A `refunds` row is created with
`status = pending`, appears in a finance work queue, and is marked paid only when settlement proof
is recorded. **This is the module's highest-risk design point** — getting it wrong produces either
unpaid customers or unrecorded cash movements.

**Exchanges carry the original financial snapshot.** An exchange is a fulfilment substitution, not
a new sale. The replacement item links to the original snapshot and only the *delta* (price
difference, extra shipping) posts as new ledger entries. Treating it as a new sale would
double-count GMV and overstate vendor payables.

**Eligibility is per-vendor and data-driven, not hard-coded.** With 82 vendors on differing return
policies, eligibility rules live in `return_policies` and are editable by admin without a
deployment.

**Rejections are logged with reasons.** `Refused – Policy Not Available` occurs 142 times in the
current data — the customer was refused because nobody could find the policy. Logged rejections
turn that into a measurable, fixable number.

### 6.5 Cutover plan

E-stebdal remains subscribed and running in parallel until the in-house module is validated
against live traffic. **Cutover is January 2027 — after the December post-Black-Friday return
peak, never during it.** Running both through December costs one month of subscription and removes
the risk of discovering a gap at the worst possible moment.

---

## 7. Technology Stack Selection

### 7.1 What actually constrains this choice

Two developers, thirteen weeks, twelve requirement areas, four integrations, two portals. The
dominant cost is not algorithmic complexity — it is the sheer volume of CRUD surface: tables with
filters, forms with validation, approval queues, exports, role-scoped dashboards.

The stack that generates that surface fastest wins, provided it handles webhooks and queues
competently. That is the criterion weighted highest below.

### 7.2 Scored comparison

Weights reflect the constraints above. Scores are 1–5.

| Criterion | Weight | Laravel 11 + Filament 3 | NestJS + Next.js | Django 5 + React | .NET 8 + Blazor |
|---|:-:|:-:|:-:|:-:|:-:|
| Speed to market for CRUD console | 30% | 5 | 2 | 4 | 3 |
| Egyptian talent availability | 20% | 5 | 5 | 3 | 3 |
| Hosting cost / footprint | 15% | 5 | 4 | 4 | 3 |
| Webhook & queue ergonomics | 15% | 4 | 5 | 4 | 4 |
| Reporting & export | 10% | 4 | 3 | 4 | 4 |
| Maintainability with 2 devs | 10% | 4 | 3 | 4 | 4 |
| **Weighted total** | | **4.65** | **3.55** | **3.80** | **3.35** |

**Laravel 11 + Filament 3** — Filament generates production-grade resource tables, filters, forms,
relation managers, bulk actions and exports from model definitions. The ops console, approval
queues and vendor portal are largely configuration rather than bespoke code. Horizon gives queue
management with a monitoring UI out of the box. PHP hosting is the cheapest of the four and Egypt
has the deepest Laravel talent pool. *Weakness:* less natural for heavy real-time UI, and Filament
customisation beyond its conventions costs more than it saves.

**NestJS + Next.js** — Best webhook and queue ergonomics, one language across the stack. But every
ops screen is hand-built React: the tables, filters, forms and exports that Filament provides free
become weeks of frontend work. In a 13-week window with one frontend developer, this is the
decisive disadvantage.

**Django 5 + React** — Django admin gives a real head start and the ORM suits the snapshot model
well. But Django admin is not production-grade for external vendor users, so the vendor portal is
still hand-built, and Egyptian Django talent is thinner than PHP or Node.

**.NET 8 + Blazor** — Strong typing and excellent financial-precision handling. But higher hosting
cost, a smaller local hiring pool at this budget, and no comparable admin-scaffolding accelerator.

### 7.3 Recommended stack

| Layer | Choice | Rationale |
|---|---|---|
| Language / runtime | PHP 8.3 | Filament prerequisite, cheapest hosting, deepest local talent |
| Framework | Laravel 11 | Queues, scheduling, events, migrations, testing built in |
| Admin / portal UI | Filament 3 | Generates both portals; the single biggest schedule saver |
| Database | PostgreSQL 16 | Correct `NUMERIC` money semantics, JSONB for payloads and audit diffs, partial indexes |
| Queue / cache | Redis 7 + Horizon | Named queues, retries, backoff, monitoring UI |
| Realtime | Laravel Reverb | Live dashboard updates without polling (req 12.3) |
| PDF | Browsershot / DomPDF | AWB relabelling, settlement statements |
| Frontend interactivity | Livewire + Alpine.js | Within Filament; React only for the Phase 1b customer portal |
| Testing | Pest + Laravel HTTP fakes | Integration adapters tested against recorded fixtures |
| CI/CD | GitHub Actions | Free tier sufficient |

**PostgreSQL over MySQL** deserves a note: `NUMERIC` arithmetic for money, JSONB for webhook
payloads and audit diffs, partial indexes for the "unsettled ledger entries" query that runs on
every settlement, and materialised views for dashboards. All four matter here.

### 7.4 What this means for the frontend engineer's role

Under this stack the FE engineer is **not** writing React screens for the ops console. Their scope
is: Filament theming and custom pages, dashboard and chart components, the vendor portal UX,
Livewire/Alpine interaction work, the AWB and statement print layouts, and — in Phase 1b — the
customer-facing returns portal, which is the one genuinely bespoke frontend deliverable.

This should be explicit when hiring. A React-only specialist would be under-utilised for the first
three months; someone comfortable with Livewire/Alpine and Blade templating is the right profile.

---

## 8. Hosting & Infrastructure

### 8.1 Sizing

The workload is modest: 3,223 items in the busiest month to date, 82 vendors, and an internal user
population in the low tens. Even at 5× Black Friday load — 16,000 items in November — this is a
small-database, low-concurrency application.

**Recommended baseline:** app node 8 vCPU / 16 GB, data node 4 vCPU / 8 GB, staging 2 vCPU / 4 GB.
This is deliberately over-provisioned for the current run-rate so that peak week needs no scaling
event.

### 8.2 Options compared

Monthly cost is for the complete environment (app + data + staging + backups + object storage).
EUR converted at 55 EGP, USD at 50.25 EGP.

| Option | Monthly cost | Latency to Egypt | Managed services | DevOps effort | PDPL position |
|---|---:|---|---|---|---|
| **Hetzner Cloud (DE/FI)** — CX43 + CX33 + CX23 | ~€41 → **~2,255 EGP** | 60–80 ms | Backups, volumes, LB | Low | Cross-border — licence required |
| Contabo (DE) | ~€25 → ~1,375 EGP | 60–90 ms | Minimal | Medium | Cross-border — licence required |
| DigitalOcean (FRA/AMS) — Droplet + managed PG | ~$95 → ~4,775 EGP | 60–80 ms | Managed PG, backups | Low | Cross-border — licence required |
| AWS me-south-1 / me-central-1 | ~$220 → ~11,055 EGP | 25–40 ms | Full managed suite | Medium | Cross-border — licence required |
| Egyptian local DC (Telecom Egypt / Orange) | **Quote required** — indicatively 3,000–8,000 EGP | < 10 ms | Limited; often no API provisioning | High | **No cross-border transfer** |

A note on honesty: the Egyptian local-provider figure is an indicative range, not a verified quote.
Local providers in this segment do not publish comparable pricing, and their managed-service and
API-provisioning maturity varies widely. **Obtaining two firm quotes is a Sprint 0 action item**
(§9.2), because this row is the only one that removes the PDPL cross-border question entirely.

### 8.3 Recommendation

**Hetzner Cloud CX-line in the EU, fronted by Cloudflare, with the PDPL licence application
started in Sprint 0.**

Reasoning:

- **Latency is not the deciding factor.** This is an internal back-office system for tens of users
  plus 82 vendors. A 70 ms round trip is imperceptible in a form-driven admin application, and
  Cloudflare fronts static assets. The only public surface is the Phase 1b returns portal.
- **Cost is decisive at this budget.** Hetzner at ~2,255 EGP/month against AWS at ~11,055 EGP/month
  is a difference of ~44,000 EGP over the first year — roughly 15% of the entire project budget,
  for no benefit this workload can use.
- **Note the June 2026 Hetzner repricing.** The CPX and CCX lines rose 113–175% in June 2026
  (CCX13 went from €15.99 to €42.99). The **CX line is now the value pick** — CX43 at €15.99 for
  8 vCPU / 16 GB. Any older cost model based on CPX pricing is out of date.
- **The PDPL licence is required regardless.** The client already transfers customer PII to Shopify
  outside Egypt. Hosting locally would not remove that obligation. See §11.

**If legal counsel rejects EU hosting**, the fallback is Egyptian local hosting at an estimated
+800 to +5,700 EGP/month, i.e. **+4,000 to +28,500 EGP across the Phase 1 window**. That must come
from contingency or displace scope. This decision needs to be made in Sprint 0, not later —
migrating hosting mid-project is not affordable in this timeline.

### 8.4 Supporting services

| Service | Choice | Monthly cost |
|---|---|---|
| DNS / TLS / WAF / CDN | Cloudflare free tier | 0 |
| Error tracking | Sentry free tier | 0 |
| Uptime monitoring | Uptime Kuma (self-hosted on staging) | 0 |
| Source control / CI | GitHub Team, 3 seats | ~$12 → ~600 EGP |
| Transactional email | Amazon SES | ~$5 → ~250 EGP |
| Object storage | Hetzner Storage Box | ~€5 → ~275 EGP |
| Domain | — | ~50 EGP amortised |

### 8.5 Backup and recovery

- PostgreSQL WAL archiving for point-in-time recovery
- Nightly encrypted snapshots, off-site, 30-day retention
- Object storage (AWB PDFs, payout proofs) included in the snapshot set
- **Restore drill executed during UAT, not assumed** — an untested backup is not a backup

Targets: RPO 15 minutes, RTO 4 hours. Both are achievable on this topology and should be verified
before code freeze.

---

## 9. Delivery Plan & Timeline

### 9.1 Fixed dates

| Date | Milestone |
|---|---|
| 10 Aug 2026 | Sprint 0 begins |
| 17 Aug 2026 | Sprint 1 begins |
| 6 Nov 2026 | Sprint 6 ends — feature complete |
| 9–20 Nov 2026 | UAT, parallel run, data migration, load test |
| **20 Nov 2026** | **Code freeze — go-live** |
| **27 Nov 2026** | **Black Friday** — hypercare |
| 23 Nov – 11 Dec 2026 | Phase 1b — customer returns portal |
| January 2027 | E-stebdal decommissioned |

### 9.2 Sprint 0 — 10–14 August

Non-negotiable prerequisites. If these are not complete by 14 August, the timeline is already at
risk and that should be escalated immediately rather than absorbed.

- Shopify custom app credentials with required Admin API scopes
- Bosta API credentials — production and sandbox
- Paymob API credentials and HMAC secrets
- **Two firm quotes from Egyptian hosting providers** (§8.2)
- **PDPL cross-border licence application initiated** (§11)
- **Return-policy workshop with CS** — pin down per-vendor eligibility rules, the single largest
  unknown in the returns module
- Vendor commission-rate master data confirmed
- Schema review and migration plan for the 18,341 historical rows
- Environments provisioned, CI/CD green

### 9.3 Sprint plan

| Sprint | Dates | Backend | Frontend | DevOps |
|---|---|---|---|---|
| **1** | 17–28 Aug | Schema, migrations, RBAC, audit log, webhook inbox, **auth + 2FA (Fortify)** | Filament shell, **login screen**, layout, ops list views | Environments, CI/CD, secrets, backups |
| **2** | 31 Aug–11 Sep | Shopify adapter, order ingestion, **item-level splitting** | Order list + item detail, filters replicating sheet columns | Staging, monitoring, log shipping |
| **3** | 14–25 Sep | Bosta adapter, **per-item AWB**, status webhooks, flex-ship, **integrations console** | Shipping console, AWB actions, label print, **users & roles screens** | Queue tuning, alerting, DLQ alerts |
| **4** | 28 Sep–9 Oct | **Financial engine** — snapshots, ledger, 3 business models | Financial dashboard, item-level margin views | Reporting replica, materialised views |
| **5** | 12–23 Oct | **Returns & exchanges** — eligibility, workflow, reverse pickup, refund ledger | Returns console, approval queue, QC receipt screens | Load test at 5× peak, PDPL controls |
| **6** | 26 Oct–6 Nov | Settlement, reconciliation, vendor portal API, **historical migration** | Vendor portal, payout views, exports | **System health + DLQ replay**, runbooks, restore drill |
| **UAT** | 9–20 Nov | Defect fixes only | Defect fixes only | Production cutover, parallel run support |

Returns lands in Sprint 5 deliberately — after the financial engine exists, since return reversals
depend on the ledger, and with one sprint of buffer before UAT.

The Super Admin console is threaded across Sprints 1, 3 and 6 rather than batched. Authentication
must exist before anything else can be gated, the integrations console belongs beside the adapter
work it manages, and system health lands last because it is the piece the team needs on-call during
hypercare rather than during build.

### 9.4 Where the in-house returns module costs more

| Work item | Integration approach | In-house build | Delta |
|---|---:|---:|---:|
| Adapter / API client | 5 d | — | −5 d |
| Eligibility rules engine | — | 4 d | +4 d |
| Reason taxonomy + admin | 1 d | 2 d | +1 d |
| Approval workflow + console | 2 d | 6 d | +4 d |
| Reverse logistics | 2 d | 3 d | +1 d |
| Exchange fulfilment | 2 d | 5 d | +3 d |
| Refund ledger | 1 d | 4 d | +3 d |
| QC receipt | — | 2 d | +2 d |
| **Total** | **13 d** | **26 d** | **+13 d (≈3 weeks)** |

Offset by moving the customer self-service portal (~8 days) to Phase 1b, and by removing the
integration risk contingency that a no-public-API dependency would have required.

### 9.5 Parallel run — non-negotiable

For the two weeks from 9 to 20 November, the ops team **keeps maintaining the Google Sheet
alongside the new system**. Daily reconciliation between the two proves data parity before the
sheet is abandoned.

This costs two weeks of duplicated effort. It buys a working fallback during peak week. Given that
the system goes live seven days before the highest-revenue day of the year, this is the cheapest
insurance available and should not be traded away for schedule.

The same principle governs E-stebdal, which stays subscribed until January.

### 9.6 Levers if the schedule slips

Stated in advance so the conversation in October is a decision, not a crisis:

1. **Cut scope** — defer settlement automation and the vendor scorecard to Phase 1b, keeping order,
   shipping, returns and finance. Recovers ~2 weeks.
2. **Extend timeline** — go live after Black Friday, in December. Removes all peak-week risk but
   forfeits a year's peak-season benefit.
3. **Add budget** — a second backend engineer for Sprints 4–6 costs ~102,000 EGP and recovers
   ~3 weeks, but incurs onboarding drag and is only effective if committed by mid-September.

The first lever is preferred. The third is least effective if invoked late.

---

## 10. Risks & Mitigations

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | **PDPL licence not granted before 31 Oct enforcement** | Medium | High | Apply in Sprint 0. Obtain Egyptian hosting quotes as fallback. Decide by end of Sprint 2 — migration later is unaffordable. |
| R2 | **Integration credentials delayed past Sprint 0** | Medium | High | Escalate at day 3, not day 5. Build adapters against recorded fixtures so work proceeds; but no fixture substitutes for real sandbox testing. |
| R3 | **Bosta API cannot create per-item AWBs as assumed** | Low | High | Validate in Sprint 0 with a real sandbox call. Fallback: order-level AWB with internal item allocation — degrades req 3.2 and must be flagged to the client immediately if hit. |
| R4 | **Returns module underestimated** | Medium | Medium | Sprint 5 placement leaves one sprint of buffer. Customer portal already deferred to 1b. CS workshop in Sprint 0 removes the largest unknown. |
| R5 | **Historical migration reveals unresolvable data quality gaps** | High | Medium | 970 rows have no status and 5,495 no governorate. Migrate with explicit `unknown` markers rather than guessing. Agreed with the client in Sprint 0 — do not silently infer. |
| R6 | **Black Friday load exceeds 5× projection** | Low | High | Load test in Sprint 5 at 5× peak. Vertical scaling headroom is one click on this topology. Queue-based architecture degrades gracefully — webhooks buffer rather than fail. |
| R7 | **Key-person dependency across a 3-person team** | Medium | High | Pair on the financial engine and returns module specifically. Runbooks in Sprint 6. Realistically this cannot be fully mitigated at this team size and should be accepted knowingly. |
| R8 | **Scope growth during build** | High | High | Phase 1 has zero slack (§1.4). Any addition must displace something. Change requests go to Phase 1b/2 by default. |
| R9 | **COD refund process not agreed with finance** | Medium | Medium | Refund settlement is manual by design (§6.4). Confirm the operational process with finance in Sprint 0, not Sprint 5. |
| R10 | **Vendor adoption of the portal is slow** | Medium | Low | Vendors currently receive labels by WhatsApp. Run the portal alongside existing channels through January rather than forcing immediate cutover. |
| R11 | **PDPL retention and data-subject rights are unbuilt** | High | Medium | The admin console covers integrations, users, rules and health — **not** retention policy, erasure workflows or data-subject access requests. With enforcement from 31 Oct 2026 this is a legal exposure rather than a feature gap. Carry as an explicit Phase 1b commitment and agree the manual interim process with counsel in Sprint 0. |
| R12 | **Privileged access is concentrated in one role** | Medium | High | On a three-person team, Super Admin holds the Paymob credentials, can edit any business rule and can grant itself any capability. Mitigations: mandatory 2FA, write-only credential storage, full audit of every configuration change, and **at least two named Super Admins** so the role is never one person. This cannot be fully resolved at this team size and should be accepted knowingly. |

---

## 11. Data Protection & PDPL Compliance

### 11.1 The obligation

Egypt's Personal Data Protection Law (Law No. 151 of 2020) reaches full enforcement on
**31 October 2026**, with cross-border transfer licensing required by **2 November 2026**. Both
dates fall inside this project's delivery window and four weeks before Black Friday.

Storing Egyptian customers' names, phone numbers and delivery addresses on infrastructure outside
Egypt constitutes a cross-border transfer requiring a licence from the Personal Data Protection
Center, and the appointment of a Data Protection Officer in Egypt.

### 11.2 The client already has this exposure

This is the most important point in this section. **Shopify already stores this data outside
Egypt.** So do Bosta and Paymob to varying degrees. The licence obligation exists today,
independent of where this system is hosted. Hosting locally would reduce but not remove it.

The correct framing is therefore: **this is a parallel legal workstream that the business needs
regardless, which this project should trigger and not be blocked by.**

### 11.3 Actions

| # | Action | Owner | When |
|---|---|---|---|
| 1 | Initiate PDPL cross-border transfer licence application | Client legal | **Sprint 0** |
| 2 | Appoint a Data Protection Officer in Egypt | Client | Sprint 0–1 |
| 3 | Obtain two Egyptian hosting quotes as fallback | DevOps | Sprint 0 |
| 4 | Data inventory: what PII, where stored, which processor | BE + legal | Sprint 1 |
| 5 | Hosting decision confirmed | Client + legal | **End of Sprint 2** |
| 6 | Encryption at rest and in transit; PII columns encrypted | BE / DevOps | Sprint 1–2 |
| 7 | Retention policy and deletion workflow | BE | Sprint 5 |
| 8 | Data subject access request procedure | BE | Phase 1b |

### 11.4 Technical controls in scope for Phase 1

- TLS 1.3 in transit; full-disk and database encryption at rest
- Application-level encryption on phone numbers and addresses
- Role-based access with least privilege (§5.7); vendors see only their own orders
- Complete audit trail of PII access (§5.8)
- Encrypted off-site backups with defined retention
- PII redacted from application logs and error reports

Note that building returns in-house **increases** the PII held in the client's own system —
customer contact details for return coordination that previously lived in E-stebdal. This raises
the importance of items 6 and 7 above.

---

## 12. Requirements Traceability Matrix

Every numbered requirement from `Ops System Requirements V 0.1.docx`, mapped to design and phase.

| Req | Requirement | Phase | Design reference | Prototype screen |
|---|---|:-:|---|---|
| 1.1 | Google Sheet automation — replicate all functionality | 1 | §2.2, §5.1 ERD | Orders |
| 1.2 | Shopify sync — events, all status scenarios | 1 | `seq-01`, `act-01`, §5.3 state machine | Orders, Integrations |
| 2.1 | Item-level processing — split `1000-1/2/3` | 1 | §5.2.1, `seq-01` | Order Detail |
| 2.2 | Multi-location fulfilment | 1 | `order_items.location_id`, `locations` | Order Detail |
| 3.1 | Multi-courier support, switch, edit, manual charges | 1 (Bosta) / 2 (2nd courier) | `couriers`, adapter interface | Shipping |
| 3.2 | Item-level AWB creation | 1 | `seq-02` | Shipping |
| 3.3 | Automatic shipping status updates | 1 | `seq-03` | Shipping, Orders |
| 3.4 | Flex shipping detection and compensation | 1 | `act-07` | Financial |
| 4.1 | Automatic payment sync — Shopify, Paymob, Bosta | 1 | `seq-08` | Financial, Integrations |
| 4.2 | Geographic data capture | 1 | `orders` governorate/area/city | Orders |
| 5 | **Returns & exchanges — IN-HOUSE** | 1 (CS) / 1b (customer) | **§6**, `seq-04`, `seq-05`, `act-03a/b`, `act-04a/b` | Returns, Customer Portal |
| 6.1 | Real-time margin calculation per item | 1 | §5.4 | Financial, Order Detail |
| 6.2 | Three business models | 1 | §5.4 formulas | Financial |
| 6.3 | Historical financial accuracy — immutable | 1 | §5.2.2 append-only snapshots | Financial |
| 6.4 | Commission & penalty tracking | 1 | §5.4 ledger types | Vendors, Financial |
| 6.5 | Profit & loss reporting | 1 | Materialised views | Financial |
| 7.1 | Product inventory tracking | 1 | `inventory_levels` | Inventory |
| 7.2 | **Raw fabric inventory & consumption** | **2** | `act-06`, `product_fabric_bom` | Inventory (marked Phase 2) |
| 8 | Vendor portal with separate secure access | 1 | §5.7 RBAC, `vendor_users` | Vendor Portal |
| 8.1 | Product management with approval rules | 1 | `seq-07` | Vendor Products, Approvals |
| 8.2 | Vendor sales reporting | 1 | Read models | Vendor Dashboard |
| 8.3 | Vendor operational analytics | 1 | Read models | Vendor Scorecard |
| 8.4 | Payout management view | 1 | `settlements` | Vendor Payouts |
| 8.5 | Bank information management | 1 | `vendors` bank fields (encrypted) | Vendor Bank Details |
| 8.6 | **Automated vendor settlement** | 1 (calc) / **2** (Paymob Send) | `seq-06`, `act-05` | Vendor Payouts |
| 8.7 | Return adjustments to vendor balance | 1 | §5.2.3 reversing entries | Vendor Payouts, Returns |
| 9 | Vendor shipping automation — label to portal + email | 1 | `seq-02` | Shipping, Vendor Portal |
| 10 | Vendor performance analytics / Score Card | 1 (basic) / 2 (advanced) | Read models | Vendor Scorecard |
| 11 | Reporting & dashboards — 5 dashboards | 1 (4) / 2 (executive) | Materialised views | All dashboards |
| 12.1 | Vendor settlement calculation | 1 | `act-05` | Vendor Payouts |
| 12.2 | Item-level profitability tracking | 1 | §5.4 | Order Detail, Financial |
| 12.3 | Real-time status listening — event-driven | 1 | §4.3, Reverb | Integrations |
| 12.4 | Audit trail — user, timestamp, old, new | 1 | §5.8 | Audit Trail |

### 12.1 Platform requirements (derived)

These are **not numbered in `Ops System Requirements V 0.1`**. They are capabilities the numbered
requirements imply but do not state — chiefly requirement 8 (separate secure vendor access), 12.3
(event-driven operation) and 12.4 (audit trail), none of which can be delivered without
authentication, user management and a way to inspect and replay events. They are labelled `P-n` and
counted separately so the client's own requirement count stays honest.

| Ref | Capability | Phase | Design reference | Prototype screen |
|---|---|:-:|---|---|
| P-1 | Authentication with role-based sign-in | 1 | §5.11.1, `seq-09` | Login |
| P-2 | Two-factor for money-moving roles | 1 | §5.11.1, `seq-09` | Login → 2FA |
| P-3 | User lifecycle: invite, suspend, offboard | 1 | §5.11.1, `act-08` | Users & Access |
| P-4 | Editable role/permission matrix | 1 | §5.7, §5.11.2 | Roles & Permissions |
| P-5 | Integration credentials, health and event replay | 1 | §5.11.2 | Integrations & Keys · System Health |
| P-6 | Business rules and reports as configuration | 1b | §5.11.3 | Business Rules · Reports |

**Coverage: all 33 numbered requirements are addressed**, plus 6 derived platform requirements. 27 are delivered wholly within Phase 1;
requirement 5 (returns & exchanges) spans Phase 1 and Phase 1b; five (3.1 multi-courier,
7.2 raw fabric, 8.6 automated disbursement, 10 advanced scorecard, 11 executive dashboard) are
partly or wholly Phase 2. No requirement is unmapped.

---

## 13. Appendix — Diagram Index

All 24 diagrams are provided as editable Mermaid source (`.mmd`), scalable vector (`.svg`) and
high-resolution raster (`.png` at 2×) in `deliverables/diagrams/`.

### High-Level Design

| File | Description |
|---|---|
| `hld-01-system-context` | System context — actors, external systems, retired E-stebdal |
| `hld-02-containers` | Container view — application, domain, data and adapter tiers |
| `hld-03-event-architecture` | Event flow — inbox, dispatcher, handlers, DLQ |
| `hld-04-deployment` | Deployment topology, observability, backup, PDPL note |
| `hld-05-erd` | Entity-relationship model with key column definitions |

### Sequence Diagrams

| File | Description |
|---|---|
| `seq-01-order-ingestion` | Shopify order → item splitting → vendor assignment → snapshot |
| `seq-02-item-level-awb` | Per-item AWB → Bosta → PDF to vendor dashboard and email |
| `seq-03-shipment-status` | Status webhook → state machine → revenue / reversal posting |
| `seq-04-return-flow` | Return request → CS approval → reverse pickup → QC → refund |
| `seq-05-exchange-flow` | Exchange → replacement order → original snapshot carry-over |
| `seq-06-vendor-settlement` | Ledger aggregation → approval → payout → proof |
| `seq-07-vendor-product-approval` | Vendor upload → QC approval → Shopify publish |
| `seq-08-payment-reconciliation` | Three-way Shopify / Paymob / Bosta COD reconciliation |
| `seq-09-auth-2fa` | Sign-in, two-factor challenge, role resolution and route guarding |

### Activity Diagrams

| File | Description |
|---|---|
| `act-01-order-lifecycle` | All four order lifecycle scenarios end to end |
| `act-02-oos-cancellation` | OOS handling with partial-order cancellation |
| `act-03a-return-intake` | Return eligibility, approval and reverse logistics |
| `act-03b-return-financial` | Return financial posting, refund routing, vendor attribution |
| `act-04a-exchange-intake` | Exchange stock check, price delta, dual shipping legs |
| `act-04b-exchange-financial` | Exchange QC, snapshot carry-over, catalogue feedback loop |
| `act-05-settlement-cycle` | Settlement calculation, dispute, approval, disbursement |
| `act-06-raw-fabric` | Raw fabric BOM, consumption and depletion forecasting (Phase 2) |
| `act-07-flex-shipping` | Flex shipping compensation detection and financial treatment |
| `act-08-user-lifecycle` | User invitation, 2FA enrolment, role change and offboarding |

### Supporting Files

| Path | Contents |
|---|---|
| `scripts/extract_data.py` | Extraction and profiling script (read-only against the workbook) |
| `data/schema.json` | Column inventory and fill rates for all 6 sheets |
| `data/enums.json` | Distinct values and frequencies for every controlled-vocabulary column |
| `data/metrics.json` | Volume, revenue, SLA, vendor and reason-taxonomy profiles |
| `data/supporting.json` | Penalty, compensation, refund, staff-order and OOS summaries |
| `data/seed.json` | Anonymised rows seeding the clickable prototype |
| `02-Budget-Plan.xlsx` | Budget model with live formulas |
| `03-Prototype/index.html` | Clickable prototype covering all requirements |

---

*Prepared from `Ops System Requirements V 0.1.docx` and `POC - Youssey Excelsheet.xlsx`.
All quantitative claims are reproducible by running `scripts/extract_data.py`.*
