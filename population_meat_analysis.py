#!/usr/bin/env python
# coding: utf-8

# In[269]:


import pandas as pd
import numpy as np
import re
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import urllib.request 
from urllib.error import HTTPError
import json
import time

sns.set_style('darkgrid')


# ## Meat Production (excluding animals slaughtered on farms)

# In[207]:


xlsx = pd.ExcelFile('data/meat_statistics.xlsx')


# The original excel file was designed for human readable, including merged cells for the first category (a.k.a Commerical vs. Federally Inspected below) and then individual cells for the secondary category (a.k.a row 0). 

# In[208]:


raw_data = pd.read_excel(xlsx, sheet_name = 'RedMeatPoultry_Prod-Full', header = 1)
raw_data.head()


# There are two types - Commerical vs. Federally Inspected. Their numbers are pretty close. I decided to use the numbers under Federally Inspected because it contains more information in terms of meat types. 

# In[209]:


idx = list(raw_data.columns).index('Federally inspected')
idxs = [0]
for i in range(len(raw_data.columns)):
    if i >= idx:
        idxs.append(i)


# In[210]:


raw_data = raw_data.iloc[:, idxs]
raw_data.head()


# Replace the current header with the first row (a.k.a the secondary categories) and remove the empty column

# In[211]:


new_header = raw_data.iloc[0, :-1]
raw_data = raw_data.iloc[1:, :-1]
raw_data.columns = new_header
raw_data.head()


# Transform the header by removing space and notation, explained below
# - 1/ Excludes slaughter on farms.																
# - 2/ Production in federally inspected and other plants.															
# - 3/ Based on packers' dressed weights.																
# - 4/ Totals may not add due to rounding.																
# - 5/ Ready-to-cook.																
# - 6/ Includes geese, guineas, ostriches, emus, rheas, squab, and other poultry.																

# In[212]:


current_header = raw_data.columns[1:] 
transformed_header = ['Month']
for i in current_header:
    word = re.search('\D+', i).group().strip().replace(' ', '_')
    transformed_header.append(word.lower())
raw_data.columns = transformed_header
raw_data.head()


# Remove the rows containing additional information

# In[213]:


raw_data.tail(10)


# In[214]:


trim_data = raw_data[~raw_data['Month'].str.contains('/ |Source|Date run')]
trim_data.tail()


# Drop columns for aggregation information and the type of `Other Chicken`

# In[215]:


trim_data = trim_data.iloc[:, [0,1,2,3,4,6,8]]
trim_data.head()


# Keep only the monthly data and then convert to datetime data type

# In[216]:


trim_data.head()


# In[217]:


meat_prod = trim_data.copy()
meat_prod = meat_prod[meat_prod['Month'].str.contains(r'\w{3}-\d{4}', regex=True)]
meat_prod.head()


# In[218]:


meat_prod['Month'] = meat_prod['Month'].apply(lambda x: datetime.strptime(x, '%b-%Y'))
meat_prod.head()


# In[219]:


meat_prod.info()


# In[220]:


# outliers in 1982 and 1948, data unavailabe between 1957 and 1976
sns.relplot(data=meat_prod, x='Month', y = 'beef')


# In[221]:


# 1982 some categories only have quartly data, 1948 December had no clear reasoning
meat_prod.loc[meat_prod['Month'].dt.year==1982, :]


# In[222]:


for i in ['beef', 'veal', 'pork', 'lamb_and_mutton']:
    meat_prod[i] = meat_prod.apply(lambda x: x[i]/3 if x['Month'].year==1982 else x[i], axis = 1)

meat_prod.loc[meat_prod['Month'].dt.year==1982, :]


# In[223]:


# split in 3 evenly and forward fill in missing data 
meat_prod = meat_prod.fillna(method='ffill', limit=2)

meat_prod.loc[meat_prod['Month'].dt.year==1982, :]


# In[224]:


# smooth out the outliers in 1982, drop the outlier in 1948
sns.relplot(data=meat_prod, x='Month', y = 'beef', kind='line')


# In[225]:


# transform the data to visualize on one chart
meat_prod2 = pd.melt(meat_prod, id_vars=['Month'], value_vars=meat_prod.columns[1:])
meat_prod2 = meat_prod2.sort_values(['Month', 'variable'])


# In[226]:


g = sns.relplot(data=meat_prod2.rename(columns={'variable':'Types'}), x='Month', y = 'value', 
                kind='line', hue='Types',height=6, aspect=2)
