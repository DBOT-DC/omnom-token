#!/usr/bin/env python3
"""
Weekly OMNOM holder snapshot during Dogechain bridge window.
Tracks holder changes, bridging activity, and supply distribution.
Run weekly via Hermes cron during the 60-day shutdown window (Jun 8 - Aug 8, 2026).

Schedule: Every Sunday 23:59:58 UTC (cron: 58 23 * * 0)
Final snapshot: Aug 3, 2026 (Sunday before estimated shutdown ~Aug 7)
After final snapshot, script exits with message and cron should be disabled.

Baseline: Jun 7, 2026 23:59:58 UTC (block 59,922,100) — 25,431 holders
"""
import json, time, os, hashlib, requests, csv
from datetime import datetime, timezone

RPCS = ["https://dogechain.rpc.thirdweb.com", "https://rpc01-sg.dogechain.dog", "https://rpc.dogechain.dog"]
OMNOM = "0xe3fcA919883950c5cD468156392a6477Ff5d18de"
DECIMALS = 18
EXPECTED_SUPPLY = 10**DECIMALS * 10**15  # 1,000,000,000,000,000

# Dogechain shutdown: announced Jun 8, ~60 days → ~Aug 7. Final snapshot Aug 3 (Sun before).
FINAL_SNAPSHOT_DATE = datetime(2026, 8, 3, 23, 59, 58, tzinfo=timezone.utc)
SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), "weekly")
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

BASELINE_BLOCK = 59_922_100
BASELINE_HOLDERS = 25_431
BASELINE_DATE = "2026-06-07T23:59:58Z"


def get_latest_block():
    for rpc in RPCS:
        try:
            r = requests.post(rpc, json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}, timeout=10)
            return int(r.json()["result"], 16)
        except:
            continue
    return None


def get_total_supply(block):
    data = "0x18160ddd"
    for rpc in RPCS:
        try:
            r = requests.post(rpc, json={"jsonrpc": "2.0", "method": "eth_call", "params": [{"to": OMNOM, "data": data}, hex(block)], "id": 1}, timeout=10)
            return int(r.json()["result"], 16)
        except:
            continue
    return None


def get_holders_from_blockscout():
    """Fetch current holders from BlockScout API."""
    BASE = "https://explorer.dogechain.dog"
    all_holders = []
    page = 1
    offset = 10000

    while True:
        url = f"{BASE}/api?module=token&action=getTokenHolders&contractaddress={OMNOM}&page={page}&offset={offset}"
        try:
            resp = requests.get(url, timeout=30)
            data = resp.json()
            if data.get("status") == "1" and data.get("result"):
                result = data["result"]
                if not result:
                    break
                all_holders.extend(result)
                page += 1
            else:
                break
        except:
            break
    return all_holders


