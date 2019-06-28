
import os
from random import randint

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

#import us
#import plotly
import plotly.graph_objs as go
import pickle
from joblib import load
#import folium
#from app import app
from sklearn import ensemble

#from datetime import datetime as dt
#import matplotlib.pyplot as plt
#import seaborn as sns
import numpy as np
import pandas as pd
import datetime
import calendar
import time
import math
import random

import urllib
import json

import flask

import dash_table


#loaded_model = load('grad_bdt_classi_tuned_2019_06_25_pipe.joblib')
loaded_model = load('grad_bdt_classi_police_2019_06_27_pipe.joblib')

mapbox_access_token = "pk.eyJ1IjoiYWhvcnRpYW4iLCJhIjoiY2p4MDZ5OG9hMW5wNzQ4bXpubTBsd2V6aSJ9.Jl9LiYDTuE7ywfLTINQHKw"

# dataset needed
#df_crime_valid = pd.read_csv("fullTrainTestCrimeData_validate_v1_weather_by_day.csv")
df_airbnb = pd.read_csv("listings.csv")

df_policeStat = pd.read_csv("Boston_Police_Stations.csv")
df_mbta = pd.read_csv("MBTA_Rapid_Transit_Stops.csv")

hotels = df_airbnb["name"][:20]
#address = df_airbnb["name"][:20]
districts = {"Downtown", "Charlestown", "East Boston", "Roxbury",
	"Mattapan", "South Boston", "Dorchester", "South End",
		"Brighton", "West Roxbury", "Jamaica Plain", "Hyde Park"}

#neighbourhoods = ['Downtown Crossing', 'Downtown', 'Chinatown', 'East Boston', 'Roxbury',
#				 'Mattapan', 'South Boston', 'Dorchester', 'South End', 'West Roxbury'
#				 , 'Jamaica Plain', 'Hyde Park']

neighbourhoods = ['Downtown', 'Chinatown', 'East Boston', 'Roxbury',
				  'Mattapan', 'South Boston', 'Dorchester', 'South End', 'West Roxbury'
				  , 'Jamaica Plain', 'Hyde Park','Brighton','Charlestown']


#neighbourhoods_notsure = ['Roslindale',  'Mission Hill', 'Fenway/Kenmore',
#				 'Back Bay', 'Leather District',   'North End',
#				 'Charlestown', 'West End', 'Beacon Hill', 'Theater District',
#				  'Financial District', 'Government Center',
#				 'Allston-Brighton' , 'Chestnut Hill',
#				 'Brookline', 'Cambridge' ,'Somerville' ,'Harvard Square']

#'Downtown'
#'Chinatown'
#'East Boston'
#'Roxbury'
#'Mattapan'
#'South Boston'
#'Dorchester'
#'South End'
#'West Roxbury'
#'Jamaica Plain'
#'Hyde Park'

#new_list_neighbour = [, , 'Roslindale', , 'Back Bay',
# 'North End', , , ,
# , 'Fenway', 'Mission Hill', 'Beacon Hill', 'Allston',
#  , , 'Bay Village',
# 'South Boston Waterfront', 'West End', , ,
# , 'Leather District', 'Longwood Medical Area']

theme = {
	'font-family': 'Raleway',
	'background-color': '#787878',
}
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


###----------------------------------------------------###
###----------------------------------------------------###
def get_shortest_dist_police(lat, lng, df_policeStat):
	min_dist = 1000
	for p in range(df_policeStat.shape[0]):
		pol_lng = df_policeStat["X"].iloc[p]
		pol_lad = df_policeStat["Y"].iloc[p]

		y_dist = abs(pol_lad-lat) *(111/1.60934)
		x_dist = abs(pol_lng-lng) *(111/1.60934)
		dist = math.sqrt((y_dist**2) + (x_dist**2))
		if dist < min_dist:
			min_dist = dist
	return min_dist


