from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_map():
    builder = InlineKeyboardBuilder()
    builder.button(text='Открыть карту 🗺', url='https://t.me/survival_map_bot/map')
    builder.button(text='Поддержать разработчиков', callback_data='support')
    builder.adjust(1)
    return builder.as_markup()


def events():
    builder = InlineKeyboardBuilder()
    builder.button(text='Открыть карту 🗺', url='https://t.me/survival_map_bot/map')
    builder.button(text='Добавить событие', callback_data='add_event')
    builder.button(text='Удалить событие', callback_data='drop_event')
    builder.adjust(1)
    return builder.as_markup()


def event_type():
    builder = InlineKeyboardBuilder()
    builder.button(text='Повестки', callback_data='tickets')
    builder.button(text='Блокпосты', callback_data='blocks')
    builder.button(text='Прочее', callback_data='other')
    builder.adjust(1)
    return builder.as_markup()


def delete_event(events):
    builder = InlineKeyboardBuilder()
    for event_id, description in events:
        builder.button(text=f'{description}', callback_data=f'delete:{event_id}')
        builder.adjust(1)
    return builder.as_markup()
