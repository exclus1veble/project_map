import psycopg_pool
from aiogram import Bot
from core.keyboards.inline import get_map


class Request:
    def __init__(self, connector: psycopg_pool.AsyncConnectionPool.connection):
        self.connector = connector

    # Добавляет пользователя в базу данных (если его там нет) или обновляет имя пользователя.
    async def add_user(self, user_id, user_name):
        query = (f"CREATE TABLE IF NOT EXISTS datausers (user_id BIGINT PRIMARY KEY, user_name VARCHAR(255));"
                 f"INSERT INTO datausers (user_id, user_name) VALUES ({user_id}, '{user_name}') " 
                 f"ON CONFLICT (user_id) DO UPDATE SET user_name='{user_name}'")
        await self.connector.execute(query)

    # Добавляет событие в базу данных
    async def add_event(self, time, latitude, longitude, description, photo, layer):
        connection = self.connector.connection
        async with connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id SERIAL PRIMARY KEY,
                    t1me TIMESTAMP,
                    latitude FLOAT,
                    longitude FLOAT,
                    description TEXT,
                    photo TEXT,
                    layer TEXT
                );
                """
            )
            await connection.execute(
                """
                INSERT INTO events (t1me, latitude, longitude, description, photo, layer)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (time, latitude, longitude, description, photo, layer)  # Pass parameters as a tuple
            )

    # Получает список событий на текущую дату
    async def get_events(self):
        try:
            query = ("SELECT t1me, latitude, longitude, description, photo, layer FROM events WHERE DATE(t1me) = "
                     "CURRENT_DATE;")
            events_list = []

            async with self.connector.connection() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(query)
                    rows = await cursor.fetchall()
                    for row in rows:
                        events = {
                            "time": row[0].strftime('%H:%M:%S'),
                            "latitude": float(row[1]),
                            "longitude": float(row[2]),
                            "description": str(row[3]),
                            "photo": str(row[4]),
                            "layer": str(row[5])
                        }
                        events_list.append(events)
            return events_list
        except Exception as e:
            print(f"Error while fetching events: {e}")
            return []

    # Отправляет уведомление о новом событии всем пользователям
    async def send_notification(self, message_text: str, bot: Bot):
        async with self.connector.connection as connection:
            async with connection.cursor() as cursor:
                await cursor.execute('SELECT user_id FROM datausers')
                async for row in cursor:
                    chat_id = row[0]
                    try:
                        await bot.send_message(chat_id=chat_id, text=message_text, reply_markup=get_map())
                    except Exception as e:
                        print(f"Failed to send a message to user {chat_id}: {e}")

    # Выводит список событий по категории
    async def fetch_events(self, layer):
        async with self.connector as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT id, description FROM events WHERE layer = %s AND DATE(t1me) = CURRENT_DATE;", (layer,))
                return await cursor.fetchall()

    # Удаляет событие по ID
    async def delete_event(self, event_id):
        async with self.connector as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('DELETE FROM events WHERE id = %s;', (event_id,))
                await conn.commit()

    async def close(self):
        self.connector.close()
        await self.connector.wait_closed()
