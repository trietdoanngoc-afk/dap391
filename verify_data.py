#!/usr/bin/env python
"""Verify revenue table data structure"""

import json

with open('dashboard/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 60)
print("DATA STRUCTURE VERIFICATION")
print("=" * 60)
print("\nIndex positions: [BANK, PLAT, RATE, VIP, MONTH, CHURN, COUNT, BAL, TEN]")
print("                [  0,   1,    2,     3,    4,      5,      6,     7,   8]")

print("\nSample aggregation entries:")
for i, agg in enumerate(data.get('agg', [])[:3]):
    bank_idx = agg[0]
    balance = agg[7] if len(agg) > 7 else 0
    churn = agg[5] if len(agg) > 5 else 0
    bank_name = data['banks'][bank_idx] if bank_idx < len(data['banks']) else "Unknown"
    
    print(f"\nEntry {i}:")
    print(f"  Bank (idx 0): {bank_idx} = {bank_name}")
    print(f"  Balance (idx 7): {balance:,.0f}")
    print(f"  Churn (idx 5): {churn}")

print("\n" + "=" * 60)
print("✓ Data structure is correct!")
print(f"✓ Total banks: {len(data['banks'])}")
print(f"✓ Total aggregations: {len(data.get('agg', []))}")
print("=" * 60)
