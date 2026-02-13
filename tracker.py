import requests
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText

# ----------------------
# CONFIG
# ----------------------
HEADERS = {"User-Agent": "Mozilla/5.0"}
REGULAR_FILE = "data_regular.csv"
BSTOCK_FILE = "data_bstock.csv"

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")
STREAMLIT_URL = os.environ.get("APP_URL")
RECEIVER = "mitja.goja@gmail.com"

# ----------------------
# SCRAPER
# ----------------------
def scrape():
    """
    Scrape Thomann Squier Affinity Telecasters using the Solr API
    Detects Regular vs B-Stock via 'condition' field
    Returns: regular_df, bstock_df
    """
    api_url = "https://www.thomann.it/solrsearch/select"

    params = {
        "q": "Affinity",                   # search Affinity
        "fq": ["manufacturer:Squier", "category:GIEGTE"],  # filter manufacturer & guitar category
        "rows": 100,
        "wt": "json"
    }

    r = requests.get(api_url, params=params, headers=HEADERS)
    data = r.json()

    regular = []
    bstock = []

    for doc in data["response"]["docs"]:
        name = doc.get("title", "")
        price = doc.get("price")
        url = doc.get("url", "")
        condition = doc.get("condition", "new")

        if not name or not price or "Telecaster" not in name:
            continue

        try:
            price_value = float(price)
        except:
            continue

        if 180 <= price_value <= 250:
            entry = {"Name": name, "Price": price_value, "Link": "https://www.thomann.it/" + url}

            # Detect B-Stock via condition field
            if condition.lower() in ["b-stock", "b stock", "used"]:
                bstock.append(entry)
            else:
                regular.append(entry)

    # Sort by price ascending
    regular_df = pd.DataFrame(regular).sort_values("Price").reset_index(drop=True)
    bstock_df = pd.DataFrame(bstock).sort_values("Price").reset_index(drop=True)

    return regular_df, bstock_df

# ----------------------
# SAVE TO CSV
# ----------------------
def save(df, filename):
    df.to_csv(filename, index=False)

# ----------------------
# SEND EMAIL ALERT
# ----------------------
def send_email(reg_df, bst_df):
    if not EMAIL or not PASSWORD:
        print("Email not configured. Skipping email.")
        return

    body = f"""
Weekly Squier Affinity Telecaster Update

Regular models: {len(reg_df)}
B-Stock models: {len(bst_df)}

Check dashboard:
{STREAMLIT_URL}
"""

    msg = MIMEText(body)
    msg["Subject"] = "🎸 Weekly Squier Tracker"
    msg["From"] = EMAIL
    msg["To"] = RECEIVER

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)

    print("Email sent successfully!")

# ----------------------
# MAIN
# ----------------------
if __name__ == "__main__":
    regular_df, bstock_df = scrape()
    save(regular_df, REGULAR_FILE)
    save(bstock_df, BSTOCK_FILE)
    send_email(regular_df, bstock_df)
    print(f"Regular: {len(regular_df)}, B-Stock: {len(bstock_df)}")




