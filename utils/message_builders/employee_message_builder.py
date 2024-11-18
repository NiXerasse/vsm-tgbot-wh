from aiogram.utils.formatting import Text, Bold

from database.models import Employee, Inquiry


class EmployeeMessageBuilder:
    @staticmethod
    def welcome_message(employee: Employee, _):
        return Text(
        '\u200B', '\n'
            '✅ ', Bold(_('Welcome')), ', \n',
            '✅ ', Bold(employee.full_name), '\n',
            '\u200B',
        ).as_markdown()

    @staticmethod
    def wh_info_message(employee: Employee, target_month_str: str, target_year: int, _):
        return Text(
            '🚹 ', Bold(employee.full_name), '\n',
            '🚹 ', Bold(employee.tab_no), '\n',
            '🚹 ', Bold(_('Data for'), ' ', target_month_str.capitalize(), '\'', target_year % 100), '\n',
            '\n',
        ).as_markdown()

    @staticmethod
    def wh_info_subdivision(wh_stat, _):
        return Text(
            '✅ ', Bold(wh_stat['subdivision_name'], ': '), '\n',
            ' 🔘 ', _('Number of days worked'), ': ', wh_stat['count_nonzero'], '\n',
            ' 🔘 ', _('Accounted hours'), ': ', wh_stat['sum_total'],
            '\n',
        ).as_markdown()

    @staticmethod
    def inquiries_message(inquiries, _):
        return EmployeeMessageBuilder._inquiries(inquiries, _) if inquiries else EmployeeMessageBuilder._no_inquiries(_)

    @staticmethod
    def _no_inquiries(_):
        return Text(
            '🚹 ', _('Here you can write an inquiry regarding employment relations and workflow.'), '\n',
            '\n',
            ' 🔘 ', _('You have no inquiries yet.'), '\n'
        ).as_markdown()

    @staticmethod
    def _inquiries(inquiries, _):
        inquiries_message = Text('🚹 ', Bold(_('Your inquiries'), ': '), '\n\n').as_markdown()

        inquiries_message += ''.join(
            EmployeeMessageBuilder._inquiry(no, inquiry)
            for no, inquiry in enumerate(inquiries, start=1)
        )

        inquiries_message += Text(
            '\n\n',
            Bold('🚹 ', _('To work with inquiry press a button with corresponding number below'), ' ⤵️', '\n')
        ).as_markdown()

        return inquiries_message

    @staticmethod
    def _inquiry(no, inquiry):
        bullet = ' 🟢 ' if inquiry.status == 'answered' else ' 🔘 ' if inquiry.status == 'closed' else ' 🟣 '
        return Text(
            bullet, f'{no}. ', Bold(inquiry.subject), '\n',
        ).as_markdown()

    @staticmethod
    def inquiry_message(inquiry, _):
        inquiry_message = EmployeeMessageBuilder._inquiry_message_header(inquiry, _)

        inquiry_message += ''.join(
            EmployeeMessageBuilder._inquiry_message_body(msg, inquiry.employee_id, _)
            for msg in sorted(inquiry.messages, key=lambda m: m.id)
        )

        return inquiry_message

    @staticmethod
    def _inquiry_message_header(inquiry, _):
        return Text(
            Bold(inquiry.employee.full_name), '\n',
            Bold(inquiry.employee.tab_no), '\n',
            Bold(_('SD'), ' "', inquiry.subdivision.name, '"'), '\n',
            '\n',
            Bold(_('Topic'), ': ', inquiry.subject), '\n',
            '\n'
        ).as_markdown()

    @staticmethod
    def _inquiry_message_body(msg, initiator, _):
        icon = ' ❓ ' if msg.employee_id == initiator else ' ✅ '
        return Text(
            Bold(_('Date'), ': ', msg.sent_at.strftime('%d-%m-%y %H:%M')), '\n',
            icon, msg.content, '\n\n'
        ).as_markdown()

    @staticmethod
    def sure_delete_inquiry_message(inquiry, _):
        return Text(
            Bold('⁉️ ', _('The inquiry'), ': ', '\n\n'),
            Bold('⁉️', inquiry.subject), '\n\n',
            Bold('⁉️ ', _('will be deleted'), '!', '\n')
        ).as_markdown()

    @staticmethod
    def enter_text_message(inquiry: Inquiry, _):
        return Text(
            Bold('🚹 ', _('Enter a text for your inquiry with topic'), ': ⤵️'),
            '\n\n',
            Bold(' 🟣 ', inquiry.subject),
        ).as_markdown()

    @staticmethod
    def being_added_message(inquiry: Inquiry, content: str, _):
        return Text(
            '🚹 ', _('You are adding the message to the inquiry with topic'), ': ', '\n',
            Bold(' 🟣 ', inquiry.subject), '\n\n',
            Bold('🚹 ', _('Content of the message'), ': '), '\n',
            ' 🔘 ', content, '\n'
        ).as_markdown()

    @staticmethod
    def enter_inquiry_head_message(_):
        return Text(
            Bold('🚹 ', _('Enter a topic for your inquiry.')),
            '\n\n',
            _('It will be displayed in the list of requests, so it should be brief and meaningful.'), ' ⤵️', '\n'
        ).as_markdown()

    @staticmethod
    def enter_inquiry_body_message(inquiry_head, _):
        return Text(
            '🚹 ', Bold(_('Enter the text for the inquiry with topic')), ': ', '\n',
            '\n',
            ' 🟣 ', Bold(inquiry_head), ' ⤵️', '\n'
        ).as_markdown()

    @staticmethod
    def inquiry_text_message(inquiry_head, inquiry_body):
        return Text(
            '✅ ', Bold(inquiry_head), '\n\n',
            ' 🟣 ', inquiry_body, '\n'
        ).as_markdown()

    @staticmethod
    def rate_info_message(_):
        return Text(
            Bold(_('Dear Employees')), ', \n'
            '\n',
            _('Please be advised that information regarding your hourly rate is confidential and is not provided through our corporate Telegram bot.'), '\n',
            '\n',
            _('To obtain details about your hourly rate, you may contact the Labor and Payroll Department. The department specialists are ready to answer your questions and provide the necessary information in accordance with existing corporate procedures.'), '\n',
            '\n',
            _('Thank you for your understanding and for maintaining confidentiality.')
        ).as_markdown()
