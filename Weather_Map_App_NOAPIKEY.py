import streamlit as st
import googlemaps
import requests
#import pymongo
#from pymongo import MongoClient
import json
import pandas as pd
import numpy as np
#import geopy
from geopy.geocoders import GoogleV3
from pandas.io.json import json_normalize
from datetime import *
import re
import gmaps

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
    cities.append(end[0])
        
    cities_df = []
    for i in cities:
        split_1 = i.split(',')
        cities_df.append(split_1)
    for i in cities_df:
        for j in i:
            if '+' in j:
                split_2 = j.split('+')
                for k in split_2:
                    split_3 = k.split(' ')
                cities_df.append(split_3)
    cities_list = []
    for i in cities_df:
        j = i[1].replace(' ','')
        if len(j) > 2:
            cities_list.append(j)
    cities_for_weather = set(cities_list)
    print(cities_for_weather)

    start_location = pd.DataFrame(start_location)
    start_location[0] = "Latitude"
    start_location[1] = "Longitude"
    end_location = pd.DataFrame(end_location)
    
    return(cities_for_weather, duration_int, start_location, end_location)

def weather_data(cities_for_weather, duration_int):
    cities_for_weather = list(cities_for_weather)
    duration_int = duration_int
    
    df = pd.DataFrame(columns=["dt","weather","visibility","pop","dt_txt","main.temp","main.feels_like","main.temp_min",
           "main.temp_max","main.pressure","main.sea_level","main.grnd_level",
           "main.humidity","main.temp_kf","clouds.all","wind.speed","wind.deg",
           "wind.gust","sys.pod","rain.3h"])
    
    headers = []
    idx = 0
    result= []
    for i in cities_for_weather:
        i =  re.sub(r"(\w)([A-Z])", r"\1 \2", i)
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
    

    main = pd.DataFrame(main)
    main = main.reset_index()
    main.drop(main.columns[0],axis=1,inplace=True)
    
    description = pd.DataFrame(description)
    description = description.reset_index()
    description.drop(description.columns[0],axis=1,inplace=True)
    

    final_df = pd.DataFrame([])
    final_df = df[["name","visibility","dt_txt","main.temp","wind.speed","wind.gust","rain.3h"]]
    

    final_df = final_df.merge(main, left_index=True, right_index=True, how='left')
    final_df = final_df.merge(description, left_index=True, right_index=True, how='left')


    final_df.columns.values[0] = "Name"
    final_df.columns.values[1] = "Visibility"
    final_df.columns.values[2] = "Date + Time"
    final_df.columns.values[3] = "Temp"
    final_df.columns.values[4] = "Wind Speed"
    final_df.columns.values[5] = "Wind Gust"
    final_df.columns.values[6] = "Chance of Rain for 3 Hours"
    final_df.columns.values[7] = "Weather Category"
    final_df.columns.values[8] = "Weather Description"
    final_df = pd.DataFrame(final_df)

    
    
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
    wind_data = weather_by_hr[["Name","Date + Time","Wind Speed","Wind Gust"]]
    weather_description = weather_by_hr[["Name","Date + Time","Weather Category","Weather Description"]]
    visibility_rain = weather_by_hr[["Name","Date + Time","Visibility","Chance of Rain for 3 Hours"]]
    
    return(weather_by_hr, wind_data, weather_description, visibility_rain)

st.title('Showing Weather Conditions for a Road Trip')

st.write('''
    # Trip Origin''')
Origin = st.text_input('Origin: 123 Street Name, City, State', value="2930 T Street, Lincoln, NE")
st.write('''
    # Trip Destination''')
Destination = st.text_input('Destination: 123 Street Name, City, State', value="6349 Granite Dr NW, Rochester, MN")
output = direction_data(Origin,Destination)
final_out = weather_data((output[0]),(output[1]))

st.write('''
    # All Weather Data''')
st.dataframe(data=final_out[0], width=800, height=800)
st.write('''
    # Weather Description''')
st.dataframe(final_out[2])
st.write('''
    # Wind Data''')
st.dataframe(final_out[1])
st.write('''
    # Visibility and Chance of Rain''')
st.dataframe(final_out[3])

