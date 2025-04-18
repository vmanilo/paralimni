import asyncio

from api.api import start_web_server

# Main entry point for the app
async def main():
    await asyncio.gather(
        start_web_server(),
    )


if __name__ == "__main__":
    asyncio.run(main())
