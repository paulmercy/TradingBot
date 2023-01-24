from django.shortcuts import render
import ccxt
from nltk.sentiment import SentimentIntensityAnalyzer
# import pandas as pd
# import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import nltk
from .models import BinanceBot, HistoricalData, CryptoAsset

def binance_bot(request):
    # Define the API key and secret
    api_key = 'YOUR_API_KEY'
    secret = 'YOUR_SECRET'

    # Initialize the Binance exchange object
    exchange = ccxt.binance({
        'rateLimit': 2000,
        'enableRateLimit': True,
        'verbose': True,
        'apiKey': api_key,
        'secret': secret
    })

    # Load the markets
    exchange.load_markets()

    # Define the symbol and timeframe
    symbol = 'BTC/USDT'
    timeframe = '1d'

    # Fetch historical data for the last 100 candles And save to the database
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe)

    for candle in ohlcv:
        timestamp, open, high, low, close, volume = candle
        ohlcv_data = HistoricalData(symbol=symbol, timestamp=timestamp, open=open, high=high, low=low, close=close, volume=volume)
        ohlcv_data.save()

    # Define the short and long moving averages
    short_ma = 10
    long_ma = 50

    # Calculate the moving averages
    short_ma_values = moving_average(ohlcv, short_ma)
    long_ma_values = moving_average(ohlcv, long_ma)


# To allow user select strategy 
    # if strategy == 'news_based':
    #     balance, trades = news_based(ohlcv)
    # elif strategy == 'moving_average_crossover':
    #     balance, trades = moving_average_crossover(ohlcv)
    # else:
    #     balance, trades = news_based(ohlcv)


    # Fetch news articles about the specific crypto asset from a news source
    url = "https://cointelegraph.com/tags/bitcoin"
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')

    # Extract the text of the news articles
    text = ""
    for article in soup.find_all('div', class_='article'):
        text += article.text

    # Perform NLP tasks using NLTK
    nltk.download('punkt')
    nltk.download('wordnet')

    # Tokenize the text
    tokens = nltk.word_tokenize(text)

    # Perform stemming and lemmatization
    stemmer = nltk.stem.PorterStemmer()
    lemmatizer = nltk.stem.WordNetLemmatizer()

    tokens_stemmed = [stemmer.stem(token) for token in tokens]
    tokens_lemmatized = [lemmatizer.lemmatize(token) for token in tokens]

    # Use a sentiment analysis library to determine the overall sentiment of the news articles
    sentiment_analyzer = SentimentIntensityAnalyzer()
    sentiment = sentiment_analyzer.polarity_scores(text)

    # Initialize a variable to track the bot's balance
    balance = 1000
    trades = 0

    # Use the sentiment analysis results to determine if the sentiment is positive, negative, or neutral
    if sentiment['compound'] > 0 and short_ma_values > long_ma_values:
        # Buy BTC using the balance variable
        balance -= current_candle
        trades += 1
    elif sentiment['compound'] < 0 and short_ma_values < long_ma_values:
        # Sell BTC using the balance variable
        balance += current_candle
        trades += 1
    else:
        print("Sentiment is Neutral or Moving averages didn't give a signal")
    
    # Create an instance of the BinanceBot model and save it to the database
    bot = BinanceBot(balance=balance, trades=trades)
    bot.save()

    # Pass the bot's balance to the template
    context = {'balance': balance, 'trades': trades}
    return render(request, 'binance_bot.html', context)


# def scanner(request):
#     exchange = ccxt.binance()
#     market_data = exchange.load_markets()
#     # Loop through the market data and store the relevant information in the CryptoAsset model
#     for asset in market_data:
#         symbol = asset['symbol']
#         name = asset['name']
#         market_cap = asset['market_cap']
#         price = asset['price']
#         volume = asset['volume']
#         CryptoAsset.objects.create(symbol=symbol, name=name, market_cap=market_cap, price=price, volume=volume)
#         #...
#         assets_data = CryptoAsset.objects.values()
#         assets_df = pd.DataFrame.from_records(assets_data)
#     #...assets_df.sort_values(by='market_cap', ascending=False, inplace=True)
#         top_10_assets = assets_df.head(10)
#         top_10_assets.plot(x='name', y='market_cap', kind='bar')
#         plt.show()
#         context = {'top_10_assets': top_10_assets}
#     return render(request, 'scanner_results.html', context)

