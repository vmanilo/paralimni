from datetime import datetime, timezone
from typing import Final, Annotated

import uvicorn
from bittensor.core.settings import SS58_FORMAT
from decouple import config
from fastapi import FastAPI, status
from fastapi import Query
from fastapi.responses import JSONResponse
from pydantic import AfterValidator
from scalecodec import is_valid_ss58_address

from services.bittensor import Bittensor

app = FastAPI()

default_netuid: Final = config('DEFAULT_NETUID', cast=int)
default_hotkey: Final = config('DEFAULT_HOTKEY')


def validate_hotkey(value: str) -> str:
    if is_valid_ss58_address(value, SS58_FORMAT):
        return value

    raise ValueError("hotkey must be a valid SS58 formatted address")


@app.get("/api/v1/tao_dividends")
async def get_dividends(
        netuid: Annotated[
            int,
            Query(
                ge=0,
            ),
        ] = default_netuid,
        hotkey: Annotated[
            str,
            AfterValidator(validate_hotkey)
        ] = default_hotkey,
):
    tao = Bittensor(config('CHAIN_URL'))
    dividend = await tao.get_dividend(netuid, hotkey)

    if dividend is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "Dividend not found",
            }
        )

    return {
        "timestamp": datetime.now(timezone.utc),
        "netuid": netuid,
        "hotkey": hotkey,
        "dividend": dividend,
        "cached": False,
        "stake_tx_triggered": False
    }


async def start_web_server():
    """
    Starts the FastAPI server using Uvicorn within an asyncio coroutine.
    """
    cfg = uvicorn.Config(app,
                         host=config('APP_HOST'),
                         port=config('APP_PORT', cast=int),
                         log_level=config('APP_LOG_LEVEL', default='info'),
                         reload=config('APP_RELOAD', cast=bool, default=False))
    server = uvicorn.Server(cfg)
    await server.serve()
