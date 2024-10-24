import pprint

from sqlalchemy import DateTime, func, Integer, BigInteger, String, ForeignKey, Date, PrimaryKeyConstraint, \
    CheckConstraint, Index, inspect, Text, JSON, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def sqlalchemy_object_to_dict(self):
        mapper = inspect(self).mapper
        columns = {column.key: getattr(self, column.key) for column in mapper.column_attrs}
        return {**columns}

    def __repr__(self):
        return pprint.pformat(self.sqlalchemy_object_to_dict())

    def __str__(self):
        return pprint.pformat(self.sqlalchemy_object_to_dict())

class User(Base):
    __tablename__ = 'users'
    bot_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fsm_state: Mapped[Text] = mapped_column(Text, nullable=True)
    fsm_data: Mapped[JSON] = mapped_column(JSON, nullable=True)
    locale: Mapped[String] = mapped_column(String(2), nullable=True)

    __table_args__ = (
        UniqueConstraint('bot_id', 'user_id', 'chat_id', name='users_unique_constraint'),
    )


class Employee(Base):
    __tablename__ = 'employee'

    id: Mapped[int] = mapped_column(primary_key=True)
    tab_no: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    pin: Mapped[str] = mapped_column(String(6), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=True, default='')

    time_records: Mapped[list["TimeRecord"]] = relationship('TimeRecord', back_populates='employee')


class Subdivision(Base):
    __tablename__ = 'subdivision'

    id: Mapped[int] = mapped_column(primary_key=True)
    gsheets_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    time_records: Mapped[list["TimeRecord"]] = relationship('TimeRecord', back_populates='subdivision')


class TimeRecord(Base):
    __tablename__ = 'time_record'

    employee_id: Mapped[int] = mapped_column(ForeignKey('employee.id'), nullable=False)
    subdivision_id: Mapped[int] = mapped_column(ForeignKey('subdivision.id'), nullable=False)
    work_date: Mapped[Date] = mapped_column(Date, nullable=False)
    hours_worked: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('employee_id', 'subdivision_id', 'work_date'),
        CheckConstraint('hours_worked >= 0', name='hours_worked >= 0'),
        Index('idx_time_records_employee_date', 'employee_id', 'work_date'),
    )

    employee: Mapped["Employee"] = relationship('Employee', back_populates='time_records')
    subdivision: Mapped["Subdivision"] = relationship('Subdivision', back_populates='time_records')
