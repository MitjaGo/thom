import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText

URL = "https://www.thomann.it/cat_BF_squier.html?oa=pra&sp=solr_improved&category%5B%5D=GIEGTE&cme=true&manufacturer%5B%5D=Squier&bn=Squier&filter=true"
HEADERS = {"User-Agent": "Mozilla/5.0"}

REGULAR_FILE = "data_regular.csv"
BSTOCK_FILE = "data_bstock.csv"

EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["PASSWORD"]
STREAMLIT_URL = os.environ["APP_URL"]
RECEIVER = "mitja.goja@gmail.com"


def scrape():
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

            if "B-Stock" in name:
                bstock.append(entry)
            else:
                regular.append(entry)

    return pd.DataFrame(regular), pd.DataFrame(bstock)


def save(df, filename):
    df.to_csv(filename, index=False)


def send_email(reg_df, bst_df):
    body = f"""
Weekly Squier Affinity Telecaster Check

Regular models: {len(reg_df)}
B-Stock models: {len(bst_df)}

Open dashboard:
{STREAMLIT_URL}
"""

    msg = MIMEText(body)
    msg["Subject"] = "🎸 Weekly Squier Tracker"
    msg["From"] = EMAIL
    msg["To"] = RECEIVER

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)


if __name__ == "__main__":
    reg, bst = scrape()
    save(reg, REGULAR_FILE)
    save(bst, BSTOCK_FILE)
    send_email(reg, bst)

