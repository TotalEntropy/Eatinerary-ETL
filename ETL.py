#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Importing dependencies
import os
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
pd.set_option('display.max_columns', None)


# In[2]:


# Path to source JSON
businessJson=os.path.join('sourceData', 'business.json')


# In[3]:


# Path to Yelp food/restaurant categories csv
yelpCategories=os.path.join('sourceData', 'yelpCategories.csv')


# In[4]:


# Creating pd dataframe
business_raw=pd.read_json(businessJson, lines=True)


# In[5]:


# Select only the businesses in Ontario
business_on=business_raw.loc[business_raw['state'] == 'ON']


# In[6]:


# Dropping any rows with blank values in these categories
business_on=business_on.dropna(subset=['name', 'address', 'postal_code', 'city', 'state', 'latitude', 'longitude', 'attributes',
                                               'categories', 'hours']).reset_index(drop=True)


# In[7]:


# Regex to fix spelling mistakes 
business_on.replace({'city': {'^AGINCOURT$': 'Agincourt',
                           '^Bradford West Gwillimbury$': 'Bradford',
                           '^East Ajax$': 'Ajax',
                           '^Caledon.{,8}$': 'Caledon',
                           '^East Gwil{1,2}imbury$': 'East Gwillimbury',
                           '(?i)^.*icoke$': 'Etobicoke',
                           '^.{,9}Toro?nto.{,9}$': 'Toronto',
                           'Malton': 'Mississauga',
                           '^.{,5}Missis{1,2}a?ua?g.{1,2}$': 'Mississauga',
                           '^Regional Municipality of York$': 'North York',
                           '(?i)^North.{0,2}York$': 'North York',
                           '^York Regional Municipality$': 'York',
                           '^Willowdale$': 'North York',
                           '^North of Brampton$': 'Brampton',
                           '(?i)^Oak.?ridges$': 'Oak Ridges',
                           '^oakville$': 'Oakville',
                           '(?i)^Richmond?.?Hill?$': 'Richmond Hill',
                           '^.{,8}Scar.?bo?rough$': 'Scarborough',
                           '^.{,11}Stouffville$': 'Stouffville',
                           '(?i)^Thornhil{,2}$': 'Thornhill',
                           '^.*Vaugh.{,3}$': 'Vaughan',
                           '^Wh.?i.?by$': 'Whitby'}}, inplace=True, regex=True)


# In[8]:


business=business_on.loc[business_on['city'].isin(['Unionville', 'Bolton', 'York', 'Bradford', 'Concord', 'East York', 'Stouffville',
                                                   'Woodbridge', 'Aurora', 'Ajax', 'Whitby', 'Pickering', 'Thornhill', 'Newmarket',
                                                   'Oakville', 'Etobicoke', 'North York', 'Scarborough', 'Vaughan', 'Richmond Hill',
                                                   'Brampton', 'Markham', 'Mississauga', 'Toronto'])].reset_index(drop=True)


# In[9]:


# Only taking these columns
business=business.loc[:, ['name', 'address', 'postal_code', 'city', 'latitude', 'longitude','categories', 'stars', 'hours','attributes']]
business.columns=['Name', 'Address', 'Postal_code', 'City', 'Latitude', 'Longitude', 'Categories', 'Stars', 'Hours', 'Attributes']


# ## Handling the hours column

# In[10]:


# Turning the hours column in to a df
hours_raw=json_normalize(data=business['Hours'])
business.drop(columns='Hours', inplace=True)


# In[11]:


