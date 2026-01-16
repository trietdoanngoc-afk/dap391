"""
Configuration file for Bank Review Analysis Project.
Contains all bank lists, app IDs, and shared constants.
"""

# =============================================================================
# BANK LISTS
# =============================================================================

# All banks covered in the project
BANKS_ALL = [
    # 🟡 Big 4 State-owned banks
    "Vietcombank",
    "BIDV", 
    "VietinBank",
    "Agribank",

    # 🔵 Private banks
    "Techcombank",
    "MB Bank",
    "TPBank",
    "VPBank",
    "SHB",
    "HDBank",
    "OCB",
    "ACB",
    "Sacombank",
    "Eximbank",
    "SeABank",
    "Bac A Bank",
    "LienVietPostBank",
    "Nam A Bank",
    "PVcomBank",
    "Kienlongbank",
    "ABBank",
    "NCB",

    # 🟣 Foreign banks
    "HSBC Vietnam",
    "Standard Chartered VN",
    "Shinhan Bank VN",
    "UOB VN",
    "OCBC VN",
    "Public Bank VN",
    "Hong Leong VN",
    "Indovina Bank",
    "Maybank VN",

    # 🟠 Others
    "VietABank",
    "Saigonbank",
    "VRB",
    "PG Bank"
]

# =============================================================================
# APP STORE IDS (iOS)
# =============================================================================

BANK_APPS_IOS = {
    # Big 4
    "Vietcombank": 561433133,
    "BIDV": 1061867449,
    "VietinBank": 689963454,
    "Agribank": 935944952,

    # Private banks
    "Techcombank": 1548623362,
    "MB Bank": 1205807363,
    "TPBank": 450464147,
    "VPBank": 1209349510,
    "SHB": 1661457183,
    "HDBank": 1461658565,
    "OCB": 6472261202,
    "ACB": 950141024,
    "Sacombank": 1436283663,
    "Eximbank": 1571427361,
    "SeABank": 846407152,
    "Bac A Bank": 1441408786,
    "LienVietPostBank": 1488794748,
    "Nam A Bank": 1456997296,
    "PVcomBank": 6467857410,
    "Kienlongbank": 1562823941,
    "ABBank": 6636532294,
    "NCB": 1435405040,

    # Foreign banks (None = no iOS app available)
    "HSBC Vietnam": 1472163155,
    "Standard Chartered VN": None,
    "Shinhan Bank VN": 1071033810,
    "UOB VN": 1174327324,
    "OCBC VN": None,
    "Public Bank VN": 1573736472,
    "Hong Leong VN": None,
    "Indovina Bank": 1096963960,
    "Maybank VN": None,

    # Others
    "VietABank": 6744814738,
    "Saigonbank": 1481832587,
    "VRB": None,
    "PG Bank": 1537765475
}

# =============================================================================
# GOOGLE PLAY IDS (Android)
# =============================================================================

BANK_APPS_GOOGLE = {
    "Vietcombank": "com.VCB",
    "BIDV": "com.bidv.smartbanking",
    "VietinBank": "com.vietinbank.ipay",
    "Agribank": "com.vnpay.Agribank3g",
    "Techcombank": "vn.com.techcombank.bb.app",
    "MB Bank": "com.mbmobile",
    "TPBank": "com.tpb.mb.smartbank",
    "VPBank": "com.vnpay.vpbankonline",
    "Sacombank": "com.sacombank.pay",
    "ACB": "com.acb.acbonline"
}

# =============================================================================
# DATA GENERATION SETTINGS
# =============================================================================

RATING_WEIGHTS = [12, 13, 25, 25, 25]  # Distribution for ratings 1-5
DUMMY_REVIEWS_PER_BANK = 500
CRAWL_REVIEWS_PER_BANK = 3000

# =============================================================================
# OUTPUT PATHS
# =============================================================================

OUTPUT_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

# Final column order for exported data
FINAL_COLUMNS = [
    "review_id",
    "date", 
    "bank_name",
    "rating",
    "churn",
    "platform",
    "sex",
    "age",
    "tenure",
    "credit_score",
    "balance",
    "products_number",
    "credit_card",
    "active_member",
    "data_source"
]
