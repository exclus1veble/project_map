import folium
import pytz
from aiogram import Bot
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime, timedelta, date
from core.utils.dbconnect import Request

custom_polygon = gpd.read_file("media/OSMB_polygon.geojson")
desired_timezone = 'Europe/Kiev'


async def update(bot: Bot, request: Request):

    Odessa_map = folium.Map(location=[46.4825, 30.7233], zoom_start=12)
    folium.GeoJson(custom_polygon, show=True)

    tickets = folium.FeatureGroup(name='повестки').add_to(Odessa_map)
    blocks = folium.FeatureGroup(name='блокпосты').add_to(Odessa_map)
    other = folium.FeatureGroup(name='прочее').add_to(Odessa_map)
    folium.LayerControl(collapsed=False).add_to(Odessa_map)

    # Загрузка из бд
    events_data = await request.get_events()
    if not events_data:
        print("No events found")

    for events in events_data:
        point = Point(events['longitude'], events['latitude'])
        if custom_polygon.geometry.contains(point).any():
            location = [events['latitude'], events['longitude']]

            pop_up = f"""<strong>{events['time']}</strong>
                                <img src="{events['photo']}" width="200px">
                                <p>{events['description']}</p>
                            """

            event_time_str = events['time']
            event_time = datetime.strptime(event_time_str, '%H:%M:%S').time()

            current_time_str = datetime.now(pytz.timezone(desired_timezone))
            current_time = current_time_str.time()

            diff_time = datetime.combine(date.min, current_time) - datetime.combine(date.min, event_time)
            radius, fill_opacity, fill_color = None, None, None
            # Радиус круа
            if diff_time <= timedelta(minutes=10):
                radius = 200
                fill_opacity = 0.9
                fill_color = 'red'
            elif timedelta(minutes=10) < diff_time <= timedelta(minutes=20):
                radius = 500
                fill_opacity = 0.6
                fill_color = 'red'
            elif timedelta(minutes=20) < diff_time <= timedelta(minutes=30):
                radius = 750
                fill_opacity = 0.3
                fill_color = 'red'

            if events['layer'] == 'tickets':
                folium.Circle(
                    location=location,
                    radius=radius,
                    color='',
                    fill=True,
                    fill_color=fill_color,
                    fill_opacity=fill_opacity,
                    popup=folium.Popup(pop_up, max_width=200)
                ).add_to(tickets)

            elif events['layer'] == 'blocks':
                folium.Marker(
                    location=location,
                    popup=folium.Popup(pop_up, max_width=200),
                    icon=folium.features.CustomIcon('media/blocks.png', icon_size=(30, 30))
                ).add_to(blocks)

            elif events['layer'] == 'other':
                folium.Marker(
                    location=location,
                    popup=folium.Popup(pop_up, max_width=200),
                    icon=folium.Icon(color='blue', icon_color='red')
                ).add_to(other)

    Odessa_map.get_root().header.add_child(folium.Element('''
        <link rel="stylesheet" href="styles.css"/>
    '''))
    Odessa_map.save('index.html')
    print('карта обновлена')
