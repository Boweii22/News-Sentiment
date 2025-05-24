import streamlit as st
import requests
from textblob import TextBlob
import pandas as pd
import plotly.express as px
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Proxy setup
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
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&pageSize=30&sortBy=publishedAt"
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
        return "Positive", polarity
    elif polarity < -0.1:
        return "Negative", polarity
    else:
        return "Neutral", polarity

st.set_page_config(page_title="Real-Time News Sentiment Tracker", layout="wide")

# Styling
st.markdown("""
<style>
    .news-card {
        background: #fff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgb(0 0 0 / 0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s ease-in-out;
    }
    .news-card:hover {
        transform: scale(1.03);
        box-shadow: 0 6px 20px rgb(0 0 0 / 0.15);
    }
    .sentiment-positive { color: #2ecc71; font-weight: bold; }
    .sentiment-negative { color: #e74c3c; font-weight: bold; }
    .sentiment-neutral { color: #f39c12; font-weight: bold; }
    a { text-decoration: none; color: inherit; }
</style>
""", unsafe_allow_html=True)

st.title("📰 Real-Time News Sentiment Tracker")
st.write("Enter a keyword below to fetch live news and visualize sentiment trends with a polished, data-driven dashboard.")

query = st.text_input("Enter keyword", value="bitcoin")

if query:
    with st.spinner("Fetching news and analyzing sentiment..."):
        articles = fetch_news(query)

    if articles:
        # Analyze sentiment for each article
        data = []
        for art in articles:
            desc = art.get("description") or art.get("title") or ""
            sentiment, polarity = analyze_sentiment(desc)
            data.append({
                "title": art.get("title"),
                "description": desc,
                "url": art.get("url"),
                "sentiment": sentiment,
                "polarity": polarity,
                "publishedAt": art.get("publishedAt")
            })

        df = pd.DataFrame(data)
        df['publishedAt'] = pd.to_datetime(df['publishedAt'])

        # KPI cards
        pos_count = (df['sentiment'] == "Positive").sum()
        neu_count = (df['sentiment'] == "Neutral").sum()
        neg_count = (df['sentiment'] == "Negative").sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Positive 👍", pos_count, delta=int(pos_count - neg_count), delta_color="normal")
        col2.metric("Neutral 😐", neu_count)
        col3.metric("Negative 👎", neg_count, delta=int(neg_count - pos_count), delta_color="inverse")

    

        # Sentiment distribution pie chart
        # fig_pie = px.pie(
        #     df['sentiment'].value_counts().reset_index(),
        #     values='sentiment',
        #     names='index',
        #     color='index',
        #     color_discrete_map={
        #         "Positive": "#2ecc71",
        #         "Neutral": "#f39c12",
        #         "Negative": "#e74c3c"
        #     },
        #     title="Sentiment Distribution"
        # )
        # fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        # st.plotly_chart(fig_pie, use_container_width=True)
        sentiment_counts = df['sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['sentiment', 'count']

        fig_pie = px.pie(
            sentiment_counts,
            names='sentiment',
            values='count',
            color='sentiment',
            color_discrete_map={
            "Positive": "#2ecc71",
            "Neutral": "#f39c12",
            "Negative": "#e74c3c"
    },
    title="Sentiment Distribution"
)


        # Sentiment polarity over time line chart
        fig_line = px.line(
            df.sort_values('publishedAt'),
            x='publishedAt',
            y='polarity',
            title="Sentiment Polarity Over Time",
            labels={"publishedAt": "Published Date", "polarity": "Polarity (-1 to 1)"}
        )
        fig_line.update_traces(mode='markers+lines', marker=dict(size=8, color='#3498db'))
        st.plotly_chart(fig_line, use_container_width=True)

        # News articles in card style
        st.subheader("Latest News Articles")
        for _, row in df.iterrows():
            sentiment_class = {
                "Positive": "sentiment-positive",
                "Negative": "sentiment-negative",
                "Neutral": "sentiment-neutral"
            }[row['sentiment']]

            st.markdown(
                f"""
                <div class="news-card">
                    <h4><a href="{row['url']}" target="_blank">{row['title']}</a></h4>
                    <p>{row['description']}</p>
                    <p class="{sentiment_class}">Sentiment: {row['sentiment']}</p>
                    <small>Published: {row['publishedAt'].strftime('%Y-%m-%d %H:%M:%S')}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No articles found for this keyword.")
