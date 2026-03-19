#!/usr/bin/env python
"""Simulate the revenue table calculation"""

import json

with open('dashboard/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Constants from JavaScript
I_BANK = 0
I_CHURN = 5
I_BAL = 7

# Simulate JavaScript calculation
revenue_by_bank = {}
for bank in data['banks']:
    idx = data['banks'].index(bank)
    revenue_by_bank[idx] = {'name': bank, 'churned': 0, 'balance': 0}

# Aggregate churned customer data
for agg in data['agg']:
    bank_idx = agg[I_BANK]
    churn_count = agg[I_CHURN]
    total_balance = float(agg[I_BAL]) if len(agg) > I_BAL else 0
    
    if bank_idx in revenue_by_bank:
        revenue_by_bank[bank_idx]['churned'] += 1 if churn_count > 0 else 0
        if churn_count > 0:
            revenue_by_bank[bank_idx]['balance'] += total_balance

# Sort and display
sorted_banks = sorted(
    [b for b in revenue_by_bank.values() if b['churned'] > 0],
    key=lambda x: x['balance'],
    reverse=True
)

print("=" * 70)
print("REVENUE LOSS PREDICTION TABLE (TEST CALCULATION)")
print("=" * 70)
print(f"{'Tên Ngân Hàng':<30} {'KH Rủi Ro':>15} {'Mất mát (Tỷ VNĐ)':>20}")
print("-" * 70)

for bank in sorted_banks[:10]:  # Top 10
    balance_in_billion = bank['balance'] / 1e9
    if balance_in_billion > 0:  # Only show non-zero
        print(f"{bank['name']:<30} {bank['churned']:>15} {balance_in_billion:>19.2f}")

print("-" * 70)
print(f"✓ Total banks with churn risk: {len(sorted_banks)}")
print(f"✓ Total revenue at risk: {sum(b['balance'] for b in sorted_banks) / 1e9:.2f} tỷ VNĐ")
print("=" * 70)
