import json

try:
    with open('dashboard/data.json', 'r') as f:
        data = json.load(f)
    print(f"✓ Valid JSON")
    print(f"Keys: {list(data.keys())}")
    print(f"Banks: {len(data.get('banks', []))}")
    print(f"Aggregated records: {len(data.get('agg', []))}")
    print(f"KPI keys: {list(data.get('kpi', {}).keys())}")
except Exception as e:
    print(f"✗ Error: {e}")
