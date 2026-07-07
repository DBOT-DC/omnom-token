# OMNOM Token Holder Snapshots

Historical holder snapshots for the **OMNOM** ERC-20 token on **Dogechain**.

> **Dogechain shutdown:** Announced June 8, 2026, ~60-day window → estimated shutdown ~August 7, 2026. Snapshots are collected weekly until the chain goes offline.

---

## Token Details

| Field | Value |
|-------|-------|
| Token | OMNOM |
| Contract | `0xe3fcA919883950c5cD468156392a6477Ff5d18de` |
| Chain | Dogechain (PoS sidechain on Dogecoin) |
| Decimals | 18 |
| Total Supply | 1,000,000,000,000,000 OMNOM (1 Quadrillion) |

---

## Snapshot Files

### Ever-Held Master List (Default Lookup)

The **union of all snapshots** — anyone who held OMNOM at any point during the snapshot window. Used for wallet lookups and airdrop eligibility.

| Field | Value |
|-------|-------|
| File | `omnom-snapshot-ever-held.csv` |
| Format | Tab-delimited |
| Holders | 25,591 (unique, all-time) |
| Source | Pre-announcement + all weekly snapshots merged |
| Columns | `rank`, `address`, `max_balance_raw`, `max_pct`, `best_rank`, `snapshot_count`, `snapshots`, `first_seen` |

**What it captures:**
- Current holders (still hold OMNOM)
- Past holders (held in any snapshot but since sold/transferred)
- Snapshot history per wallet (which weeks they appeared in, peak balance, first seen)

**Who it misses:** MEXC off-chain holdings (users who never transferred to Dogechain on-chain).

### Current Holders (Latest)

The most recent weekly snapshot — holders with non-zero OMNOM balance right now.

| Field | Value |
|-------|-------|
| File | `omnom-snapshot-latest.csv` |
| Format | CSV (comma-delimited) |
| Holders | 25,474 (as of Jul 5, 2026) |
| Columns | `rank`, `address`, `balance_raw`, `balance_formatted`, `percentage_of_supply` |

Used by the lookup script to determine `CURRENTLY_HOLDS: yes/no`.

### Pre-Announcement Snapshot (Baseline)

The canonical snapshot taken before the OMNOM public announcement.

| Field | Value |
|-------|-------|
| Date | June 7, 2026 23:59:58 UTC |
| Block | 59,922,100 |
| Holders | 25,431 |
| File | `omnom-snapshot-pre-announcement.csv` (2.5 MB) |

### Primary Snapshot (Final)

| Field | Value |
|-------|-------|
| File | `omnom-snapshot-FINAL.json` (5.8 MB, 178K lines) |
| Method | Full holder list via BlockScout API |

---

## Weekly Snapshots

Tracking holder changes during the Dogechain bridge window (June 8 → August 7, 2026).

| Week | Date | Block | Holders | Δ from Baseline | Method |
|------|------|-------|---------|-----------------|--------|
| Baseline | Jun 7 | 59,922,100 | 25,431 | — | BlockScout API |
| Week 1 | Jun 14 | 60,224,436 | 25,344 | -87 | Backfill (transfer events) |
| Week 2 | Jun 21 | 60,526,824 | 25,388 | -43 | Backfill (transfer events) |
| Week 3 | Jun 28 | 60,829,218 | 25,442 | +11 | Backfill (transfer events) |
| Week 4 | Jul 5 | 61,131,617 | 25,474 | +43 | Backfill (transfer events) |

**Files in `weekly/`:** JSON + CSV pairs for each week.

### Ever-Held Data Flow

```
pre-announcement.csv ──┐
weekly/w1.csv ──────────┤
weekly/w2.csv ──────────┼──▶ merge ──▶ omnom-snapshot-ever-held.csv (25,591 holders)
weekly/w3.csv ──────────┤                      │
weekly/w4.csv ──────────┘                      ├──▶ omnom-snapshot-latest.csv (current only)
                                               │
                                               └──▶ lookup.sh (ever-held mode)
```

Each weekly cron run:
1. Fetches fresh holders from BlockScout → saves `weekly/YYYY-MM-DD.csv`
2. Copies to `omnom-snapshot-latest.csv` (for CURRENTLY_HOLDS check)
3. Merges ALL snapshots → regenerates `omnom-snapshot-ever-held.csv` (for lookup + airdrop)

---

## Scripts

| Script | Purpose |
|--------|---------|
| `lookup.sh` | Wallet lookup for Telegram bot — ever-held mode. Returns balance, rank, class, snapshot history, currently holds status |
| `weekly_snapshot.py` | Live weekly snapshot for cron. Fetches current holders from BlockScout API. Updates `latest.csv` + merges into `ever-held.csv`. Built-in end-date guard (stops after Aug 3, 2026) |
| `backfill_snapshot.py` | Reconstructs historical holder snapshots by replaying Transfer events from baseline block. Binary search for exact block at target timestamp |

### Lookup Usage

```bash
./lookup.sh 0xab5801a7d398351b8be11c439e05c5b3259aec9b
```

**Output fields:**
- `STATUS:EVER_HELD` / `NOT_FOUND`
- `RANK` — rank in ever-held list (by max balance)
- `BEST_RANK` — best rank across all snapshots
- `BALANCE` — max balance ever held (formatted)
- `PERCENTAGE` — max supply percentage
- `CLASS` — 🐋 Whale (≥1%) / 🐬 Dolphin (≥0.01%) / 🐟 Fish (<0.01%)
- `SNAPSHOTS` — count + which snapshots the address appeared in
- `FIRST_SEEN` — first snapshot the address appeared in
- `CURRENTLY_HOLDS` — `yes` if in latest snapshot, `no` if sold

### Cron Schedule

- **Schedule:** `58 23 * * 0` (every Sunday 23:59:58 UTC)
- **End date:** August 3, 2026 (final snapshot before estimated shutdown)
- After end date, script exits with "END DATE REACHED" message

---

## Telegram Bot

The OMNOM wallet lookup bot runs on `@DBOT_DC_BOT` (Hermes agent). Send any wallet address (0x-prefixed, 42 hex chars) in DM or the OMNOM Telegram channel.

**Lookup mode:** Ever-held (default). Shows:
- 🐕 **Ever-held wallet (still holds):** Current balance, rank, class, snapshot history
- 📤 **Ever-held wallet (sold):** Peak balance, when they held, `CURRENTLY_HOLDS: no`
- ❌ **Not found:** Never appeared in any on-chain snapshot

---

## Data Integrity

- `HASHES.json` contains SHA-256 hashes for snapshot files
- Backfill reconciliation: All weekly snapshots achieve >99.99% balance reconciliation (forward-applied transfers match expected supply). Zero negative balances.
- Ever-held merge verified: 25,591 unique holders (25,431 pre-announcement + 160 new in weekly snapshots)

---

## Dogechain Shutdown Context

- **Announced:** June 8, 2026 by @DogechainFamily
- **Window:** ~60 days → estimated shutdown ~August 7, 2026
- **RPC status (Jul 7, 2026):** `rpc.dogechain.dog` alive, `dogechain.rpc.thirdweb.com` alive
- **BlockScout Explorer:** `explorer.dogechain.dog` — API partially functional
- **Final snapshot target:** August 3, 2026

---

## Future: OMNOM v2 on DogeOS?

These snapshots preserve the canonical holder list. If OMNOM is redeployed on **DogeOS** (MyDoge's EVM ZK rollup), this data enables:

1. **Airdrop/claim** for verified ever-held wallets
2. **Holder verification** without needing live Dogechain RPC
3. **Historical record** of the original distribution

---

## License

Data in this repository is on-chain public information. Scripts are provided as-is for reference.

---

*Archived by [DBOT](https://www.dbot.dog) — preserving Dogecoin ecosystem data.*
