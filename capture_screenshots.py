"""
Screenshot Automation for IEEE Report
=====================================
Tự động lấy screenshot từ Dashboard Churn Prediction
Các state cần capture:
1. Overview Dashboard (Analytics)
2. Model Results (Accuracy 93.9%)
3. Prediction Demo — High Risk Customer (Rating 1-2 sao)
4. Prediction Demo — Safe Customer (Rating 4-5 sao)

Yêu cầu: Cài đặt Playwright hoặc Selenium
  pip install playwright
  playwright install
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
import sys

# Try Playwright first (recommended for modern development)
try:
    from playwright.async_api import async_playwright
    USE_PLAYWRIGHT = True
except ImportError:
    print("⚠️ Playwright not installed. Using Selenium instead...")
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        USE_PLAYWRIGHT = False
    except ImportError:
        print("❌ Neither Playwright nor Selenium installed!")
        print("Install with: pip install playwright")
        sys.exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

DASHBOARD_URL = "http://localhost:8000/dashboard"  # Update if running on different port
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots_for_report"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Viewport size for 16:9 ratio (standard projector)
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080

SCENARIOS = {
    "01_overview_dashboard": {
        "name": "📊 Analytics Dashboard Overview",
        "description": "Dashboard tổng quan với tất cả 4 KPI + biểu đồ",
        "actions": [
            ("wait_for_load", 2),  # Wait 2 seconds for charts to render
        ]
    },
    "02_model_results": {
        "name": "📈 Model Results (93.9% Accuracy)",
        "description": "Tab kết quả mô hình với Accuracy, Precision, Recall, F1",
        "actions": [
            ("click_tab", "📌"),  # Click to Model Results tab
            ("wait_for_load", 2),
        ]
    },
    "03_customer_churn_high_risk": {
        "name": "⚠️ High Risk Customer Prediction (Rating 1-2⭐)",
        "description": "Dự báo khách hàng rủi ro cao (sẽ Churn)",
        "actions": [
            ("click_tab", "🤖"),  # Click to Prediction tab
            ("wait_for_load", 1),
            ("fill_form", {
                "rating": 2,
                "balance": 50000,
                "age": 45,
                "credit_score": 620,
                "tenure": 2,
                "products": 1,
                "active_member": False,
                "credit_card": False
            }),
            ("click_button", "🚀 Dự báo"),
            ("wait_for_result", 1),
        ]
    },
    "04_customer_stay_safe": {
        "name": "✅ Safe Customer Prediction (Rating 4-5⭐)",
        "description": "Dự báo khách hàng an toàn (sẽ Stayed)",
        "actions": [
            ("click_tab", "🤖"),  # Prediction tab
            ("wait_for_load", 1),
            ("fill_form", {
                "rating": 5,
                "balance": 200000,
                "age": 35,
                "credit_score": 750,
                "tenure": 8,
                "products": 3,
                "active_member": True,
                "credit_card": True
            }),
            ("click_button", "🚀 Dự báo"),
            ("wait_for_result", 1),
        ]
    },
    "05_feature_importance": {
        "name": "🔍 Feature Importance Insights",
        "description": "Độ quan trọng của các features (Rating: 88%)",
        "actions": [
            ("scroll_to", "Feature Importance"),
            ("wait_for_load", 1),
        ]
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# PLAYWRIGHT IMPLEMENTATION
# ══════════════════════════════════════════════════════════════════════════════

async def run_with_playwright():
    """Capture screenshots using Playwright"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False to see what's happening
        context = await browser.new_context(viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT})
        page = await context.new_page()
        
        print(f"\n🌐 Navigating to {DASHBOARD_URL}...")
        await page.goto(DASHBOARD_URL, wait_until="networkidle")
        await page.wait_for_load_state("domcontentloaded")
        
        for scenario_id, scenario in SCENARIOS.items():
            print(f"\n📸 Capturing: {scenario['name']}")
            print(f"   {scenario['description']}")
            
            # Execute actions for this scenario
            for action_type, *args in scenario["actions"]:
                if action_type == "wait_for_load":
                    await asyncio.sleep(args[0])
                    
                elif action_type == "click_tab":
                    tab_text = args[0]
                    try:
                        await page.click(f"text={tab_text}", timeout=5000)
                        await asyncio.sleep(1)
                    except Exception as e:
                        print(f"   ⚠️ Could not click tab '{tab_text}': {e}")
                    
                elif action_type == "fill_form":
                    form_data = args[0]
                    # Map form fields to selectors
                    selectors = {
                        "rating": "input[type='number'][placeholder*='Rating']",
                        "balance": "input[type='number'][placeholder*='Balance']",
                        "age": "input[type='number'][placeholder*='Age']",
                        "credit_score": "input[type='number'][placeholder*='Credit']",
                    }
                    for field, value in form_data.items():
                        if field in selectors:
                            try:
                                await page.fill(selectors[field], str(value))
                            except:
                                pass
                    
                elif action_type == "click_button":
                    button_text = args[0]
                    try:
                        await page.click(f"text={button_text}", timeout=5000)
                        await asyncio.sleep(1)
                    except Exception as e:
                        print(f"   ⚠️ Could not click button '{button_text}': {e}")
                    
                elif action_type == "wait_for_result":
                    await asyncio.sleep(args[0])
                    
                elif action_type == "scroll_to":
                    text = args[0]
                    try:
                        await page.locator(f"text={text}").scroll_into_view_if_needed()
                        await asyncio.sleep(1)
                    except:
                        pass
            
            # Take screenshot
            filename = f"{scenario_id}_{datetime.now().strftime('%H%M%S')}.png"
            filepath = SCREENSHOTS_DIR / filename
            await page.screenshot(path=str(filepath), full_page=False)
            print(f"   ✅ Saved: {filepath}")
        
        await browser.close()
        print(f"\n✅ All screenshots saved to: {SCREENSHOTS_DIR}")

