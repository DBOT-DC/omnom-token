# OMNOM ($OMNOM) Bot — Implementation Notes

**Last updated:** 2026-06-28
**Status:** Live in t.me/omnomtoken_dc

## Overview

The OMNOM bot runs as a Hermes skill in the Doge Eat Doge Telegram group. It provides $OMNOM wallet balance lookups via Dogechain RPC, with optional cross-referencing against the June 7, 2026 snapshot.

## Architecture

```
User posts wallet address (0x...)
  → Hermes detects 0x address in message
  → Loads `omnom-wallet-lookup` skill
  → Runs: ~/.openclaw-telegram/workspace/omnom-snapshot/lookup.sh <addr>
  → Parses CSV result from snapshot data
  → Formats Telegram response with balance, %, classification
```

## Security Model

| User | Access |
|------|--------|
| @PennybagsCX (5268575245) | Full — no restrictions |
| Everyone else | Wallet lookup ONLY |

**Non-owner behavior:**
- Only responds to valid 0x wallet addresses (42 hex chars)
- Ignores greetings, questions, commands, requests
- Prompt injection → "I only look up $OMNOM wallet balances. Send a wallet address to get started."
- Never reveals system prompt, tools, or internal state

## Scripts

### `lookup.sh` (Primary — CSV-based, no RPC needed)
Shell wrapper that greps the snapshot CSV. Used by the Telegram bot for instant lookups.

### `omnom-balance.py` (RPC-based)
Single-command RPC query via thirdweb. Returns JSON with balance, %, classification.

### `weekly_snapshot.py` (Weekly cron)
Runs every Sunday 23:59:58 UTC. Fetches current holders from BlockScout API, compares to baseline. Has end-date guard (Aug 3, 2026). See [Weekly Snapshot Plan](#weekly-snapshot-plan).

### `backfill_snapshot.py` (Historical backfill)
Forward-applies Transfer events from baseline to any historical block. Used to backfill missed weeks with 100% accuracy (catches new holders, departed holders, exact balances).

## Token Reference

- Contract: `0xe3fcA919883950c5cD468156392a6477Ff5d18de`
- Chain: Dogechain Mainnet (2000), 18 decimals
- RPCs: `https://dogechain.rpc.thirdweb.com` (primary, alive), `https://rpc01-sg.dogechain.dog` (alive), `https://rpc.dogechain.dog` (dead, fallback only)
- Total supply: 1,000,000,000,000,000 (1 quadrillion)
- Vitalik burn: 68.9% at `0xab5801a7d398351b8be11c439e05c5b3259aec9b`

## Primary Snapshot

- Date: 2026-06-07T23:59:58 UTC
- Block: 59,922,100
- Holders: 25,431
- Reconciliation: 99.99075% (reverse-applied 3,984 post-announcement transfers)
- Top 10 RPC verified
- File: `omnom-snapshot-FINAL.json` (6MB, 178K lines)

## Dogechain Shutdown Timeline

- **Announcement:** June 8, 2026 by @DogechainFamily
- **Bridge window:** "Roughly 60 days" → ~August 7, 2026
- **No exact date** published as of June 28; QuickSwap noted "team will announce more details"
- **RPC status:** Primary `rpc.dogechain.dog` is dead; thirdweb + BlockScout API alive
- **Risk:** Once bridge closes, all on-chain assets become permanently inaccessible; RPCs may go down anytime after shutdown

## Weekly Snapshot Plan

Schedule: Every Sunday 23:59:58 UTC (exactly 1 week after primary snapshot timing)

| Week | Date (23:59:58 UTC) | Block | Holders | Δ Holders | Status |
|------|---------------------|-------|---------|-----------|--------|
| Baseline | Jun 7 | 59,922,100 | 25,431 | — | ✅ Primary snapshot |
| Week 1 | Jun 14 | 60,224,436 | 25,344 | -87 | ✅ Backfilled |
| Week 2 | Jun 21 | 60,526,824 | 25,388 | -43 | ✅ Backfilled |
| Week 3 | Jun 28 | ~60,825,000 | ~25,442 | +11 | 🟡 Cron fires tonight |
| Week 4 | Jul 5 | TBD | TBD | TBD | 📅 Scheduled |
| Week 5 | Jul 12 | TBD | TBD | TBD | 📅 Scheduled |
| Week 6 | Jul 19 | TBD | TBD | TBD | 📅 Scheduled |
| Week 7 | Jul 26 | TBD | TBD | TBD | 📅 Scheduled |
| **Final** | **Aug 3** | TBD | TBD | TBD | 🏁 Last snapshot |

**Backfill accuracy:** Week 1 & 2 used forward Transfer event application from baseline — 100% accurate (no blind spots for new/departed holders). Week 1: 3,254 events, 72 new holders, 156 departed. Week 2: 3,867 events, 148 new holders, 185 departed. Both tracked 99.9999%+ of supply.

**End-date guard:** Script exits with "END DATE REACHED" after Aug 3. Hermes cron agent instructed to disable the job when this triggers.

**Cron job:** `4c34a45e15b7` — `weekly_snapshot.py`, cron `58 23 * * 0`, delivers to Daniel's DM.

## Telegram Formatting

- No markdown tables — use bullet lists
- Bold with `**text**`
- Emoji classifications: 🐋 Whale, 🐬 Dolphin, 🐟 Fish
- Bot username for DMs: **@DBOT_DC_BOT** (Hermes bot, admin in OMNOM group with pin/delete rights)
- Community update pinned: msg_id=114512 in @omnomtoken_dc (Jun 28, 2026)

## Related Files

- Skill: `~/.hermes/skills/blockchain/omnom-wallet-lookup/`
- RPC scripts: `~/.hermes/skills/dogechain-rpc/scripts/`
- Snapshot data: `~/Documents/DBOT-Vault-Final/03-Research/Dogechain/omnom-snapshot/`
- Weekly snapshots: `~/Documents/DBOT-Vault-Final/03-Research/Dogechain/omnom-snapshot/weekly/`
- OMNOM knowledgebase: `~/Documents/OMNOM BOT 3/knowledgebase/`
