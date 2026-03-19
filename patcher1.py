import re

with open("dashboard/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. HTML Replacement
html_target = r"<!-- PAGE 1: ANALYTICS DASHBOARD.*?(?=<!-- PAGE 2: RESULTS -->)"
html_replacement = """<!-- PAGE 1: ANALYTICS DASHBOARD -->
        <div id="tab-analytics" class="page-tab active">
            <!-- Header -->
            <header class="header">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;">
                    <div>
                        <h1>📊 SENTIFY ULTIMATE <span>DASHBOARD</span></h1>
                        <p style="color: var(--text-secondary); margin-top: 8px; font-size: 14px;">Real-time Bank Customer Churn Analytics</p>
                    </div>
                    <div style="text-align: right;">
                        <span id="dataInfo" style="background: rgba(16, 185, 129, 0.1); color: var(--accent-green); padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: 500; border: 1px solid rgba(16, 185, 129, 0.2);">Data Loading...</span>
                    </div>
                </div>

                <!-- Global Filters -->
                <div class="filters">
                    <div class="filter-group">
                        <label>Ngân hàng</label>
                        <select id="filterBank"><option value="all">Tất cả ngân hàng</option></select>
                    </div>
                    <div class="filter-group">
                        <label>Nền tảng</label>
                        <select id="filterPlatform"><option value="all">Tất cả nền tảng</option></select>
                    </div>
                    <div class="filter-group">
                        <label>Phân loại KH</label>
                        <select id="filterVIP">
                            <option value="all">Tất cả</option>
                            <option value="1">VIP (Balance > 1 Tỷ)</option>
                            <option value="0">Thường</option>
                        </select>
                    </div>
                    <div class="filter-group" style="justify-content: flex-end;">
                        <button onclick="resetFilters()" style="margin-top:20px; padding: 10px 20px; background: rgba(255,255,255,0.05); color: white; border: 1px solid var(--border); border-radius: 8px; cursor: pointer; transition: all 0.2s;">Reset</button>
                    </div>
                </div>
            </header>

            <!-- KPI Cards -->
            <div class="kpi-grid">
                <div class="kpi-card" style="border-top: 3px solid var(--accent-blue)">
                    <div class="kpi-title">TỔNG KHÁCH HÀNG</div>
                    <div class="kpi-value" id="kpiTotal">0</div>
                    <div class="kpi-sub" id="kpiTotalSub"></div>
                </div>
                <div class="kpi-card" style="border-top: 3px solid var(--accent-red)">
                    <div class="kpi-title">TỈ LỆ RỜI BỎ (CHURN RATE)</div>
                    <div class="kpi-value" id="kpiChurnRate" style="color: var(--accent-red)">0%</div>
                    <div class="kpi-sub" id="kpiChurnSub"></div>
                </div>
                <div class="kpi-card" style="border-top: 3px solid var(--accent-orange)">
                    <div class="kpi-title">RATING TRUNG BÌNH</div>
                    <div class="kpi-value" id="kpiAvgRating" style="color: var(--accent-orange)">0.0</div>
                    <div class="kpi-sub" id="kpiRatingSub"></div>
                </div>
                <div class="kpi-card" style="border-top: 3px solid var(--text-muted)">
                    <div class="kpi-title">KHÁCH ĐÃ RỜI ĐI</div>
                    <div class="kpi-value" id="kpiChurned">0</div>
                    <div class="kpi-sub" id="kpiChurnedSub"></div>
                </div>
            </div>

            <!-- AI Warnings -->
            <div id="alertsSection" style="margin-bottom: 24px; display: flex; flex-direction: column; gap: 12px;"></div>

            <!-- Charts Grid 1 -->
            <div class="charts-grid-3">
                <div class="chart-card">
                    <div class="chart-header">
                        <h3 class="chart-title">Churn Rate theo Rating</h3>
                    </div>
                    <div class="chart-container"><canvas id="chartRating"></canvas></div>
                </div>
                <div class="chart-card" style="grid-column: span 2">
                    <div class="chart-header">
                        <h3 class="chart-title">Top Ngân hàng có Churn Rate cao nhất</h3>
                    </div>
                    <div class="chart-container"><canvas id="chartBank"></canvas></div>
                </div>
            </div>

            <!-- Charts Grid 2 -->
            <div class="charts-grid-2">
                <div class="chart-card">
                    <div class="chart-header">
                        <h3 class="chart-title">Xu hướng Churn Rate theo Tháng</h3>
                    </div>
                    <div class="chart-container"><canvas id="chartTrend"></canvas></div>
                </div>
                <div class="chart-card">
                    <div class="chart-header">
                        <h3 class="chart-title">Thời gian gắn bó (Tenure) vs Rating</h3>
                        <span class="chart-subtitle">Trung bình số năm gắn bó trước khi rời đi</span>
                    </div>
                    <div class="chart-container"><canvas id="chartTenure"></canvas></div>
                </div>
            </div>

            <!-- Advance Charts -->
            <div class="charts-grid-2">
                <div class="chart-card">
                    <div class="chart-header">
                        <h3 class="chart-title">Tài sản đang Rủi Ro (Value at Risk)</h3>
                        <span class="chart-subtitle">Tổng số dư của KH đã rời đi theo Ngân hàng (Tỷ VNĐ)</span>
                    </div>
                    <div class="chart-container"><canvas id="chartVaR"></canvas></div>
                </div>
                <div class="chart-card">
                    <div class="chart-header">
                        <h3 class="chart-title">Phân rã KH VIP vs Thường</h3>
                    </div>
                    <div class="chart-container" style="height: 250px"><canvas id="chartVip"></canvas></div>
                </div>
            </div>

            <!-- TABLE SECTION -->
            <div class="table-container">
                <div class="table-header">
                    <div class="table-tabs">
                        <button class="tab-btn active" onclick="switchTab('at-risk')">
                            ⚠️ Nhóm Khẩn Cấp (<span id="tabAtRiskCount">0</span>)
                        </button>
                        <button class="tab-btn" onclick="switchTab('near-risk')">
                            ⚡ Nhóm Cận Biên (<span id="tabNearRiskCount">0</span>)
                        </button>
                    </div>
                    <button class="export-btn" onclick="exportCSV()">📥 Xuất CSV</button>
                </div>

                <div class="table-controls">
                    <div>
                        <h3 id="tableTitle" style="font-size: 16px; margin-bottom: 4px;"></h3>
                        <p id="tableCount" style="color: var(--text-muted); font-size: 13px;"></p>
                    </div>

                    <div style="display: flex; gap: 12px; align-items: center;">
                        <input type="text" id="tableSearch" class="search-input" placeholder="🔍 Tìm tên ngân hàng..." onkeyup="renderTable()">
                        <button onclick="toggleSort()" style="padding: 8px 16px; border-radius: 8px; border: 1px solid var(--border); background: var(--bg-hover); color: white; cursor: pointer;">
                            <span id="sortLabel">Balance ↓</span> <span id="sortIcon">⬇️</span>
                        </button>
                    </div>
                </div>

                <div id="prioritySection" class="priority-filters">
                    <div class="priority-card high active" onclick="filterPriority('high')">
                        <div style="font-size: 12px; opacity: 0.8">Ưu tiên Cao (VIP)</div>
                        <div style="font-size: 18px; font-weight: bold" id="prioHighCount">0</div>
                    </div>
                    <div class="priority-card medium active" onclick="filterPriority('medium')">
                        <div style="font-size: 12px; opacity: 0.8">Ưu tiên Trung bình</div>
                        <div style="font-size: 18px; font-weight: bold" id="prioMedCount">0</div>
                    </div>
                    <div class="priority-card low active" onclick="filterPriority('low')">
                        <div style="font-size: 12px; opacity: 0.8">Ưu tiên Thấp</div>
                        <div style="font-size: 18px; font-weight: bold" id="prioLowCount">0</div>
                    </div>
                </div>

                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr id="tableHead"></tr>
                        </thead>
                        <tbody id="tableBody"></tbody>
                    </table>
                </div>
            </div> <!-- END TABLE SECTION -->
        </div>

        """
if html_target != "":
    content = re.sub(html_target, html_replacement, content, flags=re.DOTALL)

with open("dashboard/index.html", "w", encoding="utf-8") as f:
    f.write(content)
print("HTML Target applied")
