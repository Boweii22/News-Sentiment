import streamlit as st
import requests
from textblob import TextBlob
import pandas as pd
import plotly.express as px
import urllib3

# Disable SSL warnings
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


# Configure page settings
st.set_page_config(page_title="Real-Time News Sentiment Tracker", layout="wide")

# Custom CSS styling
st.markdown(
    """
    <style>
    .news-card {
        background: linear-gradient(145deg, #0E1117, #041325);
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        padding: 1rem 1.5rem;
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        display: flex;
        gap: 1rem;
        align-items: flex-start;
    }
    
    .news-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.18);
    }
    
    .news-thumb {
        width: 120px;
        height: 80px;
        object-fit: cover;
        border-radius: 8px;
        flex-shrink: 0;
    }
    
    .news-content {
        flex-grow: 1;
    }
    
    .news-title {
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        color: #0d253f;
    }
    
    .news-desc {
        font-size: 0.95rem;
        color: #2e3a59;
        margin-bottom: 0.5rem;
    }
    
    .sentiment-badge {
        padding: 0.25rem 0.7rem;
        font-weight: 600;
        font-size: 0.85rem;
        border-radius: 12px;
        color: white;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        user-select: none;
        margin-bottom: 0.5rem;
    }
    
    .sentiment-positive {
        background-color: #4e4e4e;
    }
    
    .sentiment-neutral {
        background-color: #4e4e4e;
    }
    
    .sentiment-negative {
        background-color: #4e4e4e;
    }
    
    .news-date {
        font-size: 0.8rem;
        color: #829ab1;
    }
    
    .news-link {
        text-decoration: none;
        color: #007bff;
        font-weight: 600;
        transition: color 0.2s ease;
    }
    
    .news-link:hover {
        color: #0056b3;
        text-decoration: underline;
    }
    
    .sentiment-positive { color: #2ecc71; font-weight: bold; }
    .sentiment-negative { color: #e74c3c; font-weight: bold; }
    .sentiment-neutral { color: #f39c12; font-weight: bold; }
    a { text-decoration: none; color: inherit; }
    
    /* Custom metric cards */
    .stMetric {
        border-radius: 12px;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.05);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# App title and description
st.title("📰 Real-Time News Sentiment Tracker")
st.write(
    "Enter a keyword below to fetch live news and visualize sentiment trends with a polished, data-driven dashboard."
)

# User input
query = st.text_input("Enter keyword", value="bitcoin", placeholder="e.g. bitcoin, AI, stock market")

if query:
    with st.spinner("Fetching news and analyzing sentiment..."):
        articles = fetch_news(query)
        
    if articles:
        # Analyze sentiment for each article
        data = []
        for art in articles:
            desc = art.get("description") or art.get("title") or ""
            sentiment, polarity = analyze_sentiment(desc)
            data.append(
                {
                    "title": art.get("title"),
                    "description": desc,
                    "url": art.get("url"),
                    "urlToImage": art.get("urlToImage"),
                    "sentiment": sentiment,
                    "polarity": polarity,
                    "publishedAt": art.get("publishedAt"),
                }
            )

        df = pd.DataFrame(data)
        df["publishedAt"] = pd.to_datetime(df["publishedAt"])

        # KPI cards
        pos_count = (df["sentiment"] == "Positive").sum()
        neu_count = (df["sentiment"] == "Neutral").sum()
        neg_count = (df["sentiment"] == "Negative").sum()

        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Positive 👍",
            pos_count,
            delta=int(pos_count - neg_count),
            delta_color="normal",
        )
        col2.metric("Neutral 😐", neu_count)
        col3.metric(
            "Negative 👎",
            neg_count,
            delta=int(neg_count - pos_count),
            delta_color="inverse",
        )

        # Sentiment distribution pie chart
        sentiment_counts = df["sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["sentiment", "count"]

        fig_pie = px.pie(
            sentiment_counts,
            names="sentiment",
            values="count",
            color="sentiment",
            color_discrete_map={
                "Positive": "#2ecc71",
                "Neutral": "#f39c12",
                "Negative": "#e74c3c",
            },
            title="Sentiment Distribution",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # Sentiment polarity over time line chart
        fig_line = px.line(
            df.sort_values("publishedAt"),
            x="publishedAt",
            y="polarity",
            title="Sentiment Polarity Over Time",
            labels={"publishedAt": "Published Date", "polarity": "Polarity (-1 to 1)"},
        )
        fig_line.update_traces(
            mode="markers+lines", 
            marker=dict(size=8, color="#3498db"),
            line=dict(color="#3498db", width=2)
        )
        fig_line.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)")
        )
        st.plotly_chart(fig_line, use_container_width=True)

        # News articles in card style
        st.subheader("Latest News Articles")
        
        for _, row in df.iterrows():
            sentiment_class = {
                "Positive": "sentiment-positive",
                "Negative": "sentiment-negative",
                "Neutral": "sentiment-neutral",
            }[row["sentiment"]]

            # Use article image if available, else fallback to placeholder
            img_url = (
                row.get("urlToImage")
                or "https://images.unsplash.com/photo-1586339949216-35c2747cc36d?q=80&w=1587&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
            )

            st.markdown(
                f"""
                <div class="news-card">
                    <img src="{img_url}" alt="thumbnail" class="news-thumb" />
                    <div class="news-content">
                        <h4 class="news-title">{row['title']}</h4>
                        <div class="sentiment-badge {sentiment_class}">
                            {"👍" if row['sentiment'] == "Positive" else "👎" if row['sentiment'] == "Negative" else "😐"} 
                            {row['sentiment']}
                        </div>
                        <p class="news-desc">{row['description']}</p>
                        <a href="{row['url']}" target="_blank" class="news-link">Read full article</a><br />
                        <small class="news-date">Published: {row['publishedAt'].strftime('%Y-%m-%d %H:%M:%S')}</small>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.warning("No articles found for this keyword. Try a different search term.")