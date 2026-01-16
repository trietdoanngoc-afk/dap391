# Bank Review Analysis Project

A data collection and analysis project for Vietnamese bank app reviews.

## 📁 Project Structure

```
proj/
├── config.py              # Central configuration (bank lists, app IDs, settings)
├── main.py                # Main entry point - run all crawlers
│
├── crawlers/              # Data collection modules
│   ├── __init__.py
│   ├── applestore.py      # Apple App Store crawler
│   ├── googleplay.py      # Google Play Store crawler
│   └── facebook.py        # Facebook review generator (synthetic)
│
├── utils/                 # Shared utilities
│   ├── __init__.py
│   ├── features.py        # Customer feature generation
│   └── generators.py      # Synthetic data generators
│
├── data/
│   ├── raw/               # Raw data from crawlers
│   │   ├── reviews_appstore.csv
│   │   ├── reviews_googleplay.csv
│   │   └── reviews_facebook.csv
│   └── processed/         # Processed/merged data
│       └── merged_all_reviews.csv
│
└── crawl/                 # [DEPRECATED] Old crawler scripts
```

## 🚀 Usage

### Run All Crawlers
```bash
python main.py
```

### Run Individual Crawlers
```bash
python crawlers/applestore.py
python crawlers/googleplay.py
python crawlers/facebook.py
```

## 📊 Data Schema

| Column | Description |
|--------|-------------|
| `review_id` | Unique review identifier |
| `date` | Review date (YYYY-MM-DD) |
| `bank_name` | Name of the bank |
| `rating` | Rating (1-5) |
| `churn` | Churn indicator (1 if rating ≤ 2) |
| `platform` | Source platform |
| `sex` | Customer gender |
| `age` | Customer age |
| `tenure` | Years as customer |
| `credit_score` | Credit score (300-850) |
| `balance` | Account balance (VND) |
| `products_number` | Number of products |
| `credit_card` | Has credit card (0/1) |
| `active_member` | Active member status (0/1) |
| `data_source` | "real" or "synthetic" |

## 🏦 Banks Covered

- **Big 4**: Vietcombank, BIDV, VietinBank, Agribank
- **Private Banks**: Techcombank, MB Bank, TPBank, VPBank, SHB, HDBank, OCB, ACB, Sacombank, etc.
- **Foreign Banks**: HSBC Vietnam, Standard Chartered VN, Shinhan Bank VN, UOB VN, etc.

## 📦 Dependencies

```bash
pip install pandas requests google-play-scraper
```
