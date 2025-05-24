import streamlit as st
import requests
from textblob import TextBlob
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Proxy details
proxy_host = "brd.superproxy.io"
proxy_port = "33335"
proxy_user = "brd-customer-hl_5c430880-zone-mcp_news_scraper"
proxy_pass = "885fuzigki04"

proxies = {
    "http": f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}",
    "https": f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

NEWS_API_KEY = "79d21bcb52f146048f360f57e1b5354f"

def fetch_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&pageSize=10"
    response = requests.get(url, proxies=proxies, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json().get("articles", [])
    else:
        st.error(f"Failed to fetch news, status code: {response.status_code}")
        return []

def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.1:
        return "Positive", "😊", "#d4edda"
    elif polarity < -0.1:
        return "Negative", "😞", "#f8d7da"
    else:
        return "Neutral", "😐", "#fff3cd"

st.set_page_config(page_title="Real-Time News Sentiment Tracker", layout="wide")

st.title("📰 Real-Time News Sentiment Tracker")
st.write("Enter a keyword below to fetch live news headlines and analyze their sentiment.")

query = st.text_input("Keyword", value="bitcoin")

if query:
    with st.spinner("Fetching news and analyzing sentiment..."):
        articles = fetch_news(query)

    if articles:
        for article in articles:
            title = article.get("title")
            description = article.get("description") or ""
            url = article.get("url")
            sentiment, emoji, bg_color = analyze_sentiment(description)

            st.markdown(
                f"""
                <div style="background-color: {bg_color}; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <h4>{emoji} <a href="{url}" target="_blank" style="text-decoration:none; color:black;">{title}</a></h4>
                    <p>{description}</p>
                    <b>Sentiment:</b> {sentiment}
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No articles found for this keyword.")
