from aiogram.utils.formatting import Text, Bold
from database.models import Employee


class AuthMessageBuilder:
    @staticmethod
    def enter_pin_message(_):
        return Text(
            '🔘 ', Bold(_("Enter your personal PIN")), ' ⤵️'
        ).as_markdown()

    @staticmethod
    def choose_language_message(_):
        return Text(
            '🔘 ', Bold(_("Choose your language")), ' ⤵️'
        ).as_markdown()

    @staticmethod
    def pin_error_message(_):
        return Text(
            '❌ ', Bold(_('You entered a wrong PIN')), '\n',
            '\n',
            _('Please contact your supervisor to get correct PIN')
        ).as_markdown()

    @staticmethod
    def already_authorized_message(_):
        return Text(
                Bold('❌ ', _('You\'ve already set your password'), '\n'),
                Bold('❌ ', _('Please log in by your username'), '\n')
        ).as_markdown()

    @staticmethod
    def authorization_success_message(employee, _):
        return Text(
            '✅ ', _('Hello'), '\n',
            Bold(employee.full_name), '!\n\n',
            _('Your service number'), ': ', Bold(employee.tab_no), '\n\n',
            _('This is your username, which you will use to log into your personal account.'), '\n\n',
        ).as_markdown()

    @staticmethod
    def edit_password_message(_):
        return Text(_('Now you need to enter new password for your account'), ' ⤵️').as_markdown()

    @staticmethod
    def save_password_message(tab_no, password, _):
        return Text(
            '⁉️ ', Bold(_('Your username')), ': ', Bold(tab_no), '\n',
            '⁉️ ', Bold(_('Your password')), ': ', Bold(password)
        ).as_markdown()

    @staticmethod
    def account_saved_message(_):
        return Text(
            Bold('✅ ', _('Data saved successfully')), '\n',
            _('You can now login by username'), ' ⤵️'
        ).as_markdown()

    @staticmethod
    def enter_login_message(_):
        return Text(
            Bold('🔘 ', _('Please enter your username'), ' ⤵️'),
        ).as_markdown()

    @staticmethod
    def enter_password_message(employee: Employee, _):
        return Text(
            Bold('✅ ', employee.full_name, '\n'),
            Bold('✅ ', employee.tab_no, '\n'),
            '\n',
            '🔘 ', _('Please enter your password'), ' ⤵️'
        ).as_markdown()

    @staticmethod
    def err_wrong_tab_no_message(_):
        return Text(
            Bold('‼️ ', _('You\'ve entered wrong username'), '!\n'),
            '\n',
            Bold('🔘 ', _('Please try again'), ' ⤵️'),
        ).as_markdown()

    @staticmethod
    def enter_password_tab_no_message(tab_no: str, _):
        return Text(
            '✅ ', Bold(_('Username'), ': ', tab_no), '\n',
            '\n',
            '🔘 ', _('Please enter your password'), ' ⤵️'
        ).as_markdown()

    @staticmethod
    def err_wrong_password_message(_):
        return Text(
            Bold('‼️ ', _('You\'ve entered wrong password'), '!\n'),
            '\n',
            Bold('🔘 ', _('Please try again'), ' ⤵️'),
        ).as_markdown()
