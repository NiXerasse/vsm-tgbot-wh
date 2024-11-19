from database.models import Employee
from services.auth_service.auth_status import AuthStatus


class AuthResult:
    def __init__(self, status: AuthStatus, employee: Employee | None = None):
        self.status = status
        self.employee = employee
