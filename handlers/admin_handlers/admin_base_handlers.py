from aiogram import Router

from services.employee_service.employee_service import EmployeeService


class AdminBaseHandlers:
    router = Router()
    employee_service = EmployeeService()
