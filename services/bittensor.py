import aioredis
from async_substrate_interface.async_substrate import AsyncSubstrateInterface
from bittensor.core.chain_data import decode_account_id
from bittensor.core.settings import SS58_FORMAT


class Bittensor:
    def __init__(self, chain_url: str, redis_url: str, redis_ttl: int):
        self.chain = ChainHandler(chain_url)
        self.cache = CacheHandler(redis_url, redis_ttl)

    async def get_dividend(self, netuid: int, hotkey: str) -> (int | None, bool):
        dividend = await self.cache.get_dividend(netuid, hotkey)
        if dividend is not None:
            return dividend, True

        dividend = await self.chain.get_dividend(netuid, hotkey)
        if dividend is not None:
            await self.cache.store_dividend(netuid, hotkey, dividend)

        return dividend, False


class ChainHandler:
    def __init__(self, chain_url: str):
        self.chain_url = chain_url

    async def get_dividend(self, netuid: int, hotkey: str) -> int | None:
        async with AsyncSubstrateInterface(self.chain_url, ss58_format=SS58_FORMAT) as substrate:
            block_hash = await substrate.get_chain_head()

            result = await substrate.query_map(
                "SubtensorModule",
                "TaoDividendsPerSubnet",
                [netuid],
                block_hash=block_hash
            )

            async for k, v in result:
                account, val = decode_account_id(k), v.value
                if account == hotkey:
                    return int(val)

        return None


class CacheHandler:
    def __init__(self, redis_url: str, redis_ttl: int):
        self.redis_url = redis_url
        self.redis_ttl = redis_ttl

    async def get_dividend(self, netuid: int, hotkey: str) -> int | None:
        redis = await aioredis.from_url(self.redis_url, decode_responses=True)

        cached_value = await redis.get(cache_key(netuid, hotkey))
        if cached_value is not None:
            return int(cached_value)

        return None

    async def store_dividend(self, netuid: int, hotkey: str, dividend: int) -> None:
        redis = await aioredis.from_url(self.redis_url, decode_responses=True)
        await redis.set(
            cache_key(netuid, hotkey),
            dividend,
            ex=self.redis_ttl
        )


def cache_key(netuid: int, hotkey: str) -> str:
    return f"{netuid}:{hotkey}"
