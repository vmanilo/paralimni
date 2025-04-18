from async_substrate_interface.async_substrate import AsyncSubstrateInterface
from bittensor.core.chain_data import decode_account_id
from bittensor.core.settings import SS58_FORMAT


class Bittensor:
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
