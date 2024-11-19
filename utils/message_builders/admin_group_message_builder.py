from aiogram.utils.formatting import Text, Bold


class AdminGroupMessageBuilder:
    @staticmethod
    def register_message():
        return Text(
            '🚹 ', Bold('Выберите ОП для регистрации'), ' ⤵️', '\n'
        ).as_markdown()

    @staticmethod
    def inquiry_answer_message(inquiry_text, _):
        return Text(
            Bold(_('Write answer for inquiry presented below')), ' ⤵️', '\n',
            '\n',
        ).as_markdown() + inquiry_text