# ══════════════════════════════════════════════════════════════════════════════
# SELENIUM IMPLEMENTATION (FALLBACK)
# ══════════════════════════════════════════════════════════════════════════════

def run_with_selenium():
    """Capture screenshots using Selenium (fallback)"""
    print("⚠️ Using Selenium (Playwright recommended for better performance)")
    
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Comment out to see browser
    options.add_argument(f"--window-size={VIEWPORT_WIDTH},{VIEWPORT_HEIGHT}")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(DASHBOARD_URL)
        
        for scenario_id, scenario in SCENARIOS.items():
            print(f"\n📸 Capturing: {scenario['name']}")
            
            for action_type, *args in scenario["actions"]:
                if action_type == "wait_for_load":
                    asyncio.run(asyncio.sleep(args[0]))
                    
                elif action_type == "click_button":
                    button_text = args[0]
                    try:
                        buttons = driver.find_elements(By.XPATH, f"//*[contains(text(), '{button_text}')]")
                        if buttons:
                            buttons[0].click()
                    except:
                        pass
            
            # Save screenshot
            filename = f"{scenario_id}.png"
            filepath = SCREENSHOTS_DIR / filename
            driver.save_screenshot(str(filepath))
            print(f"   ✅ Saved: {filepath}")
    
    finally:
        driver.quit()
        print(f"\n✅ All screenshots saved to: {SCREENSHOTS_DIR}")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("  📸 SCREENSHOT AUTOMATION FOR IEEE REPORT")
    print("=" * 80)
    print(f"\n📍 Dashboard URL: {DASHBOARD_URL}")
    print(f"📁 Output Dir: {SCREENSHOTS_DIR}")
    print(f"🖥️  Resolution: {VIEWPORT_WIDTH}×{VIEWPORT_HEIGHT}")
    print(f"\n📋 Scenarios to capture:")
    for sid, s in SCENARIOS.items():
        print(f"   • {sid}: {s['name']}")
    
    print("\n⏳ Starting capture (browser will open automatically)...")
    print("   [Tip] Do NOT close the browser — it will auto-close after screenshots\n")
    
    if USE_PLAYWRIGHT:
        asyncio.run(run_with_playwright())
    else:
        run_with_selenium()