# extract yearly labels every five year
yearly_labels = sorted(list(meat_prod.loc[meat_prod['Month'].dt.month == 1, 'Month'].dt.year.astype(str)))
# display xtick labels every five year at 0 or 5
g.set(xticks=[yearly_labels[i+4] for i in range(0, len(yearly_labels)-4, 5)])
g.set(xticklabels=[yearly_labels[i+4] for i in range(0, len(yearly_labels)-4, 5)])
g.set(xlabel='Year', ylabel='Pounds (Million)')
g.set(title='Meat Production')


# Aggregate to yearly data making the curve smooth

# In[227]:


meat_prod2['Year'] = meat_prod2['Month'].dt.to_period('Y')
meat_prod3 = meat_prod2.groupby(['Year','variable']).sum().reset_index()
meat_prod3['Year'] = meat_prod3['Year'].astype(str)
meat_prod3['value_in_billion'] = meat_prod3.apply(lambda x: x['value']/9*12/1000 
                                                  if x['Year'] == '2022' 
                                                  else x['value']/1000
                                                  , axis = 1)
meat_prod3['Year'] = pd.to_datetime(meat_prod3['Year'])
meat_prod3.info()


# In[228]:


g = sns.relplot(data=meat_prod3.rename(columns={'variable':'Types'}),
                x='Year', y = 'value_in_billion', kind='line', hue='Types',height=6, aspect=2)
g.set(xlabel='Year', ylabel='Pounds (Billion)')
g.set(title='Meat Production')


# In[229]:


def get_text_label(df, val_name, ax, types, max_or_min = 'max'):
    if max_or_min == 'max':
        year = df['Year'].max()
    else:
        year = df['Year'].min()
        
    val = df.loc[(df['Types']==types) & (df['Year'] == year), val_name]
    
    ax.text(x = year, y = val, s = str(int(val.values)))    


# In[305]:


meat_prod4 = meat_prod3[meat_prod3['Year']>= '1990-01-01'].rename(columns={'variable':'Types'})
g = sns.relplot(data=meat_prod4, x='Year', y = 'value_in_billion', 
                kind='line', hue='Types',height=6)#, aspect=0.7)
# extract yearly labels every five year
yearly_labels = sorted(list(set(meat_prod4['Year'].dt.year.astype(str))))
# display xtick labels every five year at 0 or 5
g.set(xticks=[yearly_labels[i] for i in range(0, len(yearly_labels), 5)])
g.set(xticklabels=[yearly_labels[i] for i in range(0, len(yearly_labels), 5)])
g.set(xlabel='Year', ylabel='Pounds (Billion)')
g.set(title='Meat Production')

# label the data points at the first and last year
for i in meat_prod4['Types'].unique():
    for j in ['max', 'min']:
        get_text_label(df = meat_prod4, val_name = 'value_in_billion',
                       ax = plt.gca(), types = i, max_or_min = j)


# The scope of meat production does not cover animals slaughtered on farms. For the past three decades, US meat production has increased in beef and pork, particularly by 250% in broilers. Turkey has remained almost the same since 1990.

# ## Slaughter Counts

# The original excel file was designed for human readable, including merged cells for the first category (a.k.a Commerical vs. Federally Inspected below) and then individual cells for the secondary category (a.k.a row 0). 

# In[231]:


raw_data2 = pd.read_excel(xlsx, sheet_name = 'SlaughterCounts-Full', header = 1)
raw_data2.head()


# There are two types - Commerical vs. Federally Inspected. Their numbers are pretty close. I decided to use the numbers under Federally Inspected because it contains more information in terms of meat types. 

# In[232]:


idx = list(raw_data2.columns).index('Federally inspected 3/')
idxs = [0]
for i in range(len(raw_data2.columns)):
    if i >= idx:
        idxs.append(i)


# In[233]:


raw_data2 = raw_data2.iloc[:, idxs]
print(raw_data2.shape)
raw_data2.head()


# Replace the current header with the first row (a.k.a the secondary categories) and remove the empty column

# In[234]:


new_header = raw_data2.iloc[0, :]
raw_data2 = raw_data2.iloc[1:, :]
raw_data2.columns = new_header
raw_data2.head()


# Transform the header by removing space and punctuations													

# In[235]:


current_header = raw_data2.columns[1:] 
transformed_header = ['Month']
for i in current_header:
    word = re.search('[A-Z]\D+', i).group().strip().replace(' ', '_')
    transformed_header.append(word.lower())
