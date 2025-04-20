import asyncio
import logging

import aioredis
from async_substrate_interface.async_substrate import AsyncSubstrateInterface
from bittensor.core.settings import SS58_FORMAT

logger = logging.getLogger(__name__)


class Bittensor:
    """Bittensor service for handling chain interactions and caching.
    
    Provides functionality to interact with Bittensor blockchain and maintain a Redis cache
    for dividend values.
    """

    def __init__(self, chain_url: str, redis_url: str, redis_ttl: int, chain_max_concurrent: int, max_retries: int):
        self.chain = ChainHandler(chain_url, chain_max_concurrent, max_retries)
        self.cache = CacheHandler(redis_url, redis_ttl)

    async def get_dividend(self, netuid: int, hotkey: str) -> (int | None, bool):
        """Retrieve dividend value for given netuid and hotkey with caching.
        
        Args:
            netuid: Network subnet ID
            hotkey: Wallet hotkey address
            
        Returns:
            Tuple of (dividend value or None, bool indicating if value was from cache)
        """
        dividend = await self.cache.get_dividend(netuid, hotkey)
        if dividend is not None:
            return dividend, True

        dividend = await self.chain.get_dividend(netuid, hotkey)
        if dividend is not None:
            await self.cache.store_dividend(netuid, hotkey, dividend)

        return dividend, False


class ChainHandler:
    """Handles interactions with the Bittensor blockchain.
    
    Manages concurrent connections and retries for blockchain queries.
    """

    def __init__(self, chain_url: str, chain_max_concurrent: int, max_retries: int):
        self.chain_url = chain_url
        self.semaphore = asyncio.Semaphore(chain_max_concurrent)
        self.max_retries = max_retries

    async def get_dividend(self, netuid: int, hotkey: str) -> int | None:
        """Query blockchain for dividend value of given netuid and hotkey.
        
        Args:
            netuid: Network subnet ID
            hotkey: Wallet hotkey address
            
        Returns:
            Dividend value or None if query fails
        """
        for attempt in range(self.max_retries):
            try:
                async with self.semaphore:
                    async with AsyncSubstrateInterface(self.chain_url, ss58_format=SS58_FORMAT, max_retries=5,
                                                       retry_timeout=5) as substrate:
                        result = await substrate.query(
                            "SubtensorModule",
                            "TaoDividendsPerSubnet",
                            [netuid, hotkey],
                        )

                        return int(result.value)
            except ValueError as e:
                logger.error(f"Invalid response: {e}. Aborting retries.")
                break

            except Exception as e:
                logger.error(f"Substrate query error: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(5)

        logger.error(f"Failed to fetch dividend after {self.max_retries} attempts.")
        return None


class CacheHandler:
    """Handles Redis caching operations for Bittensor data.
    
    Provides methods to store and retrieve dividend values from Redis cache.
    """

    def __init__(self, redis_url: str, redis_ttl: int):
        self.redis_url = redis_url
        self.redis_ttl = redis_ttl

    async def get_dividend(self, netuid: int, hotkey: str) -> int | None:
        redis = await aioredis.from_url(self.redis_url, decode_responses=True)

        cached_value = await redis.get(cache_key(netuid, hotkey))
        if cached_value is not None:
            return int(cached_value)

        return None

    async def store_dividend(self, netuid: int, hotkey: str, dividend: int):
        """Store dividend value in Redis cache.
        
        Args:
            netuid: Network subnet ID
            hotkey: Wallet hotkey address
            dividend: Dividend value to cache
        """
        redis = await aioredis.from_url(self.redis_url, decode_responses=True)
        await redis.set(
            cache_key(netuid, hotkey),
            dividend,
            ex=self.redis_ttl,
        )


def cache_key(netuid: int, hotkey: str) -> str:
    """Generate Redis cache key for dividend value.
    
    Args:
        netuid: Network subnet ID
        hotkey: Wallet hotkey address
        
    Returns:
        Formatted cache key string
    """
    return f"{netuid}:{hotkey}"
