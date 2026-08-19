#!/usr/bin/env python3
"""
Extract and profile the client's manual operations workbook.

Reads `POC - Youssey Excelsheet.xlsx` (read-only, never modified) and emits JSON
profiles under deliverables/data/ that feed two consumers:

  1. The technical proposal's LLD  - real column names, enum vocabularies and
     volume figures, so the data model is grounded in how the client actually
     works rather than in guesses.
  2. The clickable prototype       - anonymised seed rows, so the demo shows the
     client their own vendors, SKUs and statuses.

Free-text columns hold Arabic customer/CS notes; those are redacted rather than
exported. Order numbers, vendor names and SKUs are the client's own business
data and are kept, since the deliverable goes back to the client.
"""

import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
WORKBOOK = ROOT / "POC - Youssey Excelsheet.xlsx"
OUT = ROOT / "deliverables" / "data"

# Columns holding free-text notes written by CS/ops staff. These mix Arabic
# customer remarks with internal commentary, so they are redacted to a presence
# flag instead of being exported verbatim.
FREE_TEXT = {
    "Comment", "Comment ", "Comment Nada", "Comment Maryam", "Comment OPS",
    "Reason For Late",
}

# Columns whose distinct values form a controlled vocabulary worth porting into
# the new system as enum/lookup tables.
ENUM_COLUMNS = {
    "Copy of Orders": [
        "Multi or Single", "Vendor Name", "AWB", "Payment Method", "Governorate",
        "Final status", "Stakeholder", "Reasons", "Vendor Penalty",
        "Recall Status", "Bosta FlexShip", "QC Checkbox",
    ],
    "OOS Orders": ["Reason For Late", "CS Action"],
    "Copy of Vendor Penalty": ["Vendor", "Reasons"],
    "Copy of Staff Orders": ["Staff Name", "Status"],
    "Copy of Bosta Compensation ": ["Comment", "Arrival"],
    "Copy of Return Bosta": [],
}

# Return/exchange outcomes, used to size the in-house returns module that
# replaces the third-party E-stebdal app.
RETURN_STATUSES = {"Returned", "Under Return", "RTO"}


# Copy-pasting between Shopify, Bosta and the sheet has left a large share of
# product names double-encoded: a UTF-8 en-dash read back as cp1252 shows up as
# "â€“". Round-tripping through cp1252 recovers the original character. Arabic
# text cannot be encoded to cp1252 at all, so it is left untouched by the except.
MOJIBAKE_HINT = ("â", "Ã", "€")


