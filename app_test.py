
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




###----------------------------------------------------###
###----------------------------------------------------###
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

select_date="2019-07-20"
print (get_weather_info(select_date))
