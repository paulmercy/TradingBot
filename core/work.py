from django.shortcuts import render
import ccxt
from nltk.sentiment import SentimentIntensityAnalyzer
# import pandas as pd
# import matplotlib.pyplot as plt
import datetime
import requests
from bs4 import BeautifulSoup
import nltk
from .models import BinanceBot, HistoricalData, CryptoAsset


def moving_average(data, period):
    values = []
    if all(isinstance(i, (int, float)) for i in data):
        for i in range(len(data) - period):
            total = 0
            for j in range(i, i+period):
                total += data[j]
            values.append(total / period)
    return values


def binance_bot(request):
    # Define the API key and secret
    api_key = 'bu7Ffd6JnugsmTULzg1xZdNEc5yri5lnLHVFunFgRXR7offJYYFsPDO9shs1OWgC'
    secret = 'qwYqS6opzZqmM06l7hqkX3tTcEJeQ6kFSAKtjbPKjYIygXfXsO69pBMz5WHpg7Xk'

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

    if not ohlcv:
        print("The list is empty, check the symbol and timeframe or the connection to the API")
    else:
        for candle in ohlcv:
            timestamp, open, high, low, close, volume = candle
             # Convert timestamp from UNIX timestamp to Python datetime object
            timestamp = datetime.datetime.fromtimestamp(timestamp / 1000)
            date = datetime.datetime.now().date()
            time = datetime.datetime.now().time()
            ohlcv_data, created = HistoricalData.objects.update_or_create(timestamp=timestamp, defaults={'symbol': symbol, 'open': open, 'high': high, 'low': low, 'close': close, 'volume': volume})
            ohlcv_data.save()

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

    # Use a sentiment analysis library to determine the overall sentiment of the news articles
    tokens = [lemmatizer.lemmatize(stemmer.stem(token)) for token in tokens]
    # Create a dictionary of positive and negative words
    positive_words = ["good", "great", "positive", "bullish", "profit", "growth"]
    negative_words = ["bad", "negative", "bearish", "loss", "decline"]

     # Count the number of positive and negative words in the text
    positive_count = 0
    negative_count = 0
    for token in tokens:
        if token in positive_words:
            positive_count += 1
        elif token in negative_words:
            negative_count += 1

    # Determine the overall sentiment of the news
    sentiment = "neutral"
    if positive_count > negative_count:
        sentiment = "positive"
    elif positive_count < negative_count:
        sentiment = "negative"


    balance = 1000

    # Use the sentiment analysis results to determine if the sentiment is positive, negative, or neutral
    if sentiment == "positive":
        # Buy BTC using the balance variable
        balance -= current_candle
    elif sentiment == "negative":
        # Sell BTC using the balance variable
        balance += current_candle
    else:
        print("Sentiment is Neutral")

    # Create an instance of the BinanceBot model and save it to the database
    bot = BinanceBot(balance=balance)
    bot.save()

    # Pass the bot's balance to the template
    context = {'balance': balance}
    return render(request, 'binance_bot.html', context)