raw_data2.columns = transformed_header
raw_data2.head()


# Remove the rows containing additional information

# In[236]:


raw_data2.tail(5)


# In[237]:


trim_data2 = raw_data2.dropna(thresh=3) # keep only rows containing 3+ observations
trim_data2.tail(5)


# Keep columns for more common types

# In[238]:


trim_data2 = trim_data2.iloc[:, [0,1,3,4,7,8,12,15,17]]
trim_data2.head()


# Keep only the monthly data and then convert to datetime data type

# In[239]:


slau_count = trim_data2.copy()
slau_count = slau_count[slau_count['Month'].str.contains(r'\w{3}-\d{4}', regex=True)]
slau_count.head()


# In[240]:


slau_count['Month'] = slau_count['Month'].apply(lambda x: datetime.strptime(x, '%b-%Y'))
slau_count.head()


# In[241]:


# outliers in 1982 
sns.relplot(data=slau_count, x='Month', y = 'cattle', aspect=2)


# In[242]:


# 1982 some categories only have quartly data
slau_count.loc[slau_count['Month'].dt.year==1982, :]


# In[243]:


for i in ['cattle', 'heifers', 'hogs', 'sheep_and_lambs']:
    slau_count[i] = slau_count.apply(lambda x: x[i]/3 if x['Month'].year==1982 else x[i], axis = 1)

slau_count.loc[slau_count['Month'].dt.year==1982, :]


# In[244]:


# split in 3 evenly and forward fill in missing data 
slau_count = slau_count.fillna(method='ffill', limit=2)

slau_count.loc[slau_count['Month'].dt.year==1982, :]


# In[245]:


# smooth out the outliers in 1982, drop the outlier in 1948
sns.relplot(data=slau_count, x='Month', y = 'cattle', kind='line', aspect = 2)


# In[246]:


# transform the data to visualize on one chart
slau_count2 = pd.melt(slau_count, id_vars=['Month'], value_vars=slau_count.columns[1:])
slau_count2 = slau_count2.rename(columns={'variable':'Types'})


# In[247]:


g = sns.relplot(data=slau_count2.rename(columns={'variable':'Types'}), x='Month', y = 'value', 
                kind='line', hue='Types',height=6, aspect=2)
# extract yearly labels every five year
yearly_labels = sorted(list(slau_count.loc[slau_count['Month'].dt.month == 1, 'Month'].dt.year.astype(str)))
# display xtick labels every five year at 0 or 5
g.set(xticks=[yearly_labels[i+4] for i in range(0, len(yearly_labels)-4, 5)])
g.set(xticklabels=[yearly_labels[i+4] for i in range(0, len(yearly_labels)-4, 5)])
g.set(xlabel='Year', ylabel='1,000 Head')
g.set(title='Slaughter Counts')


# The count info cannot really tell the truth; try with the weight info.

# ## Slaughter Weights (carcass weight, the weight of chilled animal carcass)

# The original excel file was designed for human readable, including merged cells for the first category (a.k.a Commerical vs. Federally Inspected below) and then individual cells for the secondary category (a.k.a row 0). 

# In[248]:


raw_data3 = pd.read_excel(xlsx, sheet_name = 'SlaughterWeights-Full', header = 1)
raw_data3.head()


# There are three types - `Commercial average live`, `Federally inspected average live`, and `Federally inspected average dressed`. Two average live numbers are pretty close and relatively higher than the average dressed numbers. I decided to use the numbers under Federally Inspected average live because it contains the critical category - broilers.

# In[249]:


idx = list(raw_data3.columns).index('Federally inspected average live')
end_idx = list(raw_data3.columns).index('Federally inspected average dressed 3/')
idxs = [0]
for i in range(len(raw_data3.columns)):
    if i >= idx and i < end_idx:
        idxs.append(i)


# In[250]:


raw_data3 = raw_data3.iloc[:, idxs]
print(raw_data3.shape)
raw_data3.head()


# Replace the current header with the first row (a.k.a the secondary categories) and remove the empty column

# In[251]:


new_header = raw_data3.iloc[0, :]
raw_data3 = raw_data3.iloc[1:, :]
raw_data3.columns = new_header
raw_data3.head()


# Transform the header by removing space and punctuations													

# In[252]:


