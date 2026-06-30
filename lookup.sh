#!/bin/bash
# OMNOM Wallet Lookup Script
# Usage: lookup.sh <wallet_address>
# Returns: rank, balance, percentage, holder class from snapshot

WALLET="$1"
SNAPSHOT_CSV="/Users/penny/.openclaw-telegram/workspace/omnom-snapshot/omnom-snapshot-pre-announcement.csv"

# Validate input
if [[ ! "$WALLET" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
    echo "INVALID: Not a valid Ethereum-style address"
    exit 1
fi

# Normalize to lowercase for matching
WALLET_LOWER=$(echo "$WALLET" | tr '[:upper:]' '[:lower:]')

# Look up in CSV (case-insensitive)
# CSV format: rank,address,balance_raw,balance_formatted,percentage_of_supply
RESULT=$(awk -F',' -v addr="$WALLET_LOWER" '
    NR > 1 && tolower($2) == addr {
        printf "%s,%s,%s,%s", $1, $2, $4, $5
        exit 0
    }
' "$SNAPSHOT_CSV")

if [ -z "$RESULT" ]; then
    echo "NOT_FOUND"
    exit 0
fi

# Parse fields
RANK=$(echo "$RESULT" | cut -d',' -f1)
BALANCE=$(echo "$RESULT" | cut -d',' -f3)
PCT=$(echo "$RESULT" | cut -d',' -f4)

# Determine holder class
PCT_NUM=$(echo "$PCT" | awk '{printf "%.4f", $1}')
if (( $(echo "$PCT_NUM >= 1.0" | bc -l) )); then
    CLASS="🐋 Whale"
elif (( $(echo "$PCT_NUM >= 0.01" | bc -l) )); then
    CLASS="🐬 Dolphin"  
else
    CLASS="🐟 Fish"
fi

echo "RANK:$RANK"
echo "BALANCE:$BALANCE"
echo "PERCENTAGE:$PCT"
echo "CLASS:$CLASS"
