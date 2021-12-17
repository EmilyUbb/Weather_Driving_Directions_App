# Getting Weather Data for a Road Trip 
Emily Ubbelohde

## Abstract
The goal of this project was to use a series of API calls to establish a data pipeline that would connect directons and weather data. The data from the last API call in this pipeline was then fed to a Streamlit app for the user. The user inputs their origin and destination to the app, and the app will output weather for the road trip. 


## Design
This project was inspired by my past road trip planning experience. Currently when planning a road trip you have to juggle data from both the weather and directions app to look for weather conditions. Allowing a user to see potential weather they may encounter on their trip can help them plan a road trip with confidence. 

## Data
The data pipeline was built using APIs from two main sources. Directions data was gathered using the google maps directions API. Data gathered from that API was filtered and the latitude, longitude pairs were then fed into the Google Reverse Geo Code API. Data from that API was filtered to get a list of cities. The city names were then fed into the Open Weather API. The data from the final API call was filtered and cleaned to display the most relevant weather conditions for the end user.  

## Algorithms

- API Calls
- Data from the final API call was used to create a Streamlit app  

   
## Tools
- Numpy and Pandas for Data Cleaning and Manipulation
- Google Maps API for Data Gathering
- Open Weather API for Data Gathering
- Streamlit for Production

## Summary
- The app could be improved

## Communication
 - Slides and Visuals Presented
- App Demo Video
