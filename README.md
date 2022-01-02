# Integrating Weather and Direction Data

The goal of this project was to build an app through a data pipeline that can show the weather expected to be encountered during a road trip. The user inputs the origin and destination of their road trip. The data pipeline then returns all of the weather from now - arrival time for all of the cities encountered along the way. 

## About the Pipeline 

The pipeline starts with a user input of origin and destination. That data is used to generate an API call to the Google Directions API. The city results from the steps of the directions are then sent to Google's Reverse Geocode API, which collects longitude, latitude pairs that are associated with each city. The longitude, latitude pairs are then sent to the Open Weather Map API. The results from the final API call are then formatted to feed into the final App output. 

Throughout the pipeline process necessary data is extracted from JSON files, cleaned, and formatted for use in the next step of the pipeline. 

## About the App

The user application was built in streamlit. In the video recording in this repo you can see exactly how the weather app works. 

