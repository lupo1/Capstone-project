#!/usr/bin/env python
# coding: utf-8

# ## Backgound and problem
# New York is the leading city of the world. According to Globalization and World Cities Research Network 2008,it is considered as an alfa ++ city togheter with London. With an estimated 2018 population of 8,398,748 distributed over a land area of about 302.6 square miles (784 km2), New York is also the most densely populated major city in the United States. 
# In this set, moving to New York could be an interesting and fruitfull period of the life. 
# As italian physician, I'd like to move to NY close to an hospital close to an italian restaurant 
# The project will be focuse on find out the hospital in center of NY with a good (rating average >7) italian restaurant

# ## Data and strategy
# To approach this problem, I need 3 different set of data:
# - list of NY postal code, Boroughs, Neighborhoods along with their latitude and longitude
# - list of hospital in NY
# - list of italian restaurant

# ### Data source
# - NY postal code, Boroughs, Neighborhoods along with their latitude and longitude
# - hospital in NY: foursquare API
# - italian restaurant: foursquare API

# # Analysis

# ### Imported the required library

# In[1]:


import requests # library to handle requests
import pandas as pd # library for data analsysis
import numpy as np # library to handle data in a vectorized manner
import random # library for random number generation

get_ipython().system('conda install -c conda-forge geopy --yes ')
from geopy.geocoders import Nominatim # module to convert an address into latitude and longitude values

# libraries for displaying images
from IPython.display import Image 
from IPython.core.display import HTML 
    
# tranforming json file into a pandas dataframe library
from pandas.io.json import json_normalize

get_ipython().system('conda install -c conda-forge folium=0.5.0 --yes')
import folium # plotting library

print('Folium installed')
print('Libraries imported.')


# In[2]:


CLIENT_ID = 'GYUXRRUIPW0QOOJXLVF0PI4OOLSNFPF0IA22IV2C3EQ5K41V' # your Foursquare ID
CLIENT_SECRET = '4VDSEZY2D15ZN2Z11XLVL0PYVI3ATWQKQ0VPDF04UQ02Q1CX' # your Foursquare Secret
VERSION = '20180604'
LIMIT = 30
print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[3]:


address = 'New York, NY'