current_header = raw_data3.columns[1:] 
transformed_header = ['Month']
for i in current_header:
    word = re.search('\D+', i).group().strip().replace(' ', '_')
    transformed_header.append(word.lower())
raw_data3.columns = transformed_header
raw_data3.head()


# Remove the rows containing additional information

# In[253]:


raw_data3.tail(5)


# In[254]:


trim_data3 = raw_data3.dropna(thresh=3) # keep only rows containing 3+ observations
trim_data3.tail(5)


# Keep columns for more common types

# In[255]:


trim_data3 = trim_data3.iloc[:, [0,1,2,3,4,5,7]]
trim_data3.head()


# Keep only the monthly data and then convert to datetime data type

# In[256]:


slau_avg_weight = trim_data3.copy()
slau_avg_weight = slau_avg_weight[slau_avg_weight['Month'].str.contains(r'\w{3}-\d{4}', regex=True)]
slau_avg_weight.head()


# In[257]:


slau_avg_weight['Month'] = slau_avg_weight['Month'].apply(lambda x: datetime.strptime(x, '%b-%Y'))
slau_avg_weight.head()


# In[258]:


# no outliers because it is not aggregated like count or production
sns.relplot(data=slau_avg_weight, x='Month', y = 'cattle', aspect = 2)


# In[259]:


# transform the data to visualize on one chart
slau_avg_weight2 = pd.melt(slau_avg_weight, id_vars=['Month'], value_vars=slau_avg_weight.columns[1:])\
.rename(columns={'value':'average_weight', 'variable':'Types'})
# forward fill in missing value to get rid of nan values in the middle
slau_avg_weight2 = slau_avg_weight2.fillna(method='ffill', limit=2)


# In[260]:


# combine average weight and count information
slau_weight = pd.merge(left = slau_avg_weight2, right = slau_count2.rename(columns={'value':'count_in_thousand'}), on = ['Month', 'Types'])
slau_weight.head()


# In[261]:


# calculate total weight
slau_weight['weight'] =  slau_weight['average_weight'] * slau_weight['count_in_thousand'] * 1000
slau_weight['weight_in_million'] =  slau_weight['weight'] / 1000000
slau_weight.head()


# In[262]:


# drop rows containing any missing values
print(slau_weight.shape)
slau_weight2 = slau_weight.dropna()
print(slau_weight2.shape)


# In[263]:


g = sns.relplot(data=slau_weight2, x='Month', y = 'weight_in_million', 
                kind='line', hue='Types',height=6, aspect=2)
# extract yearly labels every five year
yearly_labels = sorted(list(slau_avg_weight.loc[slau_avg_weight['Month'].dt.month == 1, 'Month'].dt.year.astype(str)))
# display xtick labels every five year at 0 or 5
g.set(xticks=[yearly_labels[i+4] for i in range(0, len(yearly_labels)-4, 5)])
g.set(xticklabels=[yearly_labels[i+4] for i in range(0, len(yearly_labels)-4, 5)])
g.set(xlabel='Year', ylabel='Million Pounds')
g.set(title='Slaughter Weight')


# Aggregate to yearly data making the curve smooth

# In[264]:


slau_weight2['Year'] = slau_weight2['Month'].dt.to_period('Y')
slau_weight3 = slau_weight2.groupby(['Year','Types']).sum().reset_index()
slau_weight3['Year'] = slau_weight3['Year'].astype(str)
slau_weight3['weight_in_billion'] = slau_weight3.apply(lambda x: x['weight_in_million']/9*12/1000
                                                         if x['Year'] == '2022' 
                                                         else x['weight_in_million']/1000
                                                         , axis = 1)
slau_weight3['Year'] = pd.to_datetime(slau_weight3['Year'])
slau_weight3.info()


# In[304]:


slau_weight4 = slau_weight3[slau_weight3['Year']>= '1990-01-01']

dic = {'broilers':'2. broilers', 'cattle': '1. cattle', 'sheep_and_lambs':'2. sheep_and_lambs',
       'hogs' : '4. hogs', 'turkeys': '5. turkeys', 'calves': '6. calves'}
slau_weight4 = slau_weight4.replace({'Types': dic})

g = sns.relplot(data=slau_weight4.sort_values('Types'), x='Year', y = 'weight_in_billion', 
                kind='line', hue='Types',height=6)#, aspect=0.7)
