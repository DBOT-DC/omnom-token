#!/bin/bash
# OMNOM Wallet Lookup — Ever-Held Mode
# Checks master list (union of ALL snapshots)
# Shows max balance ever held + whether they currently still hold

WALLET="$1"
EVER_HELD_CSV="/Users/penny/.openclaw-telegram/workspace/omnom-snapshot/omnom-snapshot-ever-held.csv"
LATEST_CSV="/Users/penny/.openclaw-telegram/workspace/omnom-snapshot/omnom-snapshot-latest.csv"
DECIMALS=18

if [[ ! "$WALLET" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
    echo "INVALID"
    exit 1
fi

WALLET_LOWER=$(echo "$WALLET" | tr '[:upper:]' '[:lower:]')

# Check ever-held master list (tab-delimited)
RESULT=$(awk -F'\t' -v addr="$WALLET_LOWER" '
    NR > 1 && $2 == addr {
        printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s", $1, $2, $3, $4, $5, $6, $7, $8
        exit 0
    }
' "$EVER_HELD_CSV")

if [ -n "$RESULT" ]; then
    RANK=$(echo "$RESULT" | cut -f1)
    BAL_RAW=$(echo "$RESULT" | cut -f3)
    PCT=$(echo "$RESULT" | cut -f4)
    BEST_RANK=$(echo "$RESULT" | cut -f5)
    SNAP_COUNT=$(echo "$RESULT" | cut -f6)
    SNAPSHOTS=$(echo "$RESULT" | cut -f7)
    FIRST_SEEN=$(echo "$RESULT" | cut -f8)

    # Format balance
    BAL_FMT=$(python3 -c "print(f'{float(\"$BAL_RAW\") / 10**$DECIMALS:,.2f}')")

    # Determine class
    PCT_NUM=$(echo "$PCT" | awk '{printf "%.4f", $1}')
    if (( $(echo "$PCT_NUM >= 1.0" | bc -l) )); then
        CLASS="🐋 Whale"
    elif (( $(echo "$PCT_NUM >= 0.01" | bc -l) )); then
        CLASS="🐬 Dolphin"
    else
        CLASS="🐟 Fish"
    fi

    # Check if currently holds
    STILL_HOLDS="no"
    if [ -f "$LATEST_CSV" ]; then
        LATEST_CHECK=$(awk -F',' -v addr="$WALLET_LOWER" '
            NR > 1 && tolower($2) == addr { print "yes"; exit 0 }
        ' "$LATEST_CSV")
        [ "$LATEST_CHECK" = "yes" ] && STILL_HOLDS="yes"
    fi

    echo "STATUS:EVER_HELD"
    echo "RANK:$RANK"
    echo "BEST_RANK:$BEST_RANK"
    echo "BALANCE:$BAL_FMT"
    echo "PERCENTAGE:$PCT"
    echo "CLASS:$CLASS"
    echo "SNAPSHOTS:$SNAP_COUNT ($SNAPSHOTS)"
    echo "FIRST_SEEN:$FIRST_SEEN"
    echo "CURRENTLY_HOLDS:$STILL_HOLDS"
    exit 0
fi

echo "NOT_FOUND"
exit 0
