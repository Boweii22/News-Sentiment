import requests

API_KEY = '79d21bcb52f146048f360f57e1b5354f'  # Replace this with your actual NewsAPI key
keyword = "technology"

url = f"https://newsapi.org/v2/everything?q={keyword}&sortBy=publishedAt&language=en&apiKey={API_KEY}"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    articles = data.get('articles', [])
    print(f"Found {len(articles)} articles about {keyword}:\n")
    for i, article in enumerate(articles[:5], 1):  # print first 5 articles
        print(f"{i}. {article['title']}")
        print(f"   Source: {article['source']['name']}")
        print(f"   URL: {article['url']}\n")
else:
    print(f"Failed to fetch news, status code: {response.status_code}")
