# Integrating Weather and Direction Data

The goal of this project was to build an app that utilizes a data pipeline that can show the weather expected to be encountered during a road trip. The user inputs the origin and destination of their road trip. The data pipeline then returns all of the weather from now - arrival time for all of the cities encountered along the way. 

## Design
This project was inspired by my past road trip planning experience. Currently when planning a road trip you have to juggle data from both a weather and directions app to look for weather conditions. Allowing a user to see potential weather they may encounter on their trip can help them plan a road trip with confidence. 

## The Data Pipeline
The data pipeline was built using APIs from two main sources. The pipeline starts with a user input of origin and destination. That data is used to generate an API call to the Google Directions API. The city results from the steps of the directions are then sent to Google's Reverse Geocode API, which collects longitude, latitude pairs that are associated with each city. The longitude, latitude pairs are then sent to the Open Weather Map API. The results from the final API call are then filtered and cleaned to feed into the final App output which displays the post relevant weater conditions for the end user. 

Throughout the pipeline process necessary data is extracted from JSON files, cleaned, and formatted for use in the next step of the pipeline. 

## About the App

The user application was built in streamlit. In the video recording in this repo you can see exactly how the weather app works. 

