import asyncio
import logging
import math
from datetime import datetime

from bittensor.core.async_subtensor import AsyncSubtensor, Balance
from bittensor_wallet import Wallet
from celery import Celery
from decouple import config

from services.sentiment_analysis import SentimentAnalyser

logger = logging.getLogger(__name__)
app = Celery("tasks", broker=f"{config('REDIS_HOST')}/0")


@app.task
def background_task(netuid: int, hotkey: str):
    async def process():
        logger.info("Background task starting...")

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

        if score is None:
            return

        async with AsyncSubtensor(network=config('NETWORK')) as subtensor:
            wallet = Wallet(name='app_wallet')
            if wallet.coldkey_file.data is None:
                wallet = wallet.regenerate_coldkey(mnemonic=config('WALLET_MNEMONIC'), use_password=False,
                                                   suppress=True, overwrite=False)

            amount = Balance.from_tao(0.01 * math.fabs(score))

            try:
                if score > 0:
                    result = await subtensor.add_stake(wallet, hotkey_ss58=hotkey, netuid=netuid, amount=amount)
                    logger.info(f'add_stake hotkey: {hotkey}, netuid: {netuid}, amount: {amount}, result: {result}')
                elif score < 0:
                    result = await subtensor.unstake(wallet, hotkey_ss58=hotkey, netuid=netuid, amount=amount)
                    logger.info(f'unstake hotkey: {hotkey}, netuid: {netuid}, amount: {amount}, result: {result}')
            except Exception as e:
                logger.error(f'Stake/unstake failed due to error: {e}')

        logger.info("Background task completed.")

    asyncio.run(process())