def get_weather_info(date_request):
	darksky_apikey = 'b4510e4f9d75ac1e308efd5fdbd97a21'
	url_txt = 'https://api.darksky.net/forecast/'
	url_txt += darksky_apikey
	url_txt += '/42.3601,-71.0589,'
	url_txt += date_request
	url_txt += 'T00:00:00'
		
	json_obj = urllib.request.urlopen(url_txt)
	data = json.load(json_obj)
	#data['hourly']['data'][0]

	hours = []
	temps = []
	humids = []
	wndsps = []
	pcips = []
	for hrly_dat in data['hourly']['data']:
		dat_req = datetime.datetime.fromtimestamp(hrly_dat['time']).date()
		hr = datetime.datetime.fromtimestamp(hrly_dat['time']).hour
		tem = hrly_dat['temperature']
		hum = hrly_dat['humidity'] *100
		wndSp = hrly_dat['windSpeed']
		pciInt = hrly_dat['precipIntensity']

		hours += [hr]
		temps += [tem]
		humids += [hum]
		wndsps += [wndSp]
		pcips += [pciInt]
		#print (date_req, hr, tem, hum,wndSp, pciInt)
	
	g1 = {"hr_grp":1,
		"temp" :np.average(temps[0:8]),
		"humid":np.average(humids[0:8]),
		"wndsp":np.average(wndsps[0:8]),
		"pcip" :np.average(pcips[0:8]),
		}
	g2 = {"hr_grp":2,
		"temp" :np.average(temps[8:16]),
		"humid":np.average(humids[8:16]),
		"wndsp":np.average(wndsps[8:16]),
		"pcip" :np.average(pcips[8:16]),
			}
	g3 = {"hr_grp":3,
		"temp" :np.average(temps[16:24]),
		"humid":np.average(humids[16:24]),
		"wndsp":np.average(wndsps[16:24]),
		"pcip" :np.average(pcips[16:24]),
			}
	output = [g1,g2,g3]
	return output


def is_crime_occur(df_airbnb, loaded_model, df_policeStat, df_mbta, select_name="One Bedroom Studio Garden Apartment", select_date="2019-07-20"):
	df_airbnb_pick = df_airbnb[df_airbnb["name"] == select_name]
	#df_crime_pick = df_crime_valid[df_crime_valid["DATE"] == select_date]
	#print (df_crime_pick.iloc[0])
	lat = df_airbnb_pick['latitude'].iloc[0]
	long = df_airbnb_pick['longitude'].iloc[0]
	day = datetime.datetime.strptime(select_date,'%Y-%m-%d')

	dist_closest_police = get_shortest_dist_police(lat, long, df_policeStat)
	dist_closest_mbta = get_shortest_dist_police(lat, long, df_mbta)

	# real weather data  from API
	#w_data = get_weather_info(select_date)
	
	# const weather data for testing
	w_data = [{'hr_grp': 1, 'temp': 68.78375000000001, 'humid': 79.875, 'wndsp': 5.2212499999999995, 'pcip': 0.009625}, {'hr_grp': 2, 'temp': 75.4225, 'humid': 66.125, 'wndsp': 7.51875, 'pcip': 0.00825}, {'hr_grp': 3, 'temp': 75.185, 'humid': 66.375, 'wndsp': 6.9087499999999995, 'pcip': 0.00875}]
	#print (w_data[1])
	
	a = []
	for i in [0,1,2]:
		data = {
			# ["DAY_OF_MONTH","DAY_OF_WEEK_NUM","MONTH","YEAR","Lat","Long"
			#,"Temperature(F)","Humidity(%)","Wind Speed(mph)","Precip.(in)"]
			
		
		
		'Hour_Grp':[i+1],
		'DAY_OF_MONTH':[day.day],
		'DAY_OF_WEEK_NUM':[day.weekday()+1], # python start with Mon = 0, Sun = 6
		'MONTH':[day.month],
		'YEAR':[day.year],
		'Lat':[lat],
		'Long':[long],
		'Temperature(F)':[w_data[i]['temp']],
		'Humidity(%)':[w_data[i]['humid']],
		'Wind Speed(mph)':[w_data[i]['wndsp']],
		'Precip.(in)':[w_data[i]['pcip']]
				#	'Temperature(F)':[df_crime_pick['Temperature(F)'].iloc[0]],
				#	'Humidity(%)':[df_crime_pick['Humidity(%)'].iloc[0]],
				#	'Wind Speed(mph)':[df_crime_pick['Wind Speed(mph)'].iloc[0]],
				#	'Precip.(in)':[df_crime_pick['Precip.(in)'].iloc[0]]
			}
		# Create DataFrame
		x_valid = pd.DataFrame(data)
		#print (x_valid)
		#predictions = loaded_model.predict(x_valid)
		predictions = loaded_model["model"].predict(x_valid)
		#print (predictions)
		##a = random.uniform(0, 1)
		a += [predictions[0]]
	return a, lat, long

#	boston_map_crime = folium.Map(location=[42.321145, -71.057083],
#								  zoom_start=11
#		     ,tiles="CartoDB dark_matter"
#								  )
#	radius = 5
#	if (a>0.5):
#		color = "#FF4500"
#	else:
#		color = "#7cfc00"
#	#color = "#FF4500"
#	popup_text = """Latitude : {}<br>
#		Longitude : {}<br>
#		Name : {}<br>"""
#	popup_text = popup_text.format(lat,
#								   long,
#								   str(str(df_airbnb_pick["name"].iloc[0]))
#								   )
#	folium.CircleMarker(location = [lat, long], popup= popup_text,radius = radius, color = color, fill = True).add_to(boston_map_crime)
#	boston_map_crime.save('plot_data_BOS_update.html')

