import streamlit as st
import googlemaps
import requests
import json
import pandas as pd
import numpy as np
import geopy
from geopy.geocoders import GoogleV3
from pandas.io.json import json_normalize
from datetime import *
import re
import gmaps
from IPython.display import Image


def direction_data(origin,destination):

    origin = origin
    destination = destination
    url = "https://maps.googleapis.com/maps/api/directions/json?origin="+origin+"&destination="+destination+"&key={API KEY}"


    payload={}
    headers = {}

    direct = requests.request("GET", url, headers=headers, data=payload)
    text = direct.text
    data = json.loads(text)
    direct_df = pd.json_normalize(data['routes'][0]['legs'][0]['steps'])

    total_trip = pd.json_normalize(data['routes'][0]['legs'])

    latitudes = []
    longitudes = []
    start_location = []
    end_location = []
    duration = []

    start_location.append(total_trip['start_location.lat'][0])
    start_location.append(total_trip['start_location.lng'][0])
    end_location.append(total_trip['end_location.lat'][0])
    end_location.append(total_trip['end_location.lng'][0])
    duration.append(total_trip['duration.text'][0])
    
    duration = ' '.join(duration)
    numeric_filter = filter(str.isdigit, duration)
    numeric_string = "".join(numeric_filter)
    duration= pd.to_datetime(numeric_string, format = '%H%M')
    duration_int = str(duration)
    duration_int = duration_int.split(' ') 
    duration_int = duration_int[1].split(':')
    duration_int = duration_int[0]
    duration_int = int(duration_int)
    

    for direct_df_row in direct_df.itertuples():
        latitudes.append(direct_df['end_location.lat'])
        longitudes.append(direct_df['end_location.lng'])
        
    def lat_lng_pairs(latitudes, longitudes):
        locations= tuple(zip(latitudes[1], longitudes[1]))
        return locations
    
    locations = lat_lng_pairs(latitudes, longitudes)
    
    cities = []
    geolocator = GoogleV3(api_key='{API KEY}')
    
    
    start = geolocator.reverse(start_location)
    cities.append(start[0])

    
    for i in locations:
        c = geolocator.reverse(i)
        if c:
            cities.append(c[0]) 
    
    end = geolocator.reverse(end_location)
    cities.append(end[-1])
    
    cities_df = []
    cities_final = []
    states_df = []
    states_final = []
    for i in cities:
        city = []
        split_1 = str(i).split(',')
        split = split_1[1].strip()
    
        if len(split) > 2:
            city = split
            try:
                state = split_1[2]
                if(str(city)) not in cities_df:
                    cities_df.append(str(city))
                    states_df.append(str(state))
            except IndexError:
                print('end of cities')
        else:
            city = split_1[0]
            state = split
            if(str(city)) not in cities_df:
                cities_df.append(str(city))
                states_df.append(str(state))
    for i in cities_df:
        if '+' in str(i):
            split_2 = str(i).split(' ',1)
            final_split = split_2[1]
            cities_final.append(final_split)
        else:
            cities_final.append(i)
    for i in states_df:
        if len(i) > 2:
            split = str(i).split(' ',2)
            final_split = split[1]
            states_final.append(final_split)
        else:
            states_final.append(i)
    return(cities_final, duration_int,states_final)

def city_state(cities_list,states_list):
    locations = tuple(zip(cities_list,states_list))
    return locations