# extract yearly labels every five year
yearly_labels = sorted(list(set(slau_weight4['Year'].dt.year.astype(str))))
# display xtick labels every five year at 0 or 5
g.set(xticks=[yearly_labels[i] for i in range(0, len(yearly_labels), 5)])
g.set(xticklabels=[yearly_labels[i] for i in range(0, len(yearly_labels), 5)])
g.set(xlabel='Year', ylabel='Pounds (Billion)')
g.set(title='Slaughter Weight (Carcass Weight)')

# label the data points at the first and last year
for i in slau_weight4['Types'].unique():
    for j in ['max', 'min']:
        get_text_label(df = slau_weight4, val_name = 'weight_in_billion',
                       ax = plt.gca(), types = i, max_or_min = j)


# Carcass weight is limited to chilled animals, so it accounts for only the partial weight of the live animals. Note that these two categories have no subset relationship; nevertheless, they show a similar trend! For the past three decades, yearly slaughter weight in the US has increased in cattle (beef) and hogs (pork). It also shows a significant 250% increase in broilers. 

# ## US Population (Census Data API)                       

# ![image-2.png](attachment:image-2.png)

# ![image.png](attachment:image.png)

# In[270]:


my_key = ''


# In[271]:


# 2000 Population Estimates - 2000-2010 Intercensal Estimates: National Monthly Population Estimates
# ONLY RETURN 2000-2010 DATA
api_link = 'http://api.census.gov/data/2000/pep/int_natmonthly?get=POP,MONTHLY_DESC&for=us:1&key={}'.format(my_key)
json_result = urllib.request.urlopen(api_link).read()
result1 = json.loads(json_result)
result1


# In[272]:


# Vintage Population Estimates: US, State, and PR Total Population and Components of Change (2013-2019)
# RETURN Annual Population Estimates. The reference date for all estimates is July 1
"""https://api.census.gov/data/2014/pep/natstprc?get=STNAME,POP&for=us:*&DATE_=7&key=6d04c5842f4f5fc4d6a4c68dfc07072389af07c8&key=6d04c5842f4f5fc4d6a4c68dfc07072389af07c8
api_link = 'http://api.census.gov/data/2000/pep/int_natmonthly?get=POP,MONTHLY_DESC&for=us:*&key={}'.format(my_key)
json_result = urllib.request.urlopen(api_link).read()
result = json.loads(json_result)
results.append(result)"""


# In[273]:


# Current Population Survey: Basic Monthly (1989-2022)
# Count the records to get the population
def monthly_count(link):
    json_result = urllib.request.urlopen(link).read()
    monthly_ct = len(json.loads(json_result))
    time.sleep(0.5)
    return monthly_ct

start_time = time.time()

yearly_ct = []
months = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
base_link = 'https://api.census.gov/data'

for year in range(1989, 2023):
    print('Reading Year', str(year))
    s = 'reading Year: {}'.format(str(year))
    v1 = 'A_AGE'
    v2 = 'PRTAGE'
    total_ct = 0
    
    for month in months:
        api_link = '{}/{}/cps/basic/{}?get={}&key={}'.format(base_link,
                                                             str(year), 
                                                             month,
                                                             v1,
                                                             my_key)
        try:
            total_ct += monthly_count(api_link)
        except HTTPError:
            try:
                api_link = '{}/{}/cps/basic/{}?get={}&key={}'.format(base_link,
                                                                     str(year),
                                                                     month,
                                                                     v2,
                                                                     my_key)
                total_ct += monthly_count(api_link)
            except:
                print('Failed in Year {} Month {}'.format(str(year), month.upper()))
    yearly_ct.append(total_ct)
    print('Done!')

end_time = time.time()
print('Elapsed Time: {} minutes.'.format(str((end_time - start_time)/60)))


# Variable in different years changed e.g failed in 1994 because `A_AGE` (demographic-age) is no longer available. For a more dynamic solution, from 1995, I changed to use `PRTAGE` (Demographics - age topcoded at 85, 90 or 80).
# 
# - Variable dictionary for pre-1994: https://api.census.gov/data/1993/cps/basic/oct/variables.html
# 
# - Variable dictionary for post-1994: https://api.census.gov/data/1994/cps/basic/apr/variables.html

# In[274]:


len(yearly_ct)


# **MATCH!!** 1989 through 2022 = 34 years

# In[275]:


yearly_ct


# These numbers are too low to be correct. I have to find another method.

# In[276]:


