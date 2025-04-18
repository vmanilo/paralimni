import asyncio

from decouple import config

from api.api import default_netuid
from services.sentiment_analysis import SentimentAnalyser


async def background_task():
    while True:
        await asyncio.sleep(10)  # Simulate periodic work (e.g., every 10 seconds)
        print("Background task running...")

        analyser = SentimentAnalyser(
            datura_api_key=config('DATURA_API_KEY'),
            tweet_days_range=config('TWEET_DAYS_RANGE', cast=int, default=10),
            tweet_limit=config('TWEET_LIMIT', cast=int, default=10),
            chutest_api_key=config('CHUTES_API_TOKEN'),
            chutest_max_concurrent=config('CHUTES_MAX_CONCURRENT', cast=int, default=5),
        )

        score = await analyser.get_sentiment(netuid=default_netuid)

        print('Sentiment score:', score)
