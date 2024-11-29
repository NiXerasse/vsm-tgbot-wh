import asyncio
import tracemalloc

from core.bot_app import BotApplication


async def main():
    tracemalloc.start()
    app = BotApplication()
    await app.run()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit...')
