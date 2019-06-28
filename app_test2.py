
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
from joblib import load



loaded_model = load('grad_bdt_classi_police_2019_06_27_pipe.joblib')
df_airbnb = pd.read_csv("listings.csv")

df_policeStat = pd.read_csv("Boston_Police_Stations.csv")
df_mbta = pd.read_csv("MBTA_Rapid_Transit_Stops.csv")

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
		dayofweek_sin = np.sin(2 * np.pi * (day.weekday()+1)/7.0)
		dayofweek_cos = np.sin(2 * np.pi * (day.weekday()+1)/7.0)
		
		df_train['dayofweek_sin']  = df_train['dayofweek_sin'].apply(lambda x: int(x*1000))
		df_train['dayofweek_cos']  = df_train['dayofweek_cos'].apply(lambda x: int(x*1000))


		print (dayofweek_sin)
		data = {
		# ["DAY_OF_MONTH","DAY_OF_WEEK_NUM","MONTH","YEAR","Lat","Long"
		#,"Temperature(F)","Humidity(%)","Wind Speed(mph)","Precip.(in)"]
#		# var_scale_strs = ["Lat","Long","Temperature(F)","Humidity(%)","Wind Speed(mph)",
#			"Precip.(in)","closest_police_d","closest_mbta_d",
#				"dayofmonth_sin","dayofmonth_cos",
#					"dayofweek_sin","dayofweek_cos",
#						"month_sin","month_cos",]


		'Lat':[lat],
		'Long':[long],
		'Temperature(F)':[w_data[i]['temp']],
		'Humidity(%)':[w_data[i]['humid']],
		'Wind Speed(mph)':[w_data[i]['wndsp']],
		'Precip.(in)':[w_data[i]['pcip']],
		'closest_police_d': [dist_closest_police],
		'closest_mbta_d': [dist_closest_mbta],
		'dayofmonth_sin': [0.5],
		'dayofmonth_cos': [0.5],
		'dayofweek_sin':[0.5],
		'dayofweek_cos':[0.5],
		'month_sin':[0.5],
		'month_cos':[0.5],
		#'Hour_Grp':[i+1],
		
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

hotel_name = "One Bedroom Studio Garden Apartment"
in_datepick = "2019-07-20"
a, lat_pick, long_pick = is_crime_occur(df_airbnb, loaded_model, df_policeStat, df_mbta, hotel_name, in_datepick)

print (a, lat_pick, long_pick)