def demojibake(text):
    if not any(h in text for h in MOJIBAKE_HINT):
        return text
    try:
        return text.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def norm(value):
    """Collapse a cell to a stable, comparable string key."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    text = str(value).strip()
    text = demojibake(text)
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    return text or None


def as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def sheet_rows(worksheet):
    """Yield (header, row_dict) pairs, skipping fully-blank rows."""
    rows = worksheet.iter_rows(values_only=True)
    header = [norm(h) for h in next(rows)]
    for raw in rows:
        if all(cell is None for cell in raw):
            continue
        yield header, dict(zip(header, raw))


def percentiles(values, points=(50, 90, 95, 99)):
    if not values:
        return {}
    ordered = sorted(values)
    result = {"n": len(ordered), "min": ordered[0], "max": ordered[-1],
              "avg": round(sum(ordered) / len(ordered), 2)}
    for p in points:
        index = min(int(len(ordered) * p / 100), len(ordered) - 1)
        result[f"p{p}"] = ordered[index]
    return result


def profile_schema(workbook):
    """Column inventory and fill rate per sheet - the raw material for the ERD."""
    schema = {}
    for worksheet in workbook.worksheets:
        filled, total, types = Counter(), 0, defaultdict(Counter)
        header = None
        for hdr, row in sheet_rows(worksheet):
            header = hdr
            total += 1
            for column, value in row.items():
                if column is None:
                    continue
                if value is not None and norm(value) is not None:
                    filled[column] += 1
                    types[column][type(value).__name__] += 1
        columns = [c for c in (header or []) if c is not None]
        schema[worksheet.title] = {
            "row_count": total,
            "columns": [
                {
                    "name": column,
                    "filled": filled[column],
                    "fill_rate": round(filled[column] / total, 4) if total else 0,
                    "observed_types": dict(types[column]),
                    "redacted": column in FREE_TEXT,
                }
                for column in columns
            ],
        }
    return schema


def profile_enums(workbook):
    """Distinct values per controlled-vocabulary column, with frequencies."""
    enums = {}
    for worksheet in workbook.worksheets:
        wanted = ENUM_COLUMNS.get(worksheet.title, [])
        if not wanted:
            continue
        counters = {column: Counter() for column in wanted}
        for _, row in sheet_rows(worksheet):
            for column in wanted:
                value = norm(row.get(column))
                counters[column][value if value is not None else "(blank)"] += 1
        enums[worksheet.title] = {
            column: {
                "distinct": len(counter),
                "values": [{"value": v, "count": c}
                           for v, c in counter.most_common()],
            }
            for column, counter in counters.items()
        }
    return enums


def profile_orders(workbook):
    """Volume, revenue, fulfilment and SLA metrics from the main orders sheet."""
    worksheet = workbook["Copy of Orders"]

    monthly = defaultdict(lambda: Counter())
    monthly_gmv = Counter()
    vendors = defaultdict(lambda: Counter())
    vendor_gmv = Counter()
    sla = defaultdict(list)
    reason_by_stakeholder = defaultdict(Counter)
    governorates = Counter()

    items = gmv = shipping = 0
    customer_orders = set()
    returns = exchanges = return_requests = flex_applied = penalties = 0
    first_date = last_date = None

    for _, row in sheet_rows(worksheet):
        items += 1

        price = as_float(row.get("Item price")) or 0.0
        quantity = as_float(row.get("Lineitem quantity")) or 1.0
        line_value = price * quantity
        gmv += line_value
        shipping += as_float(row.get("Shipping Fees")) or 0.0

        order_no = norm(row.get("Customer Orders"))
        if order_no:
            customer_orders.add(order_no.split("-")[0])

        status = norm(row.get("Final status")) or "(blank)"
        vendor = norm(row.get("Vendor Name")) or "(unassigned)"
        reason = norm(row.get("Reasons"))
        stakeholder = norm(row.get("Stakeholder"))

        vendors[vendor]["items"] += 1
        vendors[vendor][status] += 1
        vendor_gmv[vendor] += line_value

        governorate = norm(row.get("Governorate"))
        if governorate:
            governorates[governorate] += 1

        if reason and stakeholder:
            reason_by_stakeholder[stakeholder][reason] += 1

        if row.get("Return Request Date") is not None:
            return_requests += 1
        if row.get("Return Date") is not None or status in RETURN_STATUSES:
            returns += 1
        if (reason and "xchange" in reason) or "xchange" in status:
            exchanges += 1
        if norm(row.get("Bosta FlexShip")) == "Apply FlexShip":
            flex_applied += 1
        if norm(row.get("Vendor Penalty")):
            penalties += 1

        order_date = row.get("Order date")
        if isinstance(order_date, datetime):
            month = order_date.strftime("%Y-%m")
            monthly[month]["items"] += 1
            monthly[month][status] += 1
            monthly_gmv[month] += line_value
            first_date = order_date if not first_date else min(first_date, order_date)
            last_date = order_date if not last_date else max(last_date, order_date)

        # SLA columns are day-counts entered by hand; a few rows hold stray
        # serial numbers, so implausible values are dropped rather than skewing
        # the percentiles quoted in the proposal.
        for column in ("CS SLA", "FM SLA", "Delivere SLA", "Return SLA"):
            value = as_float(row.get(column))
            if value is not None and 0 <= value <= 90:
                sla[column].append(value)

    delivered = sum(month["Delivered"] for month in monthly.values())

    return {
        "period": {
            "from": first_date.date().isoformat() if first_date else None,
            "to": last_date.date().isoformat() if last_date else None,
        },
        "totals": {
            "item_rows": items,
            "unique_customer_orders": len(customer_orders),
            "vendors": len([v for v in vendors if v != "(unassigned)"]),
            "gmv_egp": round(gmv, 2),
            "shipping_fees_egp": round(shipping, 2),
            "avg_item_value_egp": round(gmv / items, 2) if items else 0,
            "delivered_items": delivered,
            "delivery_rate": round(delivered / items, 4) if items else 0,
            "return_or_rto_items": returns,
            "return_rate": round(returns / items, 4) if items else 0,
            "explicit_return_requests": return_requests,
            "exchange_items": exchanges,
            "flex_shipping_applied": flex_applied,
            "penalised_items": penalties,
        },
        "monthly": [
            {
                "month": month,
                "items": counts["items"],
                "gmv_egp": round(monthly_gmv[month], 2),
                "delivered": counts["Delivered"],
                "delivery_rate": round(counts["Delivered"] / counts["items"], 4),
                "rto": counts["RTO"],
                "failed_delivery": counts["FD Allow Open Shipment"],
                "cancelled": counts["Cancelled"],
            }
            for month, counts in sorted(monthly.items())
        ],
        "top_vendors": [
            {
                "vendor": vendor,
                "items": counts["items"],
                "gmv_egp": round(vendor_gmv[vendor], 2),
                "delivered": counts["Delivered"],
                "delivery_rate": round(counts["Delivered"] / counts["items"], 4),
                "rto": counts["RTO"],
                "returned": counts["Returned"],
            }
            for vendor, counts in sorted(
                vendors.items(), key=lambda kv: -kv[1]["items"])[:25]
            if vendor != "(unassigned)"
        ],
        "sla": {column: percentiles(values) for column, values in sla.items()},
        "governorates": [{"governorate": g, "items": c}
                         for g, c in governorates.most_common()],
        "reason_taxonomy_by_stakeholder": {
            stakeholder: [{"reason": r, "count": c} for r, c in counter.most_common()]
            for stakeholder, counter in sorted(
                reason_by_stakeholder.items(), key=lambda kv: -sum(kv[1].values()))
        },
    }


def profile_supporting(workbook):
    """The five satellite sheets that become their own tables in the new model."""
    result = {}

    penalty = Counter()
    penalty_value = 0.0
    for _, row in sheet_rows(workbook["Copy of Vendor Penalty"]):
        penalty[norm(row.get("Vendor")) or "(blank)"] += 1
        penalty_value += as_float(row.get("Item price")) or 0.0
    result["vendor_penalty"] = {
        "rows": sum(penalty.values()),
        "total_value_egp": round(penalty_value, 2),
        "by_vendor": [{"vendor": v, "count": c} for v, c in penalty.most_common()],
    }

    compensation_total = 0.0
    compensation_rows = 0
    for _, row in sheet_rows(workbook["Copy of Bosta Compensation "]):
        compensation_rows += 1
        compensation_total += as_float(row.get("Compensation Amount")) or 0.0
    result["bosta_compensation"] = {
        "rows": compensation_rows,
        "total_egp": round(compensation_total, 2),
    }

    refund_total = 0.0
    refund_rows = 0
    for _, row in sheet_rows(workbook["Copy of Return Bosta"]):
        refund_rows += 1
        refund_total += as_float(row.get("Amount")) or 0.0
    result["return_bosta"] = {
        "rows": refund_rows,
        "total_egp": round(refund_total, 2),
    }

    staff_total = 0.0
    staff_rows = 0
    for _, row in sheet_rows(workbook["Copy of Staff Orders"]):
        staff_rows += 1
        staff_total += as_float(row.get("Order Price")) or 0.0
    result["staff_orders"] = {
        "rows": staff_rows,
        "total_egp": round(staff_total, 2),
    }

    oos_reasons = Counter()
    oos_rows = 0
    for _, row in sheet_rows(workbook["OOS Orders"]):
        oos_rows += 1
        oos_reasons[norm(row.get("Reason For Late")) or "(blank)"] += 1
    result["oos_orders"] = {
        "rows": oos_rows,
        "by_reason": [{"reason": r, "count": c} for r, c in oos_reasons.most_common()],
    }

    return result


def build_seed(workbook, limit=600):
    """Anonymised rows for the prototype: real vocabulary, redacted free text.

    Sampled by ORDER rather than by row. Items belonging to one order sit
    adjacent in the sheet, so sampling every Nth row would split multi-vendor
    orders apart and the prototype could not demonstrate item-level splitting -
    the single most important concept in the design. Whole orders are kept
    intact, sampled evenly across the file so the demo still spans the full date
    range, vendor mix and status distribution.
    """
    worksheet = workbook["Copy of Orders"]

    groups = {}
    order = []
    for _, row in sheet_rows(worksheet):
        # Only seed rows that carry enough signal to render a useful demo screen.
        if not norm(row.get("Vendor Name")) or not norm(row.get("Final status")):
            continue
        ref = norm(row.get("Customer Orders")) or norm(row.get("Vendor Orders"))
        key = (ref or "#unknown").split("-")[0]
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(row)

    # Interleave multi-item orders with the even sample so the demo reliably has
    # several to show, without over-representing them relative to the real 22%.
    multi = [k for k in order if len(groups[k]) > 1]
    step = max(1, len(order) // max(1, limit // 2))
    picked, seen = [], set()
    for key in ([k for k in multi[:: max(1, len(multi) // 40)]] + order[::step] + order):
        if key in seen:
            continue
        seen.add(key)
        picked.append(key)
        if sum(len(groups[k]) for k in picked) >= limit:
            break

    seed = []
    for key in picked:
        for row in groups[key]:
            seed.append({
                "orderDate": norm(row.get("Order date")),
                "vendorOrder": norm(row.get("Vendor Orders")),
                "customerOrder": norm(row.get("Customer Orders")),
                "split": norm(row.get("Multi or Single")),
                "vendor": norm(row.get("Vendor Name")),
                "awbState": norm(row.get("AWB")),
                "sku": norm(row.get("SKU")),
                "itemName": norm(row.get("Item Name")),
                "itemPrice": as_float(row.get("Item price")),
                "shippingFees": as_float(row.get("Shipping Fees")),
                "paymentMethod": norm(row.get("Payment Method")),
                "quantity": as_float(row.get("Lineitem quantity")),
                "governorate": norm(row.get("Governorate")),
                "area": norm(row.get("Area")),
                "awbCreatedAt": norm(row.get("AWB Creation Date")),
                "csSla": as_float(row.get("CS SLA")),
                "pickupAt": norm(row.get("Bosta Pick up")),
                "fmSla": as_float(row.get("FM SLA")),
                "deliveredAt": norm(row.get("Delivere Date")),
                "deliverySla": as_float(row.get("Delivere SLA")),
                "returnRequestedAt": norm(row.get("Return Request Date")),
                "returnedAt": norm(row.get("Return Date")),
                "finalStatus": norm(row.get("Final status")),
                "stakeholder": norm(row.get("Stakeholder")),
                "reason": norm(row.get("Reasons")),
                "penalty": norm(row.get("Vendor Penalty")),
                "recallStatus": norm(row.get("Recall Status")),
                "flexShip": norm(row.get("Bosta FlexShip")),
                # Redacted: the source column holds Arabic customer/CS notes.
                "hasNote": bool(norm(row.get("Comment"))),
            })
    return seed


def write(name, payload):
    path = OUT / name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  wrote {path.relative_to(ROOT)}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"Reading {WORKBOOK.name} (read-only)")
    workbook = openpyxl.load_workbook(WORKBOOK, read_only=True, data_only=True)

    write("schema.json", profile_schema(workbook))
    write("enums.json", profile_enums(workbook))
    orders = profile_orders(workbook)
    write("metrics.json", orders)
    write("supporting.json", profile_supporting(workbook))
    write("seed.json", build_seed(workbook))

    totals = orders["totals"]
    print("\nHeadline figures for the proposal:")
    print(f"  period            {orders['period']['from']} -> {orders['period']['to']}")
    print(f"  item rows         {totals['item_rows']:,}")
    print(f"  customer orders   {totals['unique_customer_orders']:,}")
    print(f"  vendors           {totals['vendors']}")
    print(f"  GMV               {totals['gmv_egp']:,.0f} EGP")
    print(f"  delivery rate     {totals['delivery_rate']:.1%}")
    print(f"  return/RTO rate   {totals['return_rate']:.1%} "
          f"({totals['return_or_rto_items']:,} items)")
    print(f"  exchange items    {totals['exchange_items']:,}")
    print(f"  flex shipping     {totals['flex_shipping_applied']:,}")


if __name__ == "__main__":
    main()