def main():
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    # End-date guard: stop after final snapshot
    if now > FINAL_SNAPSHOT_DATE:
        print(f"⛔ END DATE REACHED: {FINAL_SNAPSHOT_DATE.isoformat()}")
        print(f"   Dogechain estimated shutdown ~Aug 7, 2026. Final snapshot was Aug 3.")
        print(f"   This cron should be disabled. Exiting.")
        return

    # Warning if within 1 week of final snapshot
    days_remaining = (FINAL_SNAPSHOT_DATE - now).total_seconds() / 86400
    if days_remaining <= 7:
        print(f"⚠️ FINAL SNAPSHOT WINDOW: {days_remaining:.0f} days until last scheduled snapshot")

    latest_block = get_latest_block()

    if not latest_block:
        print("ERROR: Could not connect to any RPC")
        return

    print(f"Weekly snapshot: {timestamp}")
    print(f"Latest block: {latest_block}")

    total_supply = get_total_supply(latest_block)
    print(f"Total supply: {total_supply / 10**DECIMALS:,.2f} OMNOM" if total_supply else "Supply: unknown")

    holders = get_holders_from_blockscout()
    print(f"Holders from BlockScout: {len(holders)}")

    total_bal = sum(int(h['value']) for h in holders)
    sorted_holders = sorted(holders, key=lambda x: int(x['value']), reverse=True)

    top10 = sum(int(h['value']) for h in sorted_holders[:10])
    top100 = sum(int(h['value']) for h in sorted_holders[:100])

    snapshot = {
        "snapshot_method": "BlockScout API current holders (real-time snapshot)",
        "snapshot_date": timestamp,
        "block_number": latest_block,
        "token": "OMNOM",
        "contract": OMNOM,
        "chain": "dogechain",
        "decimals": DECIMALS,
        "total_supply": str(total_supply) if total_supply else "unknown",
        "holders_count": len(sorted_holders),
        "total_balance_raw": str(total_bal),
        "total_balance_formatted": f"{total_bal / 10**DECIMALS:,.2f}",
        "top10_pct": f"{top10 / EXPECTED_SUPPLY * 100:.2f}%",
        "top100_pct": f"{top100 / EXPECTED_SUPPLY * 100:.2f}%",
        "holders_top100": sorted_holders[:100],
        "distribution": {
            "top10_addresses": [h.get("address") or h.get("holderAddress", "") for h in sorted_holders[:10]],
            "top10_pct": f"{top10 / EXPECTED_SUPPLY * 100:.2f}%",
            "top100_pct": f"{top100 / EXPECTED_SUPPLY * 100:.2f}%",
        },
        "baseline_ref": {
            "block": BASELINE_BLOCK,
            "date": BASELINE_DATE,
            "holders": BASELINE_HOLDERS,
        },
        "reconciliation": {
            "baseline_holders": BASELINE_HOLDERS,
            "current_holders": len(sorted_holders),
            "holder_change": len(sorted_holders) - BASELINE_HOLDERS,
        },
    }

    date_str = now.strftime("%Y-%m-%d")
    filename = f"weekly-{date_str}.json"
    filepath = os.path.join(SNAPSHOT_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(snapshot, f, indent=2)

    with open(filepath, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    print(f"Saved: {filepath}")
    print(f"SHA-256: {file_hash}")

    # Also save CSV
    csv_path = os.path.join(SNAPSHOT_DIR, f"weekly-{date_str}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["rank", "address", "balance_raw", "balance_formatted", "percentage_of_supply"])
        writer.writeheader()
        for i, h in enumerate(sorted_holders):
            addr = h.get("address") or h.get("holderAddress", "")
            writer.writerow({
                "rank": i + 1,
                "address": addr,
                "balance_raw": h["value"],
                "balance_formatted": f"{int(h['value']) / 10**DECIMALS:.18f}",
                "percentage_of_supply": f"{int(h['value']) / EXPECTED_SUPPLY * 100:.6f}",
            })
    print(f"CSV: {csv_path}")

    # Copy to lookup path for OMNOM wallet bot
    import shutil
    LOOKUP_PATH = "/Users/penny/.openclaw-telegram/workspace/omnom-snapshot/omnom-snapshot-latest.csv"
    shutil.copy2(csv_path, LOOKUP_PATH)
    print(f"Lookup updated: {LOOKUP_PATH}")

    # Update ever-held master list for airdrop eligibility
    EVER_HELD_PATH = "/Users/penny/.openclaw-telegram/workspace/omnom-snapshot/omnom-snapshot-ever-held.csv"
    PRE_PATH = "/Users/penny/.openclaw-telegram/workspace/omnom-snapshot/omnom-snapshot-pre-announcement.csv"
    
    all_sources = [PRE_PATH]
    if os.path.exists(WEEKLY_DIR):
        for f in sorted(os.listdir(WEEKLY_DIR)):
            if f.endswith(".csv"):
                all_sources.append(os.path.join(WEEKLY_DIR, f))
    
    ever_holders = {}
    for src in sorted(all_sources):
        src_label = os.path.basename(src).replace(".csv", "").replace("omnom-snapshot-", "")
        try:
            with open(src, newline="") as sf:
                for row in csv.DictReader(sf):
                    addr = row["address"].lower()
                    bal_raw = int(row["balance_raw"])
                    if addr not in ever_holders:
                        ever_holders[addr] = {
                            "max_balance_raw": bal_raw,
                            "max_balance_formatted": row["balance_formatted"],
                            "max_pct": float(row["percentage_of_supply"]),
                            "best_rank": int(row["rank"]),
                            "snapshots": [src_label],
                            "first_seen": src_label,
                        }
                    else:
                        if bal_raw > ever_holders[addr]["max_balance_raw"]:
                            ever_holders[addr]["max_balance_raw"] = bal_raw
                            ever_holders[addr]["max_balance_formatted"] = row["balance_formatted"]
                            ever_holders[addr]["max_pct"] = float(row["percentage_of_supply"])
                        if int(row["rank"]) < ever_holders[addr]["best_rank"]:
                            ever_holders[addr]["best_rank"] = int(row["rank"])
                        if src_label not in ever_holders[addr]["snapshots"]:
                            ever_holders[addr]["snapshots"].append(src_label)
        except Exception as e:
            print(f"  Warning: could not read {src}: {e}")
    
    sorted_ever = sorted(ever_holders.items(), key=lambda x: x[1]["max_balance_raw"], reverse=True)
    with open(EVER_HELD_PATH, "w", newline="") as ef:
        writer = csv.writer(ef)
        writer.writerow(["rank", "address", "max_balance_raw", "max_balance_formatted",
                         "max_percentage", "best_rank", "snapshot_count", "snapshots", "first_seen"])
        for i, (addr, data) in enumerate(sorted_ever):
            writer.writerow([i + 1, addr, data["max_balance_raw"], data["max_balance_formatted"],
                             f"{data['max_pct']:.6f}", data["best_rank"], len(data["snapshots"]),
                             ",".join(data["snapshots"]), data["first_seen"]])
    print(f"Ever-held updated: {EVER_HELD_PATH} ({len(sorted_ever):,} total unique holders)")

    # Baseline comparison
    diff = len(sorted_holders) - BASELINE_HOLDERS
    print(f"\nBaseline comparison (Jun 7, block {BASELINE_BLOCK}):")
    print(f"  Pre-announcement holders: {BASELINE_HOLDERS:,}")
    print(f"  Current holders: {len(sorted_holders):,}")
    print(f"  Change: {'+' if diff >= 0 else ''}{diff}")
    print(f"  Top 10 hold: {top10 / EXPECTED_SUPPLY * 100:.2f}%")
    print(f"  Top 100 hold: {top100 / EXPECTED_SUPPLY * 100:.2f}%")

    # Final snapshot marker
    if days_remaining <= 7:
        print(f"\n🏁 This is a FINAL-WINDOW snapshot ({days_remaining:.0f} days before end date)")


if __name__ == "__main__":
    main()
