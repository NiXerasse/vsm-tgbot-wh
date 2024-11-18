from aiogram.utils.formatting import Text, Bold

from database.models import Employee


class AdminMessageBuilder:
    @staticmethod
    def welcome_message(employee: Employee, _):
        return Text(
            '✅ ', Bold(_('Welcome'), ', ', ), '\n',
            '✅ ', Bold(employee.full_name), '\n',
            '✅ ', Bold(_('You\'re in administration mode')),
        ).as_markdown()

    @staticmethod
    def inquiry_answered_message(inquiry_text, _):
        return Text(
            '✅ ', Bold(_('Your reply to inquiry has been sent.')), '\n',
            '✅ ', Bold(_('The inquiry follows below')), '\n',
            '\n'
        ).as_markdown() + inquiry_text

    @staticmethod
    def prompt_for_employee_tab_no_message(_):
        return Text(
            Bold(_('Enter the service number of employee')), ' ⤵️'
        ).as_markdown()

    @staticmethod
    def wrong_tab_no_message(tab_no, _):
        return Text(
            Bold(_('The employee with service number %(tab_no)s is not found') % {'tab_no': tab_no}), '\n',
            _('Enter correct service number'), ' ⤵️'
        ).as_markdown()

    @staticmethod
    def sure_reset_password_message(employee: Employee, _):
        return Text(
            Bold(_('Are you sure you want to reset password for employee?')), '\n',
            '🚹 ', employee.tab_no, '\n',
            '🚹 ', employee.full_name
        ).as_markdown()

    @staticmethod
    def password_was_reset_message(employee: Employee, _):
        return Text(
            Bold(_('The password for employee has been reset successfully')), '\n',
            Bold(_('Employee info'), ':'), '\n',
            '🚹 ', employee.tab_no, '\n',
            '🚹 ', employee.full_name, '\n',
            '\n',
            _('The employee can login by an old PIN'), '\n',
            '🚹 ', _('PIN'), ': ', Bold(employee.pin)
        ).as_markdown()
