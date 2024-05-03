from datetime import datetime

import pytz
from aiogram import Bot
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from core.keyboards.inline import events, event_type, delete_event
from core.utils.dbconnect import Request
from core.middlewares.dbmiddleware import DbSession
from core.utils.states import Steps

desired_timezone = 'Europe/Kiev'  # Укажите желаемый часовой пояс


async def catch_event(call: CallbackQuery, state: FSMContext):
    
    if call.data == 'add_event':
        await call.message.answer(text='🗺 Отправьте локацию события')
        await state.set_state(Steps.LOCATION)
        await call.answer()
        
    elif call.data == 'support':
        image_path = 'media/support.jpg'
        toncoin = ''
        caption='Поддержите разработчиков USDT (TRC20)'
        await call.message.answer_photo(photo=types.FSInputFile(path=image_path), caption=caption)
    
    elif call.data == 'drop_event':
        await call.message.edit_text(text='Выберите категорию в которой хотите удалить событие', reply_markup=event_type())
        await state.set_state(Steps.EDIT_EVENT)


async def type_event(call: CallbackQuery, state: FSMContext, bot: Bot, request: Request):
    if call.data not in ('tickets', 'blocks', 'other'):
        await call.message.answer(text='error')
        await state.clear()
        return
    await call.message.answer(text=f'Событие отмечено на карте ({call.data})', reply_markup=events())
    await state.update_data(layer=call.data)

    context_data = await state.get_data()
    time = datetime.now(pytz.timezone(desired_timezone)).strftime("%Y-%m-%d %H:%M:%S")
    latitude = float(context_data.get("latitude"))
    longitude = float(context_data.get("longitude"))
    description = context_data.get('description')
    photo = context_data.get('photo', 'media/nophoto.jpg')
    layer = context_data.get('layer')

    await request.add_event(time, latitude, longitude, description, photo, layer)
    await state.set_state(Steps.LOCATION)
    await request.send_notification(bot=bot, message_text=description)


async def choose_event(call: CallbackQuery, state: FSMContext, request: Request):
    events = await request.fetch_events(call.data)
    if not events:
        await call.message.answer('В базе данных нет событий для выбранной категории.')
        return
    await call.message.edit_reply_markup(f'Выберите событие для удаления из категории "{call.data}":',
                              reply_markup=delete_event(events))
    await state.set_state(Steps.DROP_EVENT)


async def deletion_callback(call: CallbackQuery, state: FSMContext, request: Request):
    action, event_id = call.data.split(':')
    if action == 'delete':
        try:
            await request.delete_event(event_id)
            await call.message.answer(f'Событие с ID {event_id} было удалено.', reply_markup=events())
        except Exception as e:
            await call.message.answer(f'Произошла ошибка при удалении события: {e}')
        finally:
            await state.clear()
            await call.message.delete()



