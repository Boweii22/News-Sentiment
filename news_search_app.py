import streamlit as st
import requests
from bs4 import BeautifulSoup

# Bright Data API Config
BRIGHTDATA_API_URL = "https://api.brightdata.com/request"
BRIGHTDATA_TOKEN = "c73b9305e92813536b997e96516ea38780845020405678a57c45d8d4fc603c36"  # Replace with your actual token
ZONE = "web_unlocker1_news_sentiment"

def fetch_news_from_guardian(query):
    target_url = f"https://www.theguardian.com/uk/technology?q={query}"

    payload = {
        "zone": ZONE,
        "url": target_url,
        "format": "raw"
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {BRIGHTDATA_TOKEN}"
    }

    response = requests.post(BRIGHTDATA_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        st.error("Error fetching data from Bright Data API")
        return None

def parse_guardian_html(html):
    soup = BeautifulSoup(html, "html.parser")
    articles = []

    for tag in soup.find_all("a", class_="u-faux-block-link__overlay js-headline-text"):
        title = tag.get_text(strip=True)
        link = tag.get("href")
        if title and link:
            articles.append({"title": title, "link": link})
    return articles

# Streamlit UI
st.set_page_config(page_title="News Search App", layout="centered")
st.title("🗞️ News Search with BrightData")

query = st.text_input("Enter a topic to search news on The Guardian", placeholder="e.g. Google, Bitcoin, Elections")

if st.button("Search") and query:
    st.info(f"Searching The Guardian for: {query}")
    html = fetch_news_from_guardian(query)
    if html:
        articles = parse_guardian_html(html)
        if articles:
            for article in articles:
                st.markdown(f"### [{article['title']}]({article['link']})")
        else:
            st.warning("No articles found.")
