from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


class UserRepository:
    @staticmethod
    async def delete_user_with_tab_no(session: AsyncSession, tab_no):
        users = (await session.execute(
            select(User)
        )).scalars().all()

        for user in users:
            user_tab_no = user.fsm_data.get('tab_no', None)
            if user_tab_no == tab_no:
                await session.delete(user)
        await session.commit()

    @staticmethod
    async def add_user(session: AsyncSession, bot_id: int, user_id: int, chat_id: int):
        result = await session.execute(
            select(User).where(
                and_(
                    User.bot_id == bot_id,
                    User.user_id == user_id,
                    User.chat_id == chat_id
                )
            )
        )
        user = result.scalars().first()
        if user is None:
            user = User(bot_id=bot_id, user_id=user_id, chat_id=chat_id)
            session.add(user)
            await session.commit()

        return user
