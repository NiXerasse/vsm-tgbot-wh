from handlers.admin_group_handlers.admin_group_service_handlers import AdminGroupServiceHandlers
from handlers.admin_handlers.admin_base_handlers import AdminBaseHandlers
from handlers.auth_handlers.auth_base_handlers import AuthBaseHandlers
from handlers.employee_handlers.employee_base_handlers import EmployeeBaseHandlers


class RouterManager:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def setup(self):
        self.dispatcher.include_routers(
            AdminBaseHandlers.router,
            AdminGroupServiceHandlers.router,
            EmployeeBaseHandlers.router,
            AuthBaseHandlers.router,
        )