geolocator = Nominatim(user_agent="ny_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print(latitude, longitude)


# In[4]:


def get_venues(lat,lng):
    
    #set variables
    radius=1000
    LIMIT=100
    CLIENT_ID = os.environ['CLIENT_ID'] # your Foursquare ID
    CLIENT_SECRET = os.environ['CLIENT_SECRET'] # your Foursquare Secret
    VERSION = '20180605' # Foursquare API version
    
    #url to fetch data from foursquare api
    url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
    
    # get all the data
    results = requests.get(url).json()
    venue_data=results["response"]['groups'][0]['items']
    venue_details=[]
    for row in venue_data:
        try:
            venue_id=row['venue']['id']
            venue_name=row['venue']['name']
            venue_category=row['venue']['categories'][0]['name']
            venue_details.append([venue_id,venue_name,venue_category])
        except KeyError:
            pass
        
    column_names=['ID','Name','Category']
    df = pd.DataFrame(venue_details,columns=column_names)
    return df


# In[5]:


def get_venue_details(venue_id):
        
    CLIENT_ID = os.environ['CLIENT_ID'] # your Foursquare ID
    CLIENT_SECRET = os.environ['CLIENT_SECRET'] # your Foursquare Secret
    VERSION = '20180605' # Foursquare API version
    
    #url to fetch data from foursquare api
    url = 'https://api.foursquare.com/v2/venues/{}?&client_id={}&client_secret={}&v={}'.format(
            venue_id,
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION)
    
    # get all the data
    results = requests.get(url).json()
    venue_data=results['response']['venue']
    venue_details=[]
    try:
        venue_id=venue_data['id']
        venue_name=venue_data['name']
        venue_likes=venue_data['likes']['count']
        venue_rating=venue_data['rating']
        venue_tips=venue_data['tips']['count']
        venue_details.append([venue_id,venue_name,venue_likes,venue_rating,venue_tips])
    except KeyError:
        pass
        
    column_names=['ID','Name','Likes','Rating','Tips']
    df = pd.DataFrame(venue_details,columns=column_names)
    return df


# In[6]:


def get_new_york_data():
    url='https://cocl.us/new_york_dataset'
    resp=requests.get(url).json()
    # all data is present in features label
    features=resp['features']
    
    # define the dataframe columns
    column_names = ['Borough', 'Neighborhood', 'Latitude', 'Longitude'] 
    # instantiate the dataframe
    new_york_data = pd.DataFrame(columns=column_names)
    
    for data in features:
        borough = data['properties']['borough'] 
        neighborhood_name = data['properties']['name']
        
        neighborhood_latlon = data['geometry']['coordinates']
        neighborhood_lat = neighborhood_latlon[1]
        neighborhood_lon = neighborhood_latlon[0]
    
        new_york_data = new_york_data.append({'Borough': borough,
                                          'Neighborhood': neighborhood_name,
                                          'Latitude': neighborhood_lat,
                                          'Longitude': neighborhood_lon}, ignore_index=True)
    
    return new_york_data


# In[7]:


new_york_data=get_new_york_data()


# ### Search for Hospital nearby to NY center

# In[8]:


search_query = 'Hospital'
radius = 1000
print(search_query + ' .... OK!')


# In[9]:


url = 'https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&ll={},{}&v={}&query={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, search_query, radius, LIMIT)
url


# In[10]:


results = requests.get(url).json()
results


# In[11]:


# assign relevant part of JSON to venues
venues = results['response']['venues']

# tranform venues into a dataframe
dataframe_hospital= json_normalize(venues)


# In[12]:


# keep only columns that include venue name, and anything that is associated with location
filtered_columns = ['name', 'categories'] + [col for col in dataframe_hospital.columns if col.startswith('location.')] + ['id']
dataframe_hospital_filtered = dataframe_hospital.loc[:, filtered_columns]

# function that extracts the category of the venue
def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']

# filter the category for each row
dataframe_hospital_filtered['categories'] = dataframe_hospital_filtered.apply(get_category_type, axis=1)

# clean column names by keeping only last term
dataframe_hospital_filtered.columns = [column.split('.')[-1] for column in dataframe_hospital_filtered.columns]

dataframe_hospital_filtered


# In[13]:


venue_id = '4a82ef0af964a52092f91fe3' 
url = 'https://api.foursquare.com/v2/venues/{}?client_id={}&client_secret={}&v={}'.format(venue_id, CLIENT_ID, CLIENT_SECRET, VERSION)
url


# In[14]:


result = requests.get(url).json()
print(result['response']['venue'].keys())
result['response']['venue']


# In[15]:


try:
    print(result['response']['venue']['rating'])
except:
    print('This venue has not been rated yet.')


# # NewYork-Presbyterian-Lower Manhattan Hospital is the closest hospital to NY center

# ### Lets look for italian Restaurant nearby 

# In[16]:


search_query = 'Italian'
radius = 10000
print(search_query + ' .... OK!')


# In[17]:


CLIENT_ID = 'GYUXRRUIPW0QOOJXLVF0PI4OOLSNFPF0IA22IV2C3EQ5K41V' # your Foursquare ID
CLIENT_SECRET = '4VDSEZY2D15ZN2Z11XLVL0PYVI3ATWQKQ0VPDF04UQ02Q1CX' # your Foursquare Secret
VERSION = '20180604'
LIMIT = 50


# In[18]:


url = 'https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&ll={},{}&v={}&query={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, search_query, radius, LIMIT)
url


# In[19]:


results = requests.get(url).json()
results


# In[20]:


# assign relevant part of JSON to venues
venues = results['response']['venues']

# tranform venues into a dataframe
dataframe = json_normalize(venues)
dataframe.head()


# In[21]:


# keep only columns that include venue name, and anything that is associated with location
filtered_columns = ['name', 'categories'] + [col for col in dataframe_hospital.columns if col.startswith('location.')] + ['id']
dataframe_filtered = dataframe.loc[:, filtered_columns]

# function that extracts the category of the venue
def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']

# filter the category for each row
dataframe_filtered['categories'] = dataframe_filtered.apply(get_category_type, axis=1)

# clean column names by keeping only last term
dataframe_filtered.columns = [column.split('.')[-1] for column in dataframe_filtered.columns]

dataframe_filtered


# In[22]:


venues_map = folium.Map(location=[latitude, longitude], zoom_start=13) # generate map centred around the Conrad Hotel

# add a red circle marker to represent the Conrad Hotel
folium.features.CircleMarker(
    [latitude, longitude],
    radius=10,
    color='red',
    popup='NewYork-Presbyterian-Lower Manhattan Hospital',
    fill = True,
    fill_color = 'red',
    fill_opacity = 0.6
).add_to(venues_map)

# add the Italian restaurants as blue circle markers
for lat, lng, label in zip(dataframe_filtered.lat, dataframe_filtered.lng, dataframe_filtered.categories):
    folium.features.CircleMarker(
        [lat, lng],
        radius=5,
        color='blue',
        popup=label,
        fill = True,
        fill_color='blue',
        fill_opacity=0.6
    ).add_to(venues_map)

# display map
venues_map


# In[23]:


venue_id = '4a4560a7f964a5201aa81fe3' 
url = 'https://api.foursquare.com/v2/venues/{}?client_id={}&client_secret={}&v={}'.format(venue_id, CLIENT_ID, CLIENT_SECRET, VERSION)
url


# In[24]:


result = requests.get(url).json()
print(result['response']['venue'].keys())
result['response']['venue']


# In[25]:


try:
    print(result['response']['venue']['rating'])
except:
    print('This venue has not been rated yet.')


# # Harry's Italian Pizza Bar	is an italian Restaurant with a grade >7 ad it is close to NewYork-Presbyterian-Lower Manhattan Hospital. So I can move 

# In[ ]:




