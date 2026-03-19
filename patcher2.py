import re

with open("dashboard/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 2. JS Replacement
js_target = r"async function loadData\(\) \{.*?\}, 500\);\s*\}"
js_replacement = """async function loadData() {
            try {
                const res = await fetch('data.json');
                DATA = await res.json();
                document.getElementById('dataInfo').textContent =
                    `${DATA.kpi.total_customers.toLocaleString()} records | ${DATA.banks.length} banks | ${DATA.agg.length.toLocaleString()} groups`;
                populateFilters();
                initCharts();
                applyFilters();
                document.getElementById('loading').classList.add('hidden');
            } catch (e) {
                document.getElementById('loading').innerHTML =
                    `<div style="color:var(--accent-red);text-align:center">
        <p style="font-size:18px;margin-bottom:8px">❌ Lỗi tải dữ liệu</p>
        <p style="font-size:13px;color:var(--text-muted)">${e.message}</p>
        <p style="font-size:12px;color:var(--text-muted);margin-top:8px">
          Hãy chạy: python export_dashboard_data.py</p>
      </div>`;
            }
        }"""

if js_target != "":
    content = re.sub(js_target, js_replacement, content, flags=re.DOTALL)

with open("dashboard/index.html", "w", encoding="utf-8") as f:
    f.write(content)
print("JS Target applied")
