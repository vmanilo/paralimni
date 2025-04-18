import logging
import warnings
from datetime import datetime

from celery import Celery
from decouple import config

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

logger = logging.getLogger(__name__)
app = Celery("tasks", broker=f"{config('REDIS_HOST')}/0")


@app.task
def background_task(netuid: int):
    import asyncio
    from services.sentiment_analysis import SentimentAnalyser

    async def process():
        logger.info("Background task running...")

        start = datetime.now()
        analyser = SentimentAnalyser(
            datura_api_key=config('DATURA_API_KEY'),
            tweet_days_range=config('TWEET_DAYS_RANGE', cast=int, default=10),
            tweet_limit=config('TWEET_LIMIT', cast=int, default=10),
            chutest_api_key=config('CHUTES_API_TOKEN'),
            chutest_max_concurrent=config('CHUTES_MAX_CONCURRENT', cast=int, default=5),
        )

        score = await analyser.get_sentiment(netuid)

        logger.info(f'Sentiment score: {score}, elapsed time: {datetime.now() - start}')

    asyncio.run(process())
