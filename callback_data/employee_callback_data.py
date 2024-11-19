from aiogram.filters.callback_data import CallbackData


class DetailedWhInfoCallback(CallbackData, prefix='detailed_wh_info'):
    month: int
    year: int

class ShowInquiryIdCallback(CallbackData, prefix='show_inquiry_id'):
    inquiry_id: int

class DeleteInquiryIdCallback(CallbackData, prefix='delete_inquiry_id'):
    inquiry_id: int

class DoDeleteInquiryIdCallback(CallbackData, prefix='do_delete_inquiry_id'):
    inquiry_id: int

class AddMessageInquiryCallback(CallbackData, prefix='add_message_inquiry'):
    inquiry_id: int

class RateInfoCallback(CallbackData, prefix='rate_info'):
    ...