###----------------------------------------------------###
###----------------------------------------------------###

def create_header():
	header = html.Div([
			  html.H1(children='Welcome to SafeGetaway', style={'textAlign': 'center'}),
			  html.P(children='Pick an Airbnb and a date. See if a crime will occur ! ', style={'textAlign': 'center'})
			  
			  ])
	return header


def create_dropdown_dist(id_name):
	dropdown = html.Div([
						 
						 html.Div(children='Choose Neighbourhood', id='top-of-dropdown-dist'),
						 dcc.Dropdown(
									  id=id_name,
									  options=[{'label': i, 'value': i} for i in neighbourhoods],
									  value='Jamaica Plain'
									  ),
						 
						 ], className= 'three columns',
						#style={'display': 'inline-block'}
						 )
						 #],className='two columns'),
	return dropdown


def create_dropdown_hotel(id_name):
	
	dropdown = html.Div([
			  
			  html.Div(children='Choose Airbnb', id='top-of-dropdown-hotel'),
			  dcc.Dropdown(
						   id=id_name,
						   #options=[{'label': i, 'value': i} for i in hotels],
						   value='One Bedroom Studio Garden Apartment'
						   ),
			  
			  ], className='five columns',
				 style={'display': 'inline-block'}
			   )
			  #],className='two columns'),
	return dropdown


def create_calendar(id_name):
	label = 'Choose Date'
	if id_name.find("out")>0:
		label = 'Checkout'
	calendar = html.Div([
						 
			  html.Div(children=label, id=label, style={'textAlign': 'center'}),
			  dcc.DatePickerSingle(
								   id=id_name,
								   min_date_allowed=datetime.datetime.today(),
								   max_date_allowed=datetime.datetime(2019, 12, 31),
								   initial_visible_month=datetime.datetime.today(),
								   date=str(datetime.datetime.today().date())
								   ),
						 
						 ], className='two columns',
						#style={'display': 'inline-block'}
						)
	return calendar


def create_content(id_name):
	# create empty figure. It will be updated when _update_graph is triggered
	graph = dcc.Graph(id=id_name)
	content = html.Div(graph, id='content', className='eight columns' )
	return content


def creat_searchbar(id_name):
	# Column: Input Bar
	searchbar = html.Div([
					 html.P([
							 html.B("Filter the titles:  "),
							 dcc.Input(
									   placeholder="Try 'heard'",
									   id=id_name,
									   value='')
							 ]),
					 ], className='six columns')
	return searchbar





## main app code
app_name = 'Dash StaySafe'
server = flask.Flask(app_name)
#server = flask.Flask(__name__)

#server.secret_key = os.environ.get("SECRET_KEY", "secret")
#server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
server.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')

#app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)
#app = dash.Dash(__name__, server=server,)
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(name=app_name, server=server, external_stylesheets=external_stylesheets)

#config.assets.compress = True
#server = app.server


app.layout = html.Div(
					  children=[
								
							create_header(),
							
							html.Div([
									  create_dropdown_dist('district-name'),
									  create_dropdown_hotel('hotel-name'),
									  create_calendar("check-in-calendar"),
									  #create_calendar("check-out-calendar"),
							 ],className='row',style=dict(display='flex')) ,
							 # ,style=dict(display='flex') makes the bars aligned
								
							html.Div(id='result-selected', style={'textAlign': 'center'}, className='row'),

							html.Div([
									  html.Div(create_content('my-graph')),
									  
									  
									  html.Div( id='pred_result', children= [
												
												]),
									  # style={'vertical-align': 'middle'}
									  
								], className='row')
								
					   ]
					  ,
					  className='ten columns offset-by-one',
					  #style={'font-family': theme['font-family']}
					  ) # golbal



## update text
@app.callback(
			  Output('pred_result', 'children'),
			  [# list of dash.dependencies Input
			   Input('hotel-name', 'value'),
			   Input('check-in-calendar', 'date'),
			   #Input('check-out-calendar', 'date')
			   ]
			  )
