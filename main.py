import requests
import datetime
import pytz
import feedparser
import os

# ====== CONFIG (GitHub Secrets) ======
bot_token = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

# ====== API URL-ek ======
coingecko_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,ripple,binancecoin&vs_currencies=usd&include_24hr_change=true"
fg_url = "https://api.alternative.me/fng/?limit=1"

news_feeds = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss"
]

# ====== FUNKCIÓK ======
def get_prices():
    try:
        r = requests.get(coingecko_url)
        return r.json()
    except:
        return None

def get_fg_index():
    try:
        r = requests.get(fg_url).json()
        value = r["data"][0]["value"]
        classification = r["data"][0]["value_classification"]
        return value, classification
    except:
        return None, None

def get_news():
    items = []
    for url in news_feeds:
        feed = feedparser.parse(url)
        if len(feed.entries) > 0:
            items.append(feed.entries[0].title)
    return items[:2]

def send_msg(text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=data)

def generate_post():
    prices = get_prices()
    fg_value, fg_name = get_fg_index()
    news = get_news()

    if prices is None:
        return "⚠️ Hiba: nem tudtam lekérni az árfolyamokat."

    btc = prices["bitcoin"]["usd"]
    btc_change = prices["bitcoin"]["usd_24h_change"]

    eth = prices["ethereum"]["usd"]
    sol = prices["solana"]["usd"]
    xrp = prices["ripple"]["usd"]
    bnb = prices["binancecoin"]["usd"]

    now = datetime.datetime.now(pytz.timezone("Europe/Zurich"))
    title = "🌅 Reggeli Kripto Helyzetkép" if now.hour < 12 else "🌙 Esti Kripto Zárás"

    text = f"""{title} – CryptoCompassHU
(Nem minősül pénzügyi tanácsadásnak.)

📊 Piaci hangulat  
• Fear & Greed Index: {fg_value} – {fg_name}  
• BTC 24h változás: {btc_change:.2f}%  

💰 Árfolyamok  
• BTC: ${btc:,.0f}  
• ETH: ${eth:,.0f}  
• SOL: ${sol:,.1f}  
• XRP: ${xrp:.4f}  
• BNB: ${bnb:,.0f}

📰 Legfontosabb hírek  
• {news[0] if len(news)>0 else "—"}  
• {news[1] if len(news)>1 else "—"}  

🧠 Edukáció  
A következetes stratégia sokszor jobb, mint az impulzív döntések. A volatilitás a kripto természetes része.

⚠️ Ez nem befektetési tanács.
"""
    return text

# ====== FUTTATÁS ======
post = generate_post()
send_msg(post)
