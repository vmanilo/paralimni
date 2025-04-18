import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import List

import aiohttp
from datura_py import Datura

logger = logging.getLogger(__name__)


class SentimentAnalyser:
    def __init__(self,
                 datura_api_key: str,
                 tweet_days_range: int,
                 tweet_limit: int,
                 chutest_api_key: str,
                 chutest_max_concurrent: int):
        self.datura_api_key = datura_api_key
        self.tweet_days_range = tweet_days_range
        self.tweet_limit = tweet_limit
        self.chutest_api_key = chutest_api_key
        self.semaphore = asyncio.Semaphore(chutest_max_concurrent)

    async def get_sentiment(self, netuid: int) -> float | None:
        tweets = self._get_tweets(netuid)
        scores = await asyncio.gather(
            *[self._score_tweet(tweet, netuid) for tweet in tweets]
        )

        scores = [x for x in scores if x is not None]

        if len(scores) == 0:
            return None

        return sum(scores) / len(scores)

    def _get_tweets(self, netuid: int) -> List[str]:
        datura = Datura(api_key=self.datura_api_key)

        start_date = (datetime.now() - timedelta(days=self.tweet_days_range)).strftime("%Y-%m-%d")
        current_date = datetime.now().strftime("%Y-%m-%d")

        try:
            result = datura.basic_twitter_search(
                query=f"Bittensor netuid {netuid}",
                sort="Top",
                start_date=start_date,
                end_date=current_date,
                lang="en",
                min_retweets=5,
                min_likes=10,
                min_replies=2,
                verified=True,
                is_quote=False,
                count=self.tweet_limit,
            )
        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
            return []

        return [tweet['text'] for tweet in result]

    async def _score_tweet(self, tweet: str, netuid: int) -> int | None:
        headers = {
            "Authorization": "Bearer " + self.chutest_api_key,
            "Content-Type": "application/json"
        }

        body = {
            "model": "unsloth/Llama-3.2-3B-Instruct",
            "messages": [
                {
                    "role": "assistant",
                    "content": f'''
                                Does this tweet relates to 'Bittensor netuid {netuid}'?
                                If yes, please estimate sentiment of this tweet from -100 to +100, 
                                and then give me your score without reasons 
                                and shorten it to score value (with using + or - for positive and negative values) 
                                in format: 'score: value'
    
                                {tweet}
                            '''
                }
            ],
            "stream": False,
            "max_tokens": 10000,
            "temperature": 0.5
        }

        try:
            async with self.semaphore:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                            "https://llm.chutes.ai/v1/chat/completions",
                            headers=headers,
                            json=body
                    ) as response:
                        resp = await response.json()
                        content = resp['choices'][0]['message']['content']

                        score_match = re.search(r'(score)\s*:?(is)?\s*([+-]?\d+)', content, re.IGNORECASE)
                        if score_match:
                            return int(score_match.group(3))
                        return None

        except Exception as e:
            logger.error(f"Error fetching and parsing LLM response: {e}")

            return None
