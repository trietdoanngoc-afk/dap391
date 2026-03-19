#!/usr/bin/env python3
"""
SIMPLE SCREENSHOT CAPTURE — Manual Browser Method
==================================================
Cách đơn giản nhất: Dùng trình duyệt + print PDF → PNG

Bước 1: Mở Dashboard trong Chrome
Bước 2: Chạy script này → sẽ in hướng dẫn bấm screenshot từng phần
Bước 3: Copy các ảnh vào Report
"""

from pathlib import Path
import json
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════

SCREENSHOTS_DIR = Path(__file__).parent / "screenshots_for_report"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

MANUAL_STEPS = [
    {
        "step": 1,
        "name": "📊 Dashboard Overview",
        "instructions": [
            "1. Mở Chrome: http://localhost:8000/dashboard",
            "2. Chờ tất cả biểu đồ load xong (1-2 giây)",
            "3. Bấm Print (Ctrl+P) → Save as PDF → Chọn vị trí",
            "4. Rename: 01_overview_dashboard.pdf",
        ],
        "tips": "Nên sử dụng 100% zoom để text rõ ràng"
    },
    {
        "step": 2,
        "name": "📈 Model Results (93.9%)",
        "instructions": [
            "1. Bấm tab 'Kết quả Mô hình (Results)' - biểu tượng 📈",
            "2. Scroll xuống xem: Accuracy 93.9%, Precision 0.95, Recall 0.89, F1 0.92",
            "3. Bấm Print → Save PDF → Rename: 02_model_results.pdf",
        ],
        "tips": "Chính tab này sẽ chứng minh 93.9% accuracy"
    },
    {
        "step": 3,
        "name": "⚠️ High Risk Customer (Churn)",
        "instructions": [
            "1. Bấm tab 'Dự báo (Predict)' 🤖",
            "2. Điền thông tin khách hàng rủi ro:",
            "   - Rating: 1 hoặc 2",
            "   - Balance: 50,000",
            "   - Age: 45",
            "   - Credit Score: 620",
            "   - Tenure: 2 năm",
            "   - Products: 1",
            "   - Active Member: ❌ (unchecked)",
            "   - Credit Card: ❌ (unchecked)",
            "3. Bấm 🚀 Dự báo",
            "4. Print → PDF → Rename: 03_high_risk_churn.pdf",
        ],
        "tips": "Model sẽ dự báo CHURN với confidence cao (>80%)"
    },
    {
        "step": 4,
        "name": "✅ Safe Customer (Stay)",
        "instructions": [
            "1. Trong tab Predict, Reset form (hoặc clear input)",
            "2. Điền thông tin khách hàng an toàn:",
            "   - Rating: 5",
            "   - Balance: 200,000",
            "   - Age: 35", 
            "   - Credit Score: 750",
            "   - Tenure: 8 năm",
            "   - Products: 3",
            "   - Active Member: ✅ (checked)",
            "   - Credit Card: ✅ (checked)",
            "3. Bấm 🚀 Dự báo",
            "4. Print → PDF → Rename: 04_safe_stay.pdf",
        ],
        "tips": "Model sẽ dự báo STAY (high confidence)"
    },
    {
        "step": 5,
        "name": "🔍 Feature Importance",
        "instructions": [
            "1. Quay lại tab 'Kết quả Mô hình (Results)'",
            "2. Scroll xuống phần 'Feature Importance'",
            "3. Thấy: Rating (88%), Balance/Product (5-7%), Age, Credit Score, ...",
            "4. Print → PDF → Rename: 05_feature_importance.pdf",
        ],
        "tips": "Cho thấy Rating là #1 nhưng không phải duy nhất"
    }
]

# ═══════════════════════════════════════════════════════════════════════════════
# Main

def print_guide():
    print("\n" + "="*80)
    print("  📸 MANUAL SCREENSHOT GUIDE FOR IEEE REPORT")
    print("="*80)
    print(f"\n📁 Save all screenshots to: {SCREENSHOTS_DIR}\n")
    
    for step_info in MANUAL_STEPS:
        print(f"\n{'─'*80}")
        print(f"STEP {step_info['step']}: {step_info['name']}")
        print(f"{'─'*80}")
        
        for instruction in step_info["instructions"]:
            print(f"   {instruction}")
        
        print(f"\n💡 TIP: {step_info['tips']}")
    
    print(f"\n{'─'*80}")
    print(f"\n✅ HOÀN THÀNH!\n")
    print(f"📋 Checklist:")
    for i, step in enumerate(MANUAL_STEPS, 1):
        print(f"   ☐ {i}. {step['name']} (file: {i:02d}_*.pdf)")
    
    print(f"\n💾 Tất cả file sẽ lưu tại: {SCREENSHOTS_DIR}")
    print(f"\n📝 Sau khi có tất cả screenshot:")
    print(f"   1. Mở file PDF → Export as PNG (300 DPI nếu có)")
    print(f"   2. Hoặc dùng Snipping Tool: Win+Shift+S")
    print(f"   3. Copy vào Report → Thêm captions")
    print(f"\n   Ví dụ caption:")
    print(f'   "Fig. 3: Model Accuracy (93.9%) on Test Set — achieved through')
    print(f'    realistic noise injection (5-7% record flipping)"')
    print(f"\n{'='*80}\n")

# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print_guide()
    
    # Tạo JSON checklist để track
    checklist = {
        "generated_at": datetime.now().isoformat(),
        "total_screenshots": len(MANUAL_STEPS),
        "screenshots": [
            {
                "step": s["step"],
                "name": s["name"],
                "filename": f"{s['step']:02d}_{s['name'].lower().replace(' ', '_').replace('/', '_')}.pdf"
            }
            for s in MANUAL_STEPS
        ]
    }
    
    checklist_file = SCREENSHOTS_DIR / "checklist.json"
    with open(checklist_file, "w", encoding="utf-8") as f:
        json.dump(checklist, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Checklist saved to: {checklist_file}")
    print(f"\nBây giờ hãy bắt đầu lấy screenshot theo hướng dẫn trên! 🎬")
