# OMNOM Snapshot Session — June 28, 2026

## What Was Done

### 1. Backfill Script Built (`backfill_snapshot.py`)
- **Method:** Forward-applies Transfer events from baseline (Jun 7, block 59,922,100) to any target block
- Binary search finds exact block at target timestamp (Week 1: 1s off, Week 2: exact)
- Fetches ALL Transfer events via `eth_getLogs` with chunked requests
- Tracks new holders, departed holders, balance changes with 100% accuracy
- CLI: `python3 backfill_snapshot.py "Label" "2026-06-14T23:59:58+00:00"`

### 2. Weeks 1 & 2 Backfilled

| Week | Date | Block | Holders | Δ | Events | New | Departed | Reconciliation |
|------|------|-------|---------|---|--------|-----|----------|---------------|
| Baseline | Jun 7 | 59,922,100 | 25,431 | — | — | — | — | 99.99% |
| Week 1 | Jun 14 | 60,224,436 | 25,344 | -87 | 3,254 | 72 | 156 | 99.99999% |
| Week 2 | Jun 21 | 60,526,824 | 25,388 | -43 | 3,867 | 148 | 185 | 99.99999% |

- Zero negative balances in both
- Files: `weekly/weekly-2026-06-14.json`, `weekly/weekly-2026-06-21.json` (+ CSV copies)

### 3. Weekly Snapshot Cron Fixed
- **Cron ID:** `4c34a45e15b7`
- **Schedule:** `58 23 * * 0` (Sunday 23:59:58 UTC)
- **Script:** `weekly_snapshot.py` — RPC primary reordered (thirdweb first, dead rpc.dogechain.dog last)
- **End-date guard:** Exits after Aug 3, 2026 with "END DATE REACHED"
- **Cron prompt:** Instructs agent to disable job when end-date triggers
- **workdir:** `~/Documents/DBOT-Vault-Final/03-Research/Dogechain/omnom-snapshot/`

### 4. Telegram Community Update Posted & Pinned
- **Channel:** @omnomtoken_dc
- **msg_id:** 114512
- Covers: primary snapshot, all weekly dates, backfill method, shutdown deadline, bot usage
- **Bot username for DMs:** @DBOT_DC_BOT (Hermes bot, admin with pin/delete rights)
- First post (msg_id=114510) had wrong bot handle (@PennybagsCX_bot) — unpinned and corrected

### 5. Dogechain Shutdown Timeline Research
- @DogechainFamily announced June 8: "roughly 60 days" → ~August 7
- QuickSwap (Jun 18): "team will announce more detailed timelines soon"
- BingX: "deadline falls around early August"
- **No exact date published** as of June 28
- RPC status: `rpc.dogechain.dog` dead, thirdweb alive, BlockScout API alive
- Final snapshot: Aug 3 (Sunday before estimated shutdown)

### 6. Documentation Updated
- `OMNOM-BOT-IMPLEMENTATION.md` — full snapshot table, shutdown timeline, RPC status, bot username, pinned post ref
- `omnom-wallet-lookup` skill (SKILL.md) — community update section, backfill verification details
- Hermes memory — Dogechain shutdown date, snapshot plan, cron ID, file locations, bot username, pinned msg

## Key Files

| File | Location | Purpose |
|------|----------|---------|
| Baseline snapshot | `omnom-snapshot-FINAL.json` (6MB) | Primary Jun 7 data |
| Lookup CSV | `omnom-snapshot-pre-announcement.csv` (2.6MB) | Bot lookup source |
| Lookup script | `lookup.sh` | Shell wrapper for bot |
| Weekly script | `weekly_snapshot.py` | Cron job (live snapshots) |
| Backfill script | `backfill_snapshot.py` | Historical accurate snapshots |
| Week 1 JSON | `weekly/weekly-2026-06-14.json` (6MB) | Backfilled |
| Week 1 CSV | `weekly/weekly-2026-06-14.csv` (2.7MB) | Backfilled |
| Week 2 JSON | `weekly/weekly-2026-06-21.json` (6MB) | Backfilled |
| Week 2 CSV | `weekly/weekly-2026-06-21.csv` (2.7MB) | Backfilled |
| Week 3 JSON | `weekly/weekly-2026-06-28.json` (13KB) | Live (cron fires tonight) |
| Cron config | `~/.hermes/cron/jobs.json` | Job 4c34a45e15b7 |
| Skill | `~/.hermes/skills/blockchain/omnom-wallet-lookup/SKILL.md` | Full bot docs |

## Schedule Going Forward

| Week | Date (23:59:58 UTC) | Status |
|------|---------------------|--------|
| Week 3 | Jun 28 (tonight) | 🟡 Cron fires tonight |
| Week 4 | Jul 5 | 📅 Scheduled |
| Week 5 | Jul 12 | 📅 Scheduled |
| Week 6 | Jul 19 | 📅 Scheduled |
| Week 7 | Jul 26 | 📅 Scheduled |
| Final | Aug 3 | 🏁 Last before ~Aug 7 shutdown |

## Open Items

- Monitor for exact Dogechain shutdown date announcement — adjust final snapshot if needed
- If Dogechain announces different shutdown date, update `FINAL_SNAPSHOT_DATE` in `weekly_snapshot.py` and `end_guard` in cron job
- After final snapshot (Aug 3), disable cron job `4c34a45e15b7`
- Once all RPCs die post-shutdown, no more verification possible — archive all data
