from tracemalloc import take_snapshot

import objgraph
from aiogram.filters import Command
from aiogram.types import Message

from filters.is_admin import IsAdmin
from handlers.admin_handlers.admin_base_handlers import AdminBaseHandlers


class AdminServiceUtils(AdminBaseHandlers):
    @staticmethod
    @AdminBaseHandlers.router.message(IsAdmin(), Command('memory'))
    async def memory_usage(message: Message):
        snapshot = take_snapshot()
        top_stats = snapshot.statistics('lineno')[:10]
        response = "Top-10 memory consumers:\n"
        for stat in top_stats:
            response += f"{stat}\n"
        await message.reply(response)

    @staticmethod
    @AdminBaseHandlers.router.message(IsAdmin(), Command('leak'))
    async def memory_leakage(message: Message):
        most_common_types = objgraph.most_common_types(limit=10)
        response = "Top-10 objects in memory:\n"
        for obj_type, count in most_common_types:
            response += f"{obj_type}: {count}\n"
        await message.reply(response)
