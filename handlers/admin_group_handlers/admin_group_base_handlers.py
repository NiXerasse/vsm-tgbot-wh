from aiogram import Router

from config.env import admin_group_id
from services.admin_group_message_service.admin_group_message_service import AdminGroupMessageService


class AdminGroupBaseHandlers:
    router = Router()

    adm_grp_msg_service = AdminGroupMessageService(admin_group_id)
