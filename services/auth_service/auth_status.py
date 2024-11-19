from enum import Enum


class AuthStatus(Enum):
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    ALREADY_AUTHORIZED = "already_authorized"