def weather_data(cities_final, duration_int):
    cities_for_weather = cities_final
    duration_int = duration_int

    
    df = pd.DataFrame(columns=["dt","weather","visibility","pop","dt_txt","main.temp","main.feels_like","main.temp_min",
           "main.temp_max","main.pressure","main.sea_level","main.grnd_level",
           "main.humidity","main.temp_kf","clouds.all","wind.speed","wind.deg",
           "wind.gust","sys.pod","rain.3h"])
    
    headers = []
    idx = 0
    result= []
    for i in cities_for_weather:
        url = 'http://api.openweathermap.org/data/2.5/forecast?q='+i+'&units=imperial&appid={API KEY}'
        response2 = (requests.request("GET", url, headers=headers)).text
        data2 = json.loads(response2)
        try:
            holder = (pd.DataFrame(pd.json_normalize(data2['list'])))
            city_holder = (pd.DataFrame(pd.json_normalize(data2['city'])))
            holder = holder.assign(name = city_holder['name'][0])
            result.append(holder)
        except KeyError:
            print(f'City {i} not found')
        
    
    df = df.append(result)
    df = df.reset_index()
    df["dt_txt"] = pd.to_datetime(df["dt_txt"])
    
    df_weather =  (pd.concat([pd.DataFrame(x) for x in df['weather']], axis=1)
            .stack(0)
            .reset_index(level=1, drop=True))
    
    main = df_weather.iloc[1::4]
    description = df_weather.iloc[2::4]
    icon = df_weather.iloc[3::4]



    main = pd.DataFrame(main)
    main = main.reset_index()
    main.drop(main.columns[0],axis=1,inplace=True)
    
    description = pd.DataFrame(description)
    description = description.reset_index()
    description.drop(description.columns[0],axis=1,inplace=True)

    icon = pd.DataFrame(icon)
    icon = icon.reset_index()
    icon.drop(icon.columns[0],axis=1,inplace=True)
    

    final_df = pd.DataFrame([])
    final_df = df[["name","visibility","dt_txt","main.temp","wind.speed","wind.gust","rain.3h"]]

    final_df = final_df.merge(main, left_index=True, right_index=True, how='left')
    final_df = final_df.merge(description, left_index=True, right_index=True, how='left')
    final_df = final_df.merge(icon, left_index=True, right_index=True, how='left')



    final_df.columns.values[0] = "Name"
    final_df.columns.values[1] = "Visibility"
    final_df.columns.values[2] = "Date + Time"
    final_df.columns.values[3] = "Temp"
    final_df.columns.values[4] = "Wind Speed"
    final_df.columns.values[5] = "Wind Gust"
    final_df.columns.values[6] = "Chance of Rain for 3 Hours"
    final_df.columns.values[7] = "Weather Category"
    final_df.columns.values[8] = "Weather Description"
    final_df.columns.values[9] = "Icon"

    final_df['Icon'] = final_df['Icon'].astype(str) +'.png'
    
    def display_rows(final_df, duration_int):
        hr_blocks = ((duration_int)/3)
        hr_blocks = int(hr_blocks)
        number_cities = (len(final_df)/40)
        number_cities = int(number_cities)
        weather_data = []
        accum = 0
        final_df = pd.DataFrame(final_df)
        for i in (range(number_cities)):
            end = (hr_blocks+accum)
            holder = final_df.loc[accum:end]
            holder = pd.DataFrame(holder)
            accum += 40
            weather_data.append(holder)    
        return(weather_data)
            
    
    weather_by_hr = pd.concat(display_rows(final_df,duration_int))
    icon = weather_by_hr["Icon"].to_list()
    cities = weather_by_hr["Name"].to_list()
    time = weather_by_hr["Date + Time"].to_list()
    time = [str(date) for date in time]
    windgust = weather_by_hr["Wind Gust"].to_list()
    windspeed = weather_by_hr["Wind Speed"].to_list()
    visibility = weather_by_hr["Visibility"].to_list()
    rain = weather_by_hr["Chance of Rain for 3 Hours"].to_list()
    weathershort = weather_by_hr["Weather Category"].to_list()
    weatherlong = weather_by_hr["Weather Description"].to_list()
    
    return(icon,cities,time,weathershort,weatherlong,windgust,windspeed,visibility,rain)

st.set_page_config(layout="wide")
st.title('Showing Weather Conditions for a Road Trip')

st.write('''
    # Trip Origin''')
Origin = st.text_input('Origin: 123 Street Name, City, State', value="2930 T Street, Lincoln, NE")
st.write('''
    # Trip Destination''')
Destination = st.text_input('Destination: 123 Street Name, City, State', value="6349 Granite Dr NW, Rochester, MN")
    
output = direction_data(Origin,Destination)
final_out = weather_data((output[0]),(output[1]))
locations = city_state((output[0]),(output[2]))


icons = final_out[0]
date = final_out[2]
weathershort = final_out[3]
weatherlong = final_out[4]
windgust = final_out[5]
windspeed = final_out[6]
visibility = final_out[7]
rain = final_out[8]
cities = final_out[1] 
st.write('''
    # Weather Description''')
col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
with col1:
    col1.subheader("Date + Time")
    for i in (date): 
        col1.write(i)
with col2:
    col2.subheader("City")
    for i in (cities): 
        col2.write(i)
with col3:
    col3.subheader("Weather Category")
    for i in (weathershort): 
        col3.write(i)
with col4:
    col4.subheader("Icon")
    for idx, img in enumerate(icons): 
        col4.image(icons[idx], width = 25)
        idx+=1
with col5:
    col5.subheader("Weather Description")
    for i in (weatherlong): 
        col5.write(i)

st.write('''
    # Weather Details''')
col1, col2, col6, col7, col8, col9 = st.columns([1,1,1,1,1,1])
with col1:
    col1.subheader("Date + Time")
    for i in (date): 
        col1.write(i)
with col2:
    col2.subheader("City")
    for i in (cities): 
        col2.write(i)
with col6:
    col6.subheader("Wind Speed")
    for i in (windspeed): 
        col6.write(str(i)+' MPH')        
with col7:
    col7.subheader("Wind Gust")
    for i in (windgust): 
        col7.write(str(i)+' MPH')        
with col8:
    col8.subheader("Visibility")
    for i in (visibility): 
        col8.write(str(i))        
with col9:
    col9.subheader("Chance of Rain")
    for i in (rain):
        if str(i) == 'nan':
            col9.write('0%')
        else:
            col9.write(str(i)+'%')
