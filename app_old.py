

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

#from datetime import datetime as dt
#import pandas as pd
import sys
#import matplotlib.pyplot as plt
#import seaborn as sns
import numpy as np
import pandas as pd
import datetime
import calendar
import time
#import matplotlib.pyplot as plt
import math
import random

import pickle
from sklearn import ensemble

import plotly.graph_objs as go
import folium

df_crime_valid = pd.read_csv("fullTrainTestCrimeData_validate_v1_weather_by_day.csv")
df_airbnb = pd.read_csv("listings.csv")

hotels = df_airbnb["name"][:10]

def updatemapfolium(df_airbnb, loaded_model, select_name="Sunny Bungalow in the City", select_date="2018-04-01"):
	df_airbnb_pick = df_airbnb[df_airbnb["name"] == select_name]
	df_crime_pick = df_crime_valid[df_crime_valid["DATE"] == select_date]
	#print (df_crime_pick.iloc[0])
	lat = df_airbnb_pick['latitude'].iloc[0]
	long = df_airbnb_pick['longitude'].iloc[0]
	day = datetime.datetime.strptime(select_date,'%Y-%m-%d')
	data = []
	dat = {
		# ["DAY_OF_MONTH","DAY_OF_WEEK_NUM","MONTH","YEAR","Lat","Long"
		#,"Temperature(F)","Humidity(%)","Wind Speed(mph)","Precip.(in)"]
		'Lat': lat,'Long': long,
		'DAY_OF_MONTH':day.day,
		'DAY_OF_WEEK_NUM':day.weekday()+1, # python start with Mon = 0, Sun = 6
		'MONTH':day.month,
		'YEAR':day.year,
		'Temperature(F)' :df_crime_pick['Temperature(F)'].iloc[0],
		'Humidity(%)'    :df_crime_pick['Humidity(%)'].iloc[0],
		'Wind Speed(mph)':df_crime_pick['Wind Speed(mph)'].iloc[0],
		'Precip.(in)'    :df_crime_pick['Precip.(in)'].iloc[0] }
	data += [dat]
	x_valid = pd.DataFrame(data)
	#print (x_valid)
	#predictions = loaded_model.predict(x_valid)
	#print (predictions)
	a = random.uniform(0, 1)



	boston_map_crime = folium.Map(location=[42.321145, -71.057083],
								  zoom_start=11
		     ,tiles="CartoDB dark_matter"
								  )
	radius = 5
	if (a>0.5):
		color = "#FF4500"
	else:
		color = "#7cfc00"
	#color = "#FF4500"
	popup_text = """Latitude : {}<br>
		Longitude : {}<br>
		Name : {}<br>"""
	popup_text = popup_text.format(lat,
								   long,
								   str(str(df_airbnb_pick["name"].iloc[0]))
								   )
	folium.CircleMarker(location = [lat, long], popup= popup_text,radius = radius, color = color, fill = True).add_to(boston_map_crime)
	boston_map_crime.save('plot_data_BOS_update.html')



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
                       html.Div([
                                 html.H1(children='Welcome to StaySafe', style={'textAlign': 'center'}),
                                 
                                 dcc.Dropdown(
                                              id='hotel-name',
                                              options=[{'label': i, 'value': i} for i in hotels],
                                              value='Sunny Bungalow in the City'
                                              ),
                                 
#                                 dcc.Dropdown(
#                                              id='latitude',
#                                              options=[{'label': i, 'value': i} for i in lats],
#                                              value='Default Value For lat'
#                                              ),
#
#                                 dcc.Dropdown(
#                                              id='longitude',
#                                              options=[{'label': i, 'value': i} for i in lngs],
#                                              value='Default Value For long'
#                                              ),
                                 ]),
                       
                       dcc.DatePickerSingle(
                                            id='my-date-picker-single',
                                            min_date_allowed=datetime.datetime(2018, 4, 1),
                                            max_date_allowed=datetime.datetime(2018, 10, 31),
                                            #initial_visible_month=datetime.datetime.today(),
                                            initial_visible_month=datetime.datetime(2018, 4, 1),
                                            #date=str(datetime.datetime.today().date())
                                            date=str(datetime.datetime(2018, 4, 1).date())
                                            ),
                       
                       html.Div(id='result', style={'textAlign': 'center'}),
                      
                       html.Iframe(id='map', srcDoc = open('plot_data_BOS_update.html','r').read(), width='60%', height='400')
                       ])


@app.callback(
              Output('result', 'children'),
              [# list of dash.dependencies Input
               Input('hotel-name', 'value'),
               Input('my-date-picker-single', 'date')
               ]
              )

def update_hotelname(hotel_name, datepick): # the first parameter is the first dash.dependencies Input, and so on
    return 'You pressed "{}"'.format(hotel_name + ". Check in date is " +datepick )


@app.callback(
              Output('map', 'srcDoc'),
              [# list of dash.dependencies Input
			   Input('hotel-name', 'value'),
			   #Input('latitude', 'value'),
			   #Input('longitude', 'value'),
               Input('my-date-picker-single', 'date')
               ]
              )
def update_map(hotel_name, datepick): # the first parameter is the first dash.dependencies Input, and so on
	updatemapfolium(df_airbnb, loaded_model, hotel_name, datepick)
	return open('plot_data_BOS_update.html','r').read()



if __name__ == '__main__':
	loaded_model = pickle.load(open("grad_bdt_classi_2019_06_14.sav", 'rb'))
	app.run_server(debug=True)