# Reorganise columns
hours_raw=hours_raw.loc[:,['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]


# In[12]:


# Create a new df with opening and closing hours
columnsHours=hours_raw.columns
hours=hours_raw


# In[13]:


# Loop through and split the columns
for column in columnsHours:
    hours[[f"{column}_open", f"{column}_close"]]=hours_raw[column].str.split('-', expand=True)
hours.drop(columns=columnsHours, inplace=True)
hours=hours.apply(lambda x: x.str.strip())


# In[14]:


# # Create new list of column names and convert the time to minutes
columnsHours=hours.columns
for column in columnsHours:
    hours[column]=hours[column].replace('$', ':00', regex=True)
    hours[column]=pd.to_timedelta(hours[column])
    hours[column]=hours[column].dt.seconds//60


# In[15]:


# Add hours column to the original DF
business=business.join(hours)


# ## Handling the categories column

# In[16]:


# Turning the Categories column in to a df and adding restaurant id
category = business['Categories'].str.split(',', expand=True)
business.drop(columns='Categories', inplace=True)
category['Restaurant_id']=business.index
category=pd.melt(category, id_vars='Restaurant_id', value_name='Category').drop(columns='variable').sort_values('Restaurant_id')


# In[17]:


# Eliminating None categories
category=category.loc[~category['Category'].isin([None])].reset_index(drop=True)
category['Category'] = category['Category'].str.strip()


# In[18]:


# Read csv with list of yelp categories
foodCategories=pd.read_csv(yelpCategories)
foodCategories['Category'] = foodCategories['Category'].str.strip()


# In[19]:


# Take only the categories from the list of yelp categories
categoryFiltered=pd.DataFrame(category.loc[category['Category'].isin(foodCategories['Category'])])


# In[20]:


# Filter out categories that don't apply
categoryFiltered=categoryFiltered.loc[category['Category'].isin(['Acai Bowls', 'Afghan', 'African', 'Arabian', 'Argentine', 'Asian Fusion', 'Australian', 'Austrian', 'Bagels', 'Bangladeshi',
                                                                   'Barbeque', 'Basque', 'Beer Bar', 'Beer Gardens', 'Beer Hall', 'Belgian', 'Bistros', 'Brasseries', 'Brazilian', 'Breakfast & Brunch',
                                                                   'Brewpubs', 'British', 'Bubble Tea', 'Buffets', 'Burgers', 'Burmese', 'Cafes', 'Cajun/Creole', 'Cambodian', 'Cantonese', 'Caribbean',
                                                                   'Champagne Bars', 'Cheese Shops', 'Cheesesteaks', 'Chicken Shop', 'Chicken Wings', 'Chinese', 'Chocolatiers & Shops',
                                                                   'Cocktail Bars', 'Coffee & Tea', 'Colombian', 'Comfort Food', 'Creperies', 'Cuban', 'Cupcakes',
                                                                   'Czech', 'Czech/Slovakian', 'Delicatessen', 'Delis', 'Desserts', 'Dim Sum', 'Diners', 'Dive Bars', 'Do-It-Yourself Food', 'Donairs',
                                                                   'Egyptian', 'Ethical Grocery', 'Ethiopian', 'Falafel', 'Fast Food', 'Filipino', 'Fish & Chips', 'Fondue',
                                                                   'Food Stands', 'Food Trucks', 'French', 'Fruits & Veggies', 'Gastropubs', 'Gelato', 'German', 'Gluten-Free', 'Greek', 'Hainan', 'Haitian',
                                                                   'Hakka', 'Halal', 'Hawaiian', 'Himalayan/Nepalese', 'Hong Kong Style Cafe', 'Hot Dogs', 'Hot Pot', 'Hungarian', 'Iberian',
                                                                   'Ice Cream & Frozen Yogurt', 'Imported Food', 'Indian', 'Indonesian', 'International', 'Internet Cafes', 'Irish', 'Irish Pub', 'Italian',
                                                                   'Izakaya', 'Japanese', 'Japanese Sweets', 'Juice Bars & Smoothies', 'Kebab', 'Kombucha', 'Korean', 'Kosher', 'Laotian', 'Latin American',
                                                                   'Lebanese', 'Live/Raw Food', 'Lounges', 'Macarons', 'Malaysian', 'Mauritius', 'Mediterranean', 'Mexican', 'Middle Eastern',
                                                                   'Milkshake Bars', 'Minho', 'Modern European', 'Mongolian', 'Moroccan', 'Nicaraguan', 'Noodles', 'Pakistani', 'Pan Asian', 'Pasta Shops',
                                                                   'Persian/Iranian', 'Peruvian', 'Pizza', 'Poke', 'Polish', 'Portuguese',
                                                                   'Poutineries', 'Pubs', 'Ramen', 'Reunion', 'Russian', 'Salad', 'Salvadoran', 'Sandwiches', 'Scandinavian', 'Scottish', 'Seafood',
                                                                   'Seafood Markets', 'Shanghainese', 'Shaved Ice', 'Shaved Snow', 'Singaporean', 'Slovakian', 'Smokehouse', 'Soul Food', 'Soup',
                                                                   'South African', 'Southern', 'Spanish', 'Specialty Food', 'Sports Bars', 'Sri Lankan', 'Steakhouses', 'Street Vendors', 'Supper Clubs',
                                                                   'Sushi Bars', 'Swiss Food', 'Syrian', 'Szechuan', 'Tacos', 'Taiwanese', 'Tapas Bars', 'Tapas/Small Plates', 'Tea Rooms', 'Tempura',
                                                                   'Teppanyaki', 'Tex-Mex', 'Thai', 'Themed Cafes', 'Tiki Bars', 'Tonkatsu', 'Trinidadian', 'Turkish', 'Udon', 'Ukrainian', 'Vegan',
                                                                   'Vegetarian', 'Venezuelan', 'Vietnamese', 'Waffles', 'Whiskey Bars', 'Wine Bars', 'Wraps'])]


# In[21]:


# Creating a list of unique food categories
uniqueCategories=categoryFiltered['Category'].unique()
uniqueCategories.sort()


# In[22]:


# Replace all the values in categoryFiltered with the uniqueCategories index
for index, value in enumerate(uniqueCategories):
    categoryFiltered['Category'].replace(value, str(index), inplace=True)


# In[23]:


# Collect all the categories to one string
categoryPivot=categoryFiltered.pivot('Restaurant_id', 'Category', 'Category')
categoryPivot['Categories']=categoryPivot.apply(lambda x: ','.join(x.dropna().values), axis=1)


# In[24]:


# Join categories column on business
business=business.join(categoryPivot['Categories'], how='inner').reset_index(drop=True)
business.rename(columns={'Categories':'Category_ids'}, inplace=True)


# In[25]:


# Create DF for sql
uniqueCategories=pd.DataFrame(uniqueCategories, columns=['Category'])


# ## Handling the attributes column

# In[26]:


# Turning the Attributes column in to a df and adding restaurant id
attributesRaw=json_normalize(business['Attributes'])
business.drop(columns='Attributes', inplace=True)
attributes=attributesRaw.fillna('')
attributes['Restaurant_id']=business.index


# In[27]:


# Generate unique categories for ambience 
ambienceCategories=attributesRaw['Ambience'].str.split(',', expand=True).replace(['{', '}', 'False', 'True', ':', "'", ' '], '', regex=True).melt().dropna().drop(columns='variable')
ambienceCategories=ambienceCategories.loc[~ambienceCategories['value'].isin(['None'])]
ambienceCategories=ambienceCategories['value'].unique().tolist()


# In[28]:


# Generating boolean columns for ambience
for value in ambienceCategories:
    attributes[f'Ambience_{value}']=attributes['Ambience'].str.contains(f"{value}': True")
attributes.drop(columns='Ambience', inplace=True)


# In[29]:


# Generate unique categories for BusinessParking
businessParking = attributesRaw['BusinessParking'].str.split(',', expand=True).replace(['{', '}', 'False', 'True', ':', "'", ' '], '', regex=True).melt().dropna().drop(columns='variable')
businessParking=businessParking.loc[~businessParking['value'].isin(['None', ''])]
businessParking=businessParking['value'].unique().tolist()


# In[30]:


# Generating boolean columns for BusinessParking
for value in businessParking:
    attributes[f'Parking_{value}']=attributes['BusinessParking'].str.contains(f"{value}': True")
attributes.drop(columns='BusinessParking', inplace=True)


# In[31]:


# Generate unique categories for GoodForMeal
goodForMeal = attributesRaw['GoodForMeal'].str.split(',', expand=True).replace(['{', '}', 'False', 'True', ':', "'", ' '], '', regex=True).melt().drop(columns='variable').dropna()
goodForMeal=goodForMeal.loc[~goodForMeal['value'].isin(['None', ''])]
goodForMeal=goodForMeal['value'].unique().tolist()


# In[32]:


# Generating boolean columns for GoodForMeal
for value in goodForMeal:
    attributes[f'Meal_{value}']=attributes['GoodForMeal'].str.contains(f"{value}': True")
attributes.drop(columns='GoodForMeal', inplace=True)


# In[33]:


# Generate unique categories for BestNights
bestNights = attributesRaw['BestNights'].str.split(',', expand=True).replace(['{', '}', 'False', 'True', ':', "'", ' '], '', regex=True).melt().drop(columns='variable').dropna()
bestNights=bestNights.loc[~bestNights['value'].isin([''])]
bestNights=bestNights['value'].unique().tolist()


# In[34]:


# Generating boolean columns for BestNights
for value in bestNights:
    attributes[f'Best_night_{value}']=attributes['BestNights'].str.contains(f"{value}': True")
attributes.drop(columns='BestNights', inplace=True)


# In[35]:


# Generate unique categories for Alcohol
alcohol=pd.DataFrame(attributesRaw['Alcohol'].unique()).dropna()
alcohol=alcohol.replace(["'", ' '], '', regex=True)
alcohol=alcohol.loc[~alcohol[0].isin(['none', 'ufull_bar', 'unone', 'ubeer_and_wine', 'None'])]
alcohol=alcohol[0].unique().tolist()


# In[36]:


# Generate unique categories for Alcohol
for value in alcohol:
    attributes[f'Alcohol_{value}']=attributes['Alcohol'].str.contains(value)
attributes.drop(columns='Alcohol', inplace=True)


# In[37]:


# Generate unique categories for DietaryRestrictions 
dietaryRestrictions = attributes['DietaryRestrictions'].str.split(',', expand=True).replace(['{', '}', 'False', 'True', ':', "'", ' '], '',
                                                                                               regex=True).melt().drop(columns='variable').dropna()
dietaryRestrictions=dietaryRestrictions.loc[~dietaryRestrictions['value'].isin(['None', ''])]
dietaryRestrictions=dietaryRestrictions['value'].unique().tolist()


# In[38]:


# Generating boolean columns
for value in dietaryRestrictions:
    attributes[f'Dietary_Restrictions_{value}']=attributes['DietaryRestrictions'].str.contains(f"{value}': True")
attributes.drop(columns='DietaryRestrictions', inplace=True)


# In[39]:


# Generate unique categories for Music 
music = attributesRaw['Music'].str.split(',', expand=True).replace(['{', '}', 'False', 'True', ':', "'", ' '], '', regex=True).melt().drop(columns='variable').dropna()
music=music.loc[~music['value'].isin(['None', ''])]
music=music['value'].unique().tolist()


# In[40]:


# Generating boolean columns
for value in music:
    attributes[f'Music_{value}']=attributes['Music'].str.contains(f"{value}': True")
attributes.drop(columns='Music', inplace=True)


# In[41]:


# Generate unique categories for NoiseLevel 
noiseLevel=pd.DataFrame(attributesRaw['NoiseLevel'].unique()).dropna()
noiseLevel=noiseLevel.replace(["'", ' '], '', regex=True)
noiseLevel=noiseLevel.loc[~noiseLevel[0].isin(['None', 'uloud', 'uaverage', 'uquiet', 'uvery_loud'])]
noiseLevel=noiseLevel[0].tolist()


# In[42]:


# Generate unique categories for noiseLevel 
for value in noiseLevel:
    attributes[f'Noise_{value}']=attributes['NoiseLevel'].str.contains(value)
attributes.drop(columns='NoiseLevel', inplace=True)


# In[43]:


# Generate unique categories for RestaurantsAttire 
restaurantsAttire=pd.DataFrame(attributesRaw['RestaurantsAttire'].unique()).dropna()
restaurantsAttire=restaurantsAttire.replace(["'", ' '], '', regex=True)
restaurantsAttire=restaurantsAttire.loc[~restaurantsAttire[0].isin(['ucasual', 'None', 'udressy', 'uformal'])]
restaurantsAttire=restaurantsAttire[0].tolist()


# In[44]:


# Generate unique categories for RestaurantsAttire 
for value in restaurantsAttire:
    attributes[f'Restaurants_Attire_{value}']=attributes['RestaurantsAttire'].str.contains(value)
attributes.drop(columns='RestaurantsAttire', inplace=True)


# In[45]:


# Generate unique categories for Smoking 
smoking=pd.DataFrame(attributesRaw['Smoking'].unique()).dropna()
smoking=smoking.replace(["'", "' '", '.outdoor', '.yes', '.no'], ['', '', 'outdoor', 'yes', 'no'], regex=True)
smoking=smoking.loc[~smoking[0].isin(['None'])]
smoking=smoking[0].tolist()


# In[46]:


# Generating Smoking boolean columns
for value in smoking:
    attributes[f'Smoking_{value}']=attributes['Smoking'].str.contains(f"{value}': True")
attributes.drop(columns='Smoking', inplace=True)


# In[47]:


# Convert columns to boolean
attributes.replace({'AgesAllowed':{'':False, "u'19plus'":True},
                    'BYOBCorkage':{'':False, "u'yes_corkage'":True},
                    'BikeParking':{'False':False, 'None':False, '':False, 'True':True},
                    'BusinessAcceptsCreditCards':{'False':False, 'None':False, '':False, 'True':True},
                    'CoatCheck':{'False':False, 'None':False, '':False, 'True':True},
                    'DogsAllowed':{'False':False, 'None':False, '':False, 'True':True},
                    'GoodForDancing':{'False':False, 'None':False, '':False, 'True':True},
                    'GoodForKids':{'False':False, 'None':False, '':False, 'True':True},
                    'HappyHour':{'False':False, 'None':False, '':False, 'True':True},
                    'HasTV':{'False':False, 'None':False, '':False, 'True':True},
                    'OutdoorSeating':{'False':False, 'None':False, '':False, 'True':True},
                    'RestaurantsCounterService':{'True':True, '':False},
                    'RestaurantsGoodForGroups':{'False':False, 'None':False, '':False, 'True':True},
                    'RestaurantsPriceRange2':{'None':np.nan},
#                     'RestaurantsPriceRange2':{'':0, 'None':0},
                    'RestaurantsTableService':{'False':False, 'None':False, '':False, 'True':True},
                    'RestaurantsTakeOut':{'False':False, 'None':False, '':False, 'True':True},
                    'WheelchairAccessible':{'False':False, 'None':False, '':False, 'True':True}}, inplace=True)

# Convert pricing column to int
attributes['RestaurantsPriceRange2']=pd.to_numeric(attributes['RestaurantsPriceRange2'])


# In[48]:


# Rename AgesAllowed to Over_19
attributes.rename(columns={'AgesAllowed':'Over_19'}, inplace=True)


# In[49]:


# Drop unnecessary columns
attributes.drop(columns=['AcceptsInsurance', 'BusinessAcceptsBitcoin', 'Caters', 'DriveThru', 'HairSpecializesIn', 'Open24Hours',
                         'RestaurantsDelivery', 'RestaurantsReservations', 'WiFi'], inplace=True)


# In[50]:


# Filter by restaurants that require appointments
attributes=attributes.loc[attributes['ByAppointmentOnly']!='True']
attributes.drop(columns='ByAppointmentOnly', inplace=True)


# In[51]:


# Join the master table with the attributes table
business=business.join(attributes, how='inner').drop(columns='Restaurant_id').reset_index(drop=True)


# In[52]:


# Dependencies
from sqlalchemy import create_engine, Integer, String, Float, Time, Boolean
from config import conn #Format is 'user:pass@host'
import pymysql


# In[53]:


# Connect to mysql
engine = create_engine(f'mysql+pymysql://{conn}', echo=True)


# In[54]:


# Create the EATinerary db if it doesn't exit
engine.execute('CREATE DATABASE IF NOT EXISTS eatinerary;')


# In[55]:


# Connect to the EATinerary db
engine = create_engine(f'mysql+pymysql://{conn}/eatinerary', echo=True)


# In[56]:


# Creating sql database and tables for the restaurants and the unique categories
uniqueCategories.to_sql('category', engine, if_exists='replace', index_label='Category_id')

# Set primary key for category table
engine.execute('ALTER table category ADD PRIMARY KEY (`category_id`)')


# In[57]:


# Removing all special characters
business['Name']=business['Name'].str.replace('[^A-Za-z\s]+', '')


# In[58]:


# Creating sql database and tables for the restaurants and the unique categories
business.to_sql('restaurant', engine, if_exists='replace', index_label='Restaurant_id')
# , dtype=dataType)

# Set primary key for restaurant table
engine.execute('ALTER table restaurant ADD PRIMARY KEY (`restaurant_id`)')

