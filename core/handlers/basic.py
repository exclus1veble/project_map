import os
import time
import uuid
import aiohttp
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import geopandas as gpd
from shapely.geometry import Point, Polygon
from core.keyboards.inline import get_map, events, event_type
from core.utils.states import Steps
from core.settings import settings
from core.utils.dbconnect import Request
from core.middlewares.dbmiddleware import DbSession

custom_polygon = gpd.read_file("media/OSMB_polygon.geojson")


async def get_start(message: Message, request: Request):
    url = f'https://api.telegram.org/bot{settings.bots.bot_token}/getChatMember?chat_id={settings.bots.channel_id}&user_id={message.from_user.id}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            # Если пользователь является участником канала
            if data.get('ok') and (data.get('result', {}).get('status') in ['member', 'creator']):
                await message.answer(f'Привет {message.from_user.username}, будь внимателен. Всё в твоих руках',
                                     reply_markup=events())
            # Если пользователь не является участником канала
            else:
                await message.answer(f'Добро пожаловать! Рады Вас видеть, снова', reply_markup=get_map())
                await request.add_user(message.from_user.id, message.from_user.first_name)


async def get_location(message: Message, state: FSMContext):
    point = Point(message.location.longitude, message.location.latitude)
    # если точка входит в полигон
    if custom_polygon.contains(point).all():
        await state.update_data(latitude=message.location.latitude)
        await state.update_data(longitude=message.location.longitude)
        await message.answer('Вы отправили локацию.\n 📸 Добавьте фото (если есть)\n ✍️ Либо введите описание события:')
        await state.set_state(Steps.DESCRIPTION)
    # если точка не входит в полигон
    else:
        await message.answer('🚫 Недопустимые координаты')
        await message.answer(text='🗺 Отправьте локацию события')


async def get_photo(message: Message, state: FSMContext):
    save_photo_path = "media/photos"
    photo = message.photo[-1]
    # Генерируем уникальное имя файла для изображения
    unique_filename = f"photo_{uuid.uuid4()}.jpg"
    photo_path = os.path.join(save_photo_path, unique_filename)
    await state.update_data(photo=photo_path)  # Сохраняем путь к изображению в машине состояний

    # Загружаем изображение в папку media
    file_id = photo.file_id
    file_path = await message.bot.get_file(file_id)
    await message.bot.download_file(file_path.file_path, photo_path)
    await message.answer(f"📸 Фото добавлено.\n ✍️ добавь описание события")
    await state.set_state(Steps.DESCRIPTION)


async def get_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(f'✍️ {message.text} \r\n укажите тип события!', reply_markup=event_type())
    await state.set_state(Steps.TYPE_EVENT)




