import asyncio

from api.api import start_web_server
from tasks.task import background_task


# Main entry point for the app
async def main():
    await asyncio.gather(
        start_web_server(),
        background_task()
    )


if __name__ == "__main__":
    asyncio.run(main())
