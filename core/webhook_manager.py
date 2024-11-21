import os
import ssl

from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config.env import certs_path, bot_token, webhook_port, webhook_host, webhook_path


class WebhookManager:
    def __init__(self, dispatcher, bot):
        self.dispatcher = dispatcher
        self.bot = bot
        self.runner = None

    async def start_webhook(self):
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(
            certfile=os.path.join(certs_path, "fullchain.pem"),
            keyfile=os.path.join(certs_path, "privkey.pem")
        )

        app = web.Application()
        SimpleRequestHandler(dispatcher=self.dispatcher, bot=self.bot).register(app, path=webhook_path)
        setup_application(app, self.dispatcher, bot=self.bot)

        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, host="0.0.0.0", port=webhook_port, ssl_context=ssl_context)
        print(f"Starting webhook server on {webhook_host}:{webhook_port}{webhook_path}...")
        await site.start()

    async def stop_webhook(self):
        if self.runner:
            await self.runner.cleanup()
