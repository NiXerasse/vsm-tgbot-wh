from middlewares.fsm_data_middleware import FSMDataMiddleware
from middlewares.i18n_middleware import I18nMiddleware
from middlewares.session_middleware import DataBaseSession


class MiddlewareManager:
    def __init__(self, dispatcher, session_maker):
        self.dispatcher = dispatcher
        self.session_maker = session_maker

    def setup(self):
        self.dispatcher.update.middleware(DataBaseSession(session_pool=self.session_maker))
        self.dispatcher.update.middleware(FSMDataMiddleware())
        self.dispatcher.update.middleware(I18nMiddleware())