# 1990 Population Estimates - 1990-2000 Intercensal Estimates: United States Resident Population Estimates by Age and Sex
api_link = 'https://api.census.gov/data/1990/pep/int_natrespop?get=YEAR,TOT_POP&key={}'.format(my_key)
json_result = urllib.request.urlopen(api_link).read()
results = json.loads(json_result)
    


# In[277]:


results[:2]


# In[278]:


yearly_ct = {}
for i in results[1:]:
    yearly_ct[int(i[0])] = int(i[1])

yearly_ct.keys()


# In[279]:


# 2000 Population Estimates - 2000-2010 Intercensal Estimates: Population
api_link = 'https://api.census.gov/data/2000/pep/int_population?get=GEONAME,POP,DATE_&for=us:1&key={}'.format(my_key)
json_result = urllib.request.urlopen(api_link).read()
results = json.loads(json_result)
    


# In[280]:


results[:2]


# In[281]:


# the first year is 2000, so add 1999. This overwrites year 2000 from the last method
for i in results[1:]:
    yearly_ct[1999+int(i[2])] = int(i[1])

yearly_ct.keys()


# In[282]:


# 2012 National Population Projections: Projected Population by Single Year of Age
year = 2012
api_link = '{}/{}/popproj/pop?get=YEAR,TOTAL_POP&key={}'.format(base_link, str(year), my_key)
json_result = urllib.request.urlopen(api_link).read()
results = json.loads(json_result)
yearly_ct[year] = int(results[1][1])

yearly_ct.keys()


# In[283]:


def get_result(link):
    json_result = urllib.request.urlopen(link).read()
    results = json.loads(json_result)
    time.sleep(0.5)
    return int(results[1][1])


# In[284]:


## 2013 - 2014: Vintage XXXX Population Estimates: US, State, and PR Total Population and Components of Change
# tricky part: 2013's DATE_ is 6 vs. 2014's DATE_ is 7, reason unknown yet

for year in range(2013, 2015):
    api_link = '{}/{}/pep/natstprc?get=STNAME,POP&for=us:*&DATE_={}&key={}'.format(base_link, 
                                                                                   str(year), 
                                                                                   str(year-2007),
                                                                                   my_key)
    yearly_ct[year] = get_result(api_link)


# In[285]:


# 2015 - 2021: Vintage XXXX Population Estimates: Population Estimates
for year in range(2015, 2022):
    v1 = 'GEONAME'
    v2 = 'NAME'
    v3 = 'POP_'+str(year)

    api_link = '{}/{}/pep/population?get={},POP&for=us:*&key={}'.format(base_link, 
                                                                        str(year),
                                                                        v1,
                                                                        my_key)
    try:
        yearly_ct[year] = get_result(api_link)
    except:
        try:
            api_link = '{}/{}/pep/population?get={},POP&for=us:*&key={}'.format(base_link,
                                                                                str(year),
                                                                                v2,
                                                                                my_key)                                                                                            
            yearly_ct[year] = get_result(api_link)
        except: 
            try:
                api_link = '{}/{}/pep/population?get={},{}&for=us:*&key={}'.format(base_link,
                                                                                    str(year),
                                                                                    v2,
                                                                                    v3,
                                                                                    my_key)                                                                                            
                yearly_ct[year] = get_result(api_link)
            except: 
                yearly_ct[year] = 0
    
yearly_ct


# In[303]:


df = pd.DataFrame({'Year':yearly_ct.keys(), 'Pop':yearly_ct.values()})
df = df[df['Pop']!=0]
df['Population (Millions)'] = df['Pop'].apply(lambda x: x/1000000)
sns.relplot(data=df, x='Year', y = 'Population (Millions)', kind='line')#, height = 6, aspect = 0.7)
plt.ylim(0)
plt.title('US Population')

# label the data points at the first and last year
max_year = df['Year'].max()
max_year_val = df.loc[df['Year'] == max_year, 'Population (Millions)']
plt.gca().text(x = max_year, y = max_year_val - 15, 
               s = str(int(max_year_val.values)))    
min_year = df['Year'].min()
min_year_val = df.loc[df['Year'] == min_year, 'Population (Millions)']
plt.gca().text(x = df['Year'].min(), y = min_year_val - 15, 
               s = str(int(min_year_val.values)))    


# The US population has increased by around 33% since 1990. By comparison, the relatively high-increasing meat consumption, especially 250% in broilers, is quite worrying and alarming. No wonder Chick-fil-A has more than 4 drive-thru lanes and people are lining up all the time. 

# In[ ]:




