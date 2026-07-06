# OMNOM Token Holder Snapshots

Historical holder snapshots for the **OMNOM** ERC-20 token on **Dogechain** (now shut down).

> **Dogechain shutdown:** Announced June 8, 2026, ~60-day window → estimated shutdown ~August 7, 2026. These snapshots preserve the on-chain state before the chain went offline.

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

## Snapshot Index

### Primary Snapshot (Final)

The canonical snapshot taken at the moment of the OMNOM token announcement.

| Field | Value |
|-------|-------|
| Date | June 7, 2026 23:59:58 UTC |
| Block | 59,922,100 |
| Holders | 25,431 |
| Method | Full holder list via BlockScout API |

**Files:**
- `omnom-snapshot-FINAL.json` — Full JSON with all holders, ranked by balance (5.8 MB, 178K lines)
- `omnom-snapshot-pre-announcement.csv` — CSV format (25,432 rows including header, 2.5 MB)
- `HASHES.json` — SHA-256 hashes for verification

### Pre-Announcement Snapshot

Held separately from the FINAL — taken before the OMNOM public announcement.

**File:** `omnom-snapshot-pre-announcement.csv` (also the source for the Telegram bot lookup)

### Weekly Snapshots

Tracking holder changes during the Dogechain bridge window (June 8 → August 7, 2026).

| Week | Date | Block | Holders | Δ from Baseline | Method |
|------|------|-------|---------|-----------------|--------|
| Baseline | Jun 7 | 59,922,100 | 25,431 | — | BlockScout API |
| Week 1 | Jun 14 | 60,224,436 | 25,344 | -87 | Backfill (transfer events) |
| Week 2 | Jun 21 | 60,526,824 | 25,388 | -43 | Backfill (transfer events) |
| Week 3 | Jun 28 | 60,825,305 | 25,442 | +11 | Live cron (top 100 only) |
| Week 4 | Jul 5 | 61,131,617 | 25,474 | +43 | Backfill (transfer events) |

**Files in `weekly/`:**
- `weekly-2026-06-14.json` + `.csv` — Full holder list (backfilled, 6 MB each)
- `weekly-2026-06-21.json` + `.csv` — Full holder list (backfilled, 6 MB each)
- `weekly-2026-06-28.json` — Top 100 holders only (live cron snapshot, 12 KB)
- `weekly-2026-07-05.json` + `.csv` — Full holder list (backfilled, 6 MB each)

#### Methods

1. **Backfill** (`backfill_snapshot.py`): Forward-applies Transfer events from baseline block to target block using `eth_getLogs`. Produces full accurate holder lists. Used for Weeks 1–2.
2. **Live cron** (`weekly_snapshot.py`): Fetches current holders from BlockScout API at execution time. Only saves top 100 to keep file sizes manageable. Used from Week 3 onward.

#### Why Week 3 is smaller

The weekly cron script (`weekly_snapshot.py`) only captures the top 100 holders + distribution metadata. The backfill script captures ALL holders but requires RPC access to replay transfer events. After Week 3, the cron continued running until the final snapshot date (Aug 3) — if additional weekly files exist post-shutdown they were not recovered.

---

## Scripts

| Script | Purpose |
|--------|---------|
| `backfill_snapshot.py` | Reconstructs historical holder snapshots by replaying Transfer events from a baseline block. Binary search for exact block at target timestamp. |
| `weekly_snapshot.py` | Live weekly snapshot for cron. Fetches current holders from BlockScout API. Built-in end-date guard (stops after Aug 3, 2026). |
| `lookup.sh` | Shell script used by the Telegram bot (`@DBOT_DC_BOT`) for OMNOM wallet lookups against the FINAL snapshot. |

### Backfill Usage

```bash
python3 backfill_snapshot.py "Week 1" "2026-06-14T23:59:58+00:00"
```

Outputs JSON + CSV to `weekly/` directory.

### Cron Schedule (historical)

- **Schedule:** `58 23 * * 0` (every Sunday 23:59:58 UTC)
- **End date:** August 3, 2026 (final snapshot before estimated shutdown)
- After end date, script exits with "END DATE REACHED" message

---

## Telegram Bot

The OMNOM wallet lookup bot runs on `@DBOT_DC_BOT` (Hermes agent). Send any wallet address (0x-prefixed, 42 hex chars) to get the holder's OMNOM balance, rank, and supply percentage from the FINAL snapshot.

**Response format:**
```
🐕 $OMNOM Snapshot Lookup
💰 Balance: <AMOUNT>
📊 Supply: <PERCENTAGE>%
🏷️ Rank: #<RANK> of 25,431
🐋/🐬/🐟 <CLASSIFICATION>
📅 Snapshot: June 7, 2026 23:59:58 UTC (Block 59,922,100)
```

---

## Data Integrity

- `HASHES.json` contains SHA-256 hashes for the primary snapshot files
- Backfill reconciliation: Weeks 1–2 both achieved 99.99999% balance reconciliation (forward-applied transfers match expected supply)
- Zero negative balances in all snapshots

---

## Dogechain Shutdown Context

- **Announced:** June 8, 2026 by @DogechainFamily
- **Window:** ~60 days → estimated shutdown ~August 7, 2026
- **RPC status at last check:** `rpc.dogechain.dog` dead, `rpc01-sg.dogechain.dog` dead, `rpc.thirdweb.com/dogechain` alive (but chain may be frozen post-shutdown)
- **BlockScout Explorer:** `explorer.dogechain.dog` — API partially functional (account/txlist works, stats/tokenlist broken)
- **Final snapshot:** August 3, 2026 (Sunday before estimated shutdown)

---

## Future: OMNOM v2 on DogeOS?

These snapshots preserve the canonical holder list. If OMNOM is redeployed on **DogeOS** (MyDoge's EVM ZK rollup), this data enables:

1. **Airdrop/claim** for verified holders from the original snapshot
2. **Holder verification** without needing live Dogechain RPC
3. **Historical record** of the original distribution

---

## License

Data in this repository is on-chain public information. Scripts are provided as-is for reference.

---

*Archived by [DBOT](https://www.dbot.dog) — preserving Dogecoin ecosystem data.*
