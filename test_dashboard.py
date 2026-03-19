#!/usr/bin/env python
"""Test script for dashboard functionality"""

import requests
import json
import sys

print("=" * 60)
print("TESTING DASHBOARD FUNCTIONALITY")
print("=" * 60)

# Test 1: API Availability
print("\n[TEST 1] API Availability")
print("-" * 40)
try:
    payload = {
        'bank_name': 0,
        'rating': 3,
        'sex': 1,
        'age': 30,
        'tenure': 5,
        'credit_score': 650,
        'balance': 5000000000,
        'products_number': 2,
        'credit_card': 1,
        'active_member': 1,
        'platform_app_store': 1,
        'platform_facebook': 0,
        'platform_google_play': 0
    }
    response = requests.post('http://localhost:8000/predict', json=payload, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        print("✓ API Test Passed")
        print(f"  Status Code: {response.status_code}")
        print(f"  Churn Probability: {data.get('probability_churn', 'N/A'):.2%}")
        print(f"  Stay Probability: {data.get('probability_stay', 'N/A'):.2%}")
        print(f"  Prediction: {'CHURN' if data.get('churn') == 1 else 'STAY'}")
    else:
        print(f"✗ API returned non-200 status: {response.status_code}")
        
except Exception as e:
    print(f"✗ API Test Failed: {str(e)}")
    print("  Make sure API is running: python api.py")

# Test 2: Data JSON Structure
print("\n[TEST 2] Data JSON Structure")
print("-" * 40)
try:
    with open('dashboard/data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    required_keys = ['kpi', 'banks', 'agg', 'platforms']
    if all(key in data for key in required_keys):
        print("✓ Data JSON Structure Valid")
        print(f"  - Banks: {len(data['banks'])}")
        print(f"  - Platforms: {len(data['platforms'])}")
        print(f"  - Aggregation groups: {len(data['agg'])}")
        print(f"  - Total customers: {data['kpi']['total_customers']:,}")
        print(f"  - Churned customers: {data['kpi']['total_churned']}")
        print(f"  - Churn rate: {data['kpi']['churn_rate']:.2%}")
    else:
        print("✗ Data JSON missing required keys")
        print(f"  Found: {list(data.keys())}")
        
except FileNotFoundError:
    print("✗ dashboard/data.json not found")
    print("  Run: python export_dashboard_data.py")
except json.JSONDecodeError:
    print("✗ data.json is not valid JSON")
except Exception as e:
    print(f"✗ Data JSON Test Failed: {str(e)}")

# Test 3: Bank List (35 banks required)
print("\n[TEST 3] Bank List Verification")
print("-" * 40)
try:
    with open('dashboard/data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    banks = data.get('banks', [])
    if len(banks) == 35:
        print(f"✓ All 35 Banks Found")
        print(f"  First 5: {', '.join(banks[:5])}")
        print(f"  Last 5: {', '.join(banks[-5:])}")
    else:
        print(f"✗ Wrong number of banks: {len(banks)} (expected 35)")
        
except Exception as e:
    print(f"✗ Bank List Test Failed: {str(e)}")

# Test 4: API with all 35 banks
print("\n[TEST 4] API Testing with Bank Variations")
print("-" * 40)
try:
    banks_to_test = [0, 17, 34]  # First, middle, last bank
    base_payload = {
        'rating': 2,
        'sex': 1,
        'age': 45,
        'tenure': 3,
        'credit_score': 500,
        'balance': 1000000000,
        'products_number': 1,
        'credit_card': 0,
        'active_member': 0,
        'platform_app_store': 1,
        'platform_facebook': 0,
        'platform_google_play': 0
    }
    
    with open('dashboard/data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    banks = data.get('banks', [])
    success_count = 0
    
    for bank_idx in banks_to_test:
        if bank_idx < len(banks):
            payload = base_payload.copy()
            payload['bank_name'] = bank_idx
            response = requests.post('http://localhost:8000/predict', json=payload, timeout=5)
            if response.status_code == 200:
                success_count += 1
                pred = response.json()
                print(f"  Bank {bank_idx} ({banks[bank_idx]}): {pred.get('churn', 0) and 'RISK' or 'SAFE'}")
    
    if success_count == len(banks_to_test):
        print(f"✓ All {len(banks_to_test)} test cases passed")
    else:
        print(f"✗ Only {success_count}/{len(banks_to_test)} test cases passed")
        
except Exception as e:
    print(f"✗ API Bank Test Failed: {str(e)}")

print("\n" + "=" * 60)
print("TESTING COMPLETE")
print("=" * 60)
