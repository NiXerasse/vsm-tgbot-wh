from aiogram import Router

from services.employee_service.employee_service import EmployeeService


class EmployeeBaseHandlers:
    router = Router()
    employee_service = EmployeeService()
