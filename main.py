import asyncio

from core.bot_app import BotApplication


async def main():
    app = BotApplication()
    await app.run()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit...')
