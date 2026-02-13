import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText

# =========================
# CONFIG
# =========================

URL = "https://www.thomann.it/cat_BF_squier.html?oa=pra&sp=solr_improved&category%5B%5D=GIEGTE&cme=true&manufacturer%5B%5D=Squier&bn=Squier&filter=true"
HEADERS = {"User-Agent": "Mozilla/5.0"}

REGULAR_FILE = "data_regular.csv"
BSTOCK_FILE = "data_bstock.csv"

EMAIL = st.secrets.get("EMAIL", "")
PASSWORD = st.secrets.get("PASSWORD", "")
RECEIVER = "mitja.goja@gmail.com"

# =========================
# SCRAPER
# =========================

def scrape_guitars():
    r = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    regular = []
    bstock = []

    for item in soup.select(".product"):
        title = item.select_one(".product__title")
        price = item.select_one(".price")

        if not title or not price:
            continue

        name = title.text.strip()
        price_text = price.text.strip().replace("€", "").replace(",", ".")
        
        try:
            value = float(price_text)
        except:
            continue

        if "Affinity" in name and "Tele" in name and 180 <= value <= 250:
            link = "https://www.thomann.it" + title["href"]

            entry = {
                "Name": name,
                "Price": value,
                "Link": link
            }

            if "B-Stock" in name or "B Stock" in name:
                bstock.append(entry)
            else:
                regular.append(entry)

    return pd.DataFrame(regular), pd.DataFrame(bstock)

# =========================
# PRICE COMPARISON
# =========================

def compare_prices(new_df, file_name):
    if not os.path.exists(file_name):
        new_df.to_csv(file_name, index=False)
        return new_df.assign(Drop=0)

    old_df = pd.read_csv(file_name)

    merged = new_df.merge(old_df, on="Name", how="left", suffixes=("", "_old"))
    merged["Drop"] = merged["Price_old"] - merged["Price"]
    merged["Drop"] = merged["Drop"].fillna(0)

    new_df.to_csv(file_name, index=False)

    return merged

# =========================
# EMAIL ALERT
# =========================

def send_email_alert(reg_df, bst_df):
    if not EMAIL or not PASSWORD:
        return

    drops_regular = reg_df[reg_df["Drop"] > 0]
    drops_bstock = bst_df[bst_df["Drop"] > 0]

    if drops_regular.empty and drops_bstock.empty:
        return

    body = "PRICE DROPS DETECTED:\n\n"

    if not drops_regular.empty:
        body += "REGULAR:\n"
        body += drops_regular.to_string(index=False)
        body += "\n\n"

    if not drops_bstock.empty:
        body += "B-STOCK:\n"
        body += drops_bstock.to_string(index=False)

    msg = MIMEText(body)
    msg["Subject"] = "🔥 Squier Telecaster Price Drop Alert"
    msg["From"] = EMAIL
    msg["To"] = RECEIVER

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)

# =========================
# STREAMLIT UI
# =========================

st.title("🎸 Squier Affinity Telecaster Tracker")

if st.button("Check Now"):
    regular_df, bstock_df = scrape_guitars()

    regular_df = compare_prices(regular_df, REGULAR_FILE)
    bstock_df = compare_prices(bstock_df, BSTOCK_FILE)

    send_email_alert(regular_df, bstock_df)

    # -------- REGULAR --------
    st.header("🟢 Regular Stock")

    if regular_df.empty:
        st.write("No regular models found.")
    else:
        for _, row in regular_df.iterrows():
            st.subheader(row["Name"])
            st.write(f"💰 {row['Price']} €")
            if row["Drop"] > 0:
                st.success(f"🔥 Price dropped by {row['Drop']} €!")
            st.markdown(f"[View on Thomann]({row['Link']})")
            st.divider()

    # -------- B-STOCK --------
    st.header("🟡 B-Stock")

    if bstock_df.empty:
        st.write("No B-Stock models found.")
    else:
        for _, row in bstock_df.iterrows():
            st.subheader(row["Name"])
            st.write(f"💰 {row['Price']} €")
            if row["Drop"] > 0:
                st.success(f"🔥 Price dropped by {row['Drop']} €!")
            st.markdown(f"[View on Thomann]({row['Link']})")
            st.divider()