def update_prediction(hotel_name, in_datepick):
	
	a, lat_pick, long_pick = is_crime_occur(df_airbnb, loaded_model, df_policeStat, df_mbta, hotel_name, in_datepick)
	val_predict = 'There will be NO CRIME'
	if a[0] > 0.5:
		val_predict = 'High chance to have CRIME !'
	val_predict1 = 'There will be NO CRIME'
	if a[1] > 0.5:
		val_predict1 = 'High chance to have CRIME !'
	val_predict2 = 'There will be NO CRIME'
	if a[2] > 0.5:
		val_predict2 = 'High chance to have CRIME !'
	
	a = html.Div([
				  html.Label(' ', className='three columns'),
				  dcc.Input(id= 'pred1', value= '[12AM -  8AM]  ' + val_predict, type='text', className='four columns'),
				  dcc.Input(id= 'pred2', value= '[ 8AM -  4PM]  ' + val_predict1, type='text', className='four columns'),
				  dcc.Input(id= 'pred3', value= '[ 4PM - 12AM]  '  + val_predict2, type='text', className='four columns'),
				  
#				  dash_table.DataTable(
#									   id='table',
#									   columns=[{"name":"test0", "id":"test1"}],
#									   data=pd.DataFrame({"test":"test2"}),
#									   )
				  
				  ])
	return a



## update text
@app.callback(
              Output('result-selected', 'children'),
              [# list of dash.dependencies Input
               Input('hotel-name', 'value'),
               Input('check-in-calendar', 'date'),
			   #Input('check-out-calendar', 'date')
               ]
              )
def update_hotelname(hotel_name, in_datepick):
	return 'You selected "{}"'.format(hotel_name + ". Check-in date is " +in_datepick)
#def update_hotelname(hotel_name, in_datepick, out_datepick): # the first parameter is the first dash.dependencies Input, and so on
#return 'You selected "{}"'.format(hotel_name + ". Check-in date is " +in_datepick + ". Checkout date is " +out_datepick)


@app.callback(
			  Output('hotel-name', 'options'),
			  [# list of dash.dependencies Input
			   Input('district-name', 'value'),
			   ]
			  )
def update_hotel_dropdown(dist_name): # the first parameter is the first dash.dependencies Input, and so on
	hotels = df_airbnb[df_airbnb["neighbourhood"] == dist_name]["name"][:]
	return [{'label': i, 'value': i} for i in hotels]




## update map
@app.callback(
              Output("my-graph", "figure"),
              [# list of dash.dependencies Input
			   Input('hotel-name', 'value'),
			   #Input('latitude', 'value'),
			   #Input('longitude', 'value'),
               Input('check-in-calendar', 'date')
               ]
              )
def update_map(hotel_name, datepick): # the first parameter is the first dash.dependencies Input, and so on
	a, lat_pick, long_pick = is_crime_occur(df_airbnb, loaded_model, df_policeStat, df_mbta, hotel_name, datepick)
	display_txt = ""
	#display_txt =  "[12AM- 8AM  is " + str(a[0]) + "]\n"
	#display_txt += "[8AM - 4PM  is " + str(a[1]) + "]\n"
	#display_txt += "[4PM - 12AM is " + str(a[2]) + "]\n"
	display_txt = hotel_name + '\n' + display_txt
	if a[0] > 0.5 or a[1] > 0.5 or a[2] > 0.5:
		plot_col = "rgb(255, 0, 0)"
		plot_col_opac = "rgb(242, 177, 172)"
	else:
		plot_col = "rgb(0, 255, 0)"
		plot_col_opac = "rgb(172, 242, 172)"
	trace = []
	
	trace.append(
				go.Scattermapbox(lat=[lat_pick], lon=[long_pick],
								 mode='markers',
								 marker=go.scattermapbox.Marker(
																size=5,
																color=plot_col
																))
				)
	trace.append(
				 go.Scattermapbox(lat=[lat_pick], lon=[long_pick],
								  mode='markers',
								  marker=go.scattermapbox.Marker(
																 size=25,
																 color=plot_col_opac,
																 opacity=0.7
																 ),
								  text=display_txt,
								  hoverinfo='text',
								  name='')
				 )

	layout = go.Layout(
						 autosize=True,
						 hovermode='closest',
						 showlegend=False,
						 height=400,
					     margin=go.layout.Margin(l=0, r=0, t=25, b=30),
						 mapbox={
						 'accesstoken': mapbox_access_token,
						 'bearing': 0,
						 'center': {'lat': lat_pick, 'lon': long_pick},
						 'pitch': 0,
						 'zoom': 13,
					     "style": 'mapbox://styles/mapbox/light-v9'
								   })

	dict_return = {"data":trace, "layout":layout}

	return dict_return


#@app.callback(
#			  Output('result_filter', 'children'),
#			  [
#			   Input('hotel-text-filter', 'value')
#			   ]
#			  )
#def filter_hotel_by_name(filter_text):
##return bigfoot_by_year(filter_sightings(filter_text))
#	return 'Your filter is "{}"'.format(filter_text)





if __name__ == '__main__':
	#loaded_model = pickle.load(open("grad_bdt_classi_2019_06_14.sav", 'rb'))
	#app.run_server(debug=True)
	app.run_server(debug=True)
	#app.server.run(debug=True, threaded=True)
