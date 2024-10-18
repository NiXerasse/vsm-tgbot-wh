from aiogram.fsm.state import State
from sqlalchemy import select, update, and_
from typing import Optional, Dict, Any
from aiogram.fsm.storage.base import BaseStorage, StorageKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert


from database.models import User
from database.orm import add_user
from logger.logger import logger


class PostgresFSMStorage(BaseStorage):
    def __init__(self, session_maker: sessionmaker):
        self.session_maker = session_maker

    async def set_state(self, key: StorageKey, state: Optional[State] = None) -> None:
        state_str = state.state if state else None
        logger.warning(f'Setting state for key: {key} to {state_str}')
        async with self.session_maker() as session:
            stmt = pg_insert(User).values(
                bot_id=key.bot_id,
                user_id=key.user_id,
                chat_id=key.chat_id,
                fsm_state=state_str
            ).on_conflict_do_update(
                index_elements=['bot_id', 'user_id', 'chat_id'],
                set_=dict(fsm_state=state_str)
            )
            await session.execute(stmt)
            await session.commit()

    async def get_state(self, key: StorageKey) -> Optional[str]:
        async with self.session_maker() as session:
            stmt = select(User).where(
                and_(
                    User.bot_id == key.bot_id,
                    User.user_id == key.user_id,
                    User.chat_id == key.chat_id
                )
            )
            user = (await session.execute(stmt)).scalar_one_or_none()
            if user is None:
                user = await add_user(session, key.bot_id, key.user_id, key.chat_id)

            # stmt = select(User.fsm_state).where(
            #     and_(
            #         User.bot_id == key.bot_id,
            #         User.user_id == key.user_id,
            #         User.chat_id == key.chat_id
            #     )
            # )
            # result = await session.execute(stmt)
            # state = result.scalar_one_or_none()
            return user.fsm_state

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        async with self.session_maker() as session:
            stmt = pg_insert(User).values(
                bot_id=key.bot_id,
                user_id=key.user_id,
                chat_id=key.chat_id,
                fsm_data=data
            ).on_conflict_do_update(
                index_elements=['bot_id', 'user_id', 'chat_id'],
                set_=dict(fsm_data=data)
            )
            await session.execute(stmt)
            await session.commit()

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        async with self.session_maker() as session:
            stmt = select(User.fsm_data).where(
                and_(
                    User.bot_id == key.bot_id,
                    User.user_id == key.user_id,
                    User.chat_id == key.chat_id
                )
            )
            result = await session.execute(stmt)
            data = result.scalar_one_or_none()
            return data or {}

    async def clear_state(self, key: StorageKey) -> None:
        async with self.session_maker() as session:
            stmt = update(User).where(
                and_(
                    User.bot_id == key.bot_id,
                    User.user_id == key.user_id,
                    User.chat_id == key.chat_id
                )
            ).values(fsm_state=None, fsm_data=None)
            await session.execute(stmt)
            await session.commit()

    async def has_state(self, key: StorageKey) -> bool:
        async with self.session_maker() as session:
            stmt = select(User.fsm_state).where(
                and_(
                    User.bot_id == key.bot_id,
                    User.user_id == key.user_id,
                    User.chat_id == key.chat_id
                )
            )
            result = await session.execute(stmt)
            state = result.scalar_one_or_none()
            return state is not None

    async def has_data(self, key: StorageKey) -> bool:
        async with self.session_maker() as session:
            stmt = select(User.fsm_data).where(
                and_(
                    User.bot_id == key.bot_id,
                    User.user_id == key.user_id,
                    User.chat_id == key.chat_id
                )
            )
            result = await session.execute(stmt)
            data = result.scalar_one_or_none()
            return data is not None

    async def close(self) -> None:
        pass
