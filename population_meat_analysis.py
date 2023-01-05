#!/usr/bin/env python
# coding: utf-8

# In[70]:


import pandas as pd
import numpy as np
import re
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from urllib import request 
from urllib.error import HTTPError
import json
import time


# ## Meat Production

# In[9]:


xlsx = pd.ExcelFile('data/meat_statistics.xlsx')


# The original excel file was designed for human readable, including merged cells for the first category (a.k.a Commerical vs. Federally Inspected below) and then individual cells for the secondary category (a.k.a row 0). 

# In[10]:


raw_data = pd.read_excel(xlsx, sheet_name = 'RedMeatPoultry_Prod-Full', header = 1)
raw_data.head()


# There are two types - Commerical vs. Federally Inspected. Their numbers are pretty close. I decided to use the numbers under Federally Inspected because it contains more information in terms of meat types. 

# In[11]:


idx = list(raw_data.columns).index('Federally inspected')
idxs = [0]
for i in range(len(raw_data.columns)):
    if i >= idx:
        idxs.append(i)


# In[12]:


raw_data = raw_data.iloc[:, idxs]
raw_data.head()


# Replace the current header with the first row (a.k.a the secondary categories) and remove the empty column

# In[13]:


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

# In[14]:


current_header = raw_data.columns[1:] 
transformed_header = ['Month']
for i in current_header:
    word = re.search('\D+', i).group().strip().replace(' ', '_')
    transformed_header.append(word.lower())
raw_data.columns = transformed_header
raw_data.head()


# Remove the rows containing additional information

# In[15]:


raw_data.tail(10)


# In[16]:


trim_data = raw_data[~raw_data['Month'].str.contains('/ |Source|Date run')]
trim_data.tail()


# Drop columns for aggregation information and the type of `Other Chicken`

# In[17]:


trim_data = trim_data.iloc[:, [0,1,2,3,4,6,8]]
trim_data.head()


# Keep only the monthly data and then convert to datetime data type

# In[18]:


trim_data.head()


# In[19]:


meat_prod = trim_data.copy()
meat_prod = meat_prod[meat_prod['Month'].str.contains(r'\w{3}-\d{4}', regex=True)]
meat_prod.head()


# In[20]:


meat_prod['Month'] = meat_prod['Month'].apply(lambda x: datetime.strptime(x, '%b-%Y'))
meat_prod.head()


# In[21]:


meat_prod.info()


# In[22]:


# outliers in 1982 and 1948, data unavailabe between 1957 and 1976
sns.relplot(data=meat_prod, x='Month', y = 'beef')


# In[23]:


# 1982 some categories only have quartly data, 1948 December had no clear reasoning
meat_prod.loc[meat_prod['Month'].dt.year==1982, :]


# In[24]:


for i in ['beef', 'veal', 'pork', 'lamb_and_mutton']:
    meat_prod[i] = meat_prod.apply(lambda x: x[i]/3 if x['Month'].year==1982 else x[i], axis = 1)

meat_prod.loc[meat_prod['Month'].dt.year==1982, :]


# In[25]:


# split in 3 evenly and forward fill in missing data 
meat_prod = meat_prod.fillna(method='ffill', limit=2)

meat_prod.loc[meat_prod['Month'].dt.year==1982, :]


# In[26]:


# smooth out the outliers in 1982, drop the outlier in 1948
sns.relplot(data=meat_prod, x='Month', y = 'beef', kind='line')


# In[27]:


# transform the data to visualize on one chart
meat_prod2 = pd.melt(meat_prod, id_vars=['Month'], value_vars=meat_prod.columns[1:])


# In[28]:


g = sns.relplot(data=meat_prod2.rename(columns={'variable':'Types'}), x='Month', y = 'value', 
                kind='line', hue='Types',height=6, aspect=2)
# extract yearly labels every five year
yearly_labels = sorted(list(meat_prod.loc[meat_prod['Month'].dt.month == 1, 'Month'].dt.year.astype(str)))
# display xtick labels every five year at 0 or 5
g.set(xticks=[yearly_labels[i+4] for i in range(0, len(yearly_labels)-4, 5)])
g.set(xticklabels=[yearly_labels[i+4] for i in range(0, len(yearly_labels)-4, 5)])
g.set(xlabel='Year', ylabel='Million Pounds')
g.set(title='Meat Production')


# ## Slaughter Counts

# The original excel file was designed for human readable, including merged cells for the first category (a.k.a Commerical vs. Federally Inspected below) and then individual cells for the secondary category (a.k.a row 0). 

# In[29]:


raw_data2 = pd.read_excel(xlsx, sheet_name = 'SlaughterCounts-Full', header = 1)
raw_data2.head()


# There are two types - Commerical vs. Federally Inspected. Their numbers are pretty close. I decided to use the numbers under Federally Inspected because it contains more information in terms of meat types. 

# In[30]:


idx = list(raw_data2.columns).index('Federally inspected 3/')
idxs = [0]
for i in range(len(raw_data2.columns)):
    if i >= idx:
        idxs.append(i)


# In[31]:


raw_data2 = raw_data2.iloc[:, idxs]
print(raw_data2.shape)
raw_data2.head()


# Replace the current header with the first row (a.k.a the secondary categories) and remove the empty column

# In[32]:


new_header = raw_data2.iloc[0, :]
raw_data2 = raw_data2.iloc[1:, :]
raw_data2.columns = new_header
raw_data2.head()


# Transform the header by removing space and punctuations													

# In[33]:


current_header = raw_data2.columns[1:] 
transformed_header = ['Month']
for i in current_header:
    word = re.search('[A-Z]\D+', i).group().strip().replace(' ', '_')
    transformed_header.append(word.lower())
raw_data2.columns = transformed_header
raw_data2.head()


# Remove the rows containing additional information

# In[34]:


raw_data2.tail(5)


# In[35]:


trim_data2 = raw_data2.dropna(thresh=3) # keep only rows containing 3+ observations
trim_data2.tail(5)


# Keep columns for more common types

# In[36]:


trim_data2 = trim_data2.iloc[:, [0,1,3,4,7,8,12,15,17]]
trim_data2.head()


# Keep only the monthly data and then convert to datetime data type

# In[37]:


slau_count = trim_data2.copy()
slau_count = slau_count[slau_count['Month'].str.contains(r'\w{3}-\d{4}', regex=True)]
slau_count.head()


# In[38]:


slau_count['Month'] = slau_count['Month'].apply(lambda x: datetime.strptime(x, '%b-%Y'))
slau_count.head()


# In[39]:


# outliers in 1982 
sns.relplot(data=slau_count, x='Month', y = 'cattle')


# In[40]:


# 1982 some categories only have quartly data
slau_count.loc[slau_count['Month'].dt.year==1982, :]


# In[41]:


for i in ['cattle', 'heifers', 'hogs', 'sheep_and_lambs']:
    slau_count[i] = slau_count.apply(lambda x: x[i]/3 if x['Month'].year==1982 else x[i], axis = 1)

slau_count.loc[slau_count['Month'].dt.year==1982, :]


# In[42]:


# split in 3 evenly and forward fill in missing data 
slau_count = slau_count.fillna(method='ffill', limit=2)

slau_count.loc[slau_count['Month'].dt.year==1982, :]


# In[43]:


# smooth out the outliers in 1982, drop the outlier in 1948
sns.relplot(data=slau_count, x='Month', y = 'cattle', kind='line')


# In[44]:


# transform the data to visualize on one chart
slau_count2 = pd.melt(slau_count, id_vars=['Month'], value_vars=slau_count.columns[1:])
slau_count2 = slau_count2.rename(columns={'variable':'Types'})


# In[45]:


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

# ## Slaughter Weights

# The original excel file was designed for human readable, including merged cells for the first category (a.k.a Commerical vs. Federally Inspected below) and then individual cells for the secondary category (a.k.a row 0). 

# In[46]:


raw_data3 = pd.read_excel(xlsx, sheet_name = 'SlaughterWeights-Full', header = 1)
raw_data3.head()


# There are three types - `Commercial average live`, `Federally inspected average live`, and `Federally inspected average dressed`. Two average live numbers are pretty close and relatively higher than the average dressed numbers. I decided to use the numbers under Federally Inspected average live because it contains the critical category - broilers.

# In[47]:


idx = list(raw_data3.columns).index('Federally inspected average live')
end_idx = list(raw_data3.columns).index('Federally inspected average dressed 3/')
idxs = [0]
for i in range(len(raw_data3.columns)):
    if i >= idx and i < end_idx:
        idxs.append(i)


# In[48]:


raw_data3 = raw_data3.iloc[:, idxs]
print(raw_data3.shape)
raw_data3.head()


# Replace the current header with the first row (a.k.a the secondary categories) and remove the empty column

# In[49]:


new_header = raw_data3.iloc[0, :]
raw_data3 = raw_data3.iloc[1:, :]
raw_data3.columns = new_header
raw_data3.head()


# Transform the header by removing space and punctuations													

# In[50]:


current_header = raw_data3.columns[1:] 
transformed_header = ['Month']
for i in current_header:
    word = re.search('\D+', i).group().strip().replace(' ', '_')
    transformed_header.append(word.lower())
raw_data3.columns = transformed_header
raw_data3.head()


# Remove the rows containing additional information

# In[51]:


raw_data3.tail(5)


# In[52]:


trim_data3 = raw_data3.dropna(thresh=3) # keep only rows containing 3+ observations
trim_data3.tail(5)


# Keep columns for more common types

# In[53]:


trim_data3 = trim_data3.iloc[:, [0,1,2,3,4,5,7]]
trim_data3.head()


# Keep only the monthly data and then convert to datetime data type

# In[54]:


slau_avg_weight = trim_data3.copy()
slau_avg_weight = slau_avg_weight[slau_avg_weight['Month'].str.contains(r'\w{3}-\d{4}', regex=True)]
slau_avg_weight.head()


# In[55]:


slau_avg_weight['Month'] = slau_avg_weight['Month'].apply(lambda x: datetime.strptime(x, '%b-%Y'))
slau_avg_weight.head()


# In[56]:


# no outliers because it is not aggregated like count or production
sns.relplot(data=slau_avg_weight, x='Month', y = 'cattle')


# In[57]:


# transform the data to visualize on one chart
slau_avg_weight2 = pd.melt(slau_avg_weight, id_vars=['Month'], value_vars=slau_avg_weight.columns[1:])\
.rename(columns={'value':'average_weight', 'variable':'Types'})
# forward fill in missing value to get rid of nan values in the middle
slau_avg_weight2 = slau_avg_weight2.fillna(method='ffill', limit=2)


# In[58]:


# combine average weight and count information
slau_weight = pd.merge(left = slau_avg_weight2, right = slau_count2.rename(columns={'value':'count'}), on = ['Month', 'Types'])
slau_weight.head()


# In[59]:


# calculate total weight
slau_weight['weight_in_thousands'] =  slau_weight['average_weight'] * slau_weight['count'] / 1000
slau_weight.head()


# In[60]:


# drop rows containing any missing values
print(slau_weight.shape)
slau_weight2 = slau_weight.dropna()
print(slau_weight2.shape)


# In[61]:


g = sns.relplot(data=slau_weight2, x='Month', y = 'weight_in_thousands', kind='line', hue='Types',height=6, aspect=2)
# extract yearly labels every five year
yearly_labels = sorted(list(slau_avg_weight.loc[slau_avg_weight['Month'].dt.month == 1, 'Month'].dt.year.astype(str)))
# display xtick labels every five year at 0 or 5
g.set(xticks=[yearly_labels[i+4] for i in range(0, len(yearly_labels)-4, 5)])
g.set(xticklabels=[yearly_labels[i+4] for i in range(0, len(yearly_labels)-4, 5)])
g.set(xlabel='Year', ylabel='Thousand Pounds')
g.set(title='Slaughter Weight')


# ## US Population (Census Data API)                       

# ![image-2.png](attachment:image-2.png)

# ![image.png](attachment:image.png)

# In[62]:


my_key = '6d04c5842f4f5fc4d6a4c68dfc07072389af07c8'


# In[63]:


# 2000 Population Estimates - 2000-2010 Intercensal Estimates: National Monthly Population Estimates
# ONLY RETURN 2000-2010 DATA
api_link = 'http://api.census.gov/data/2000/pep/int_natmonthly?get=POP,MONTHLY_DESC&for=us:1&key={}'.format(my_key)
json_result = urllib.request.urlopen(api_link).read()
result1 = json.loads(json_result)
result1


# In[64]:


# Vintage Population Estimates: US, State, and PR Total Population and Components of Change (2013-2019)
# RETURN Annual Population Estimates. The reference date for all estimates is July 1
"""https://api.census.gov/data/2014/pep/natstprc?get=STNAME,POP&for=us:*&DATE_=7&key=6d04c5842f4f5fc4d6a4c68dfc07072389af07c8&key=6d04c5842f4f5fc4d6a4c68dfc07072389af07c8
api_link = 'http://api.census.gov/data/2000/pep/int_natmonthly?get=POP,MONTHLY_DESC&for=us:*&key={}'.format(my_key)
json_result = urllib.request.urlopen(api_link).read()
result = json.loads(json_result)
results.append(result)"""


# In[101]:


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

# In[103]:


len(yearly_ct)


# **MATCH!!** 1989 through 2022 = 34 years

# In[104]:


yearly_ct


# These numbers are too low to be correct. I have to find another method.

# In[186]:


# 1990 Population Estimates - 1990-2000 Intercensal Estimates: United States Resident Population Estimates by Age and Sex
api_link = 'https://api.census.gov/data/1990/pep/int_natrespop?get=YEAR,TOT_POP&key={}'.format(my_key)
json_result = urllib.request.urlopen(api_link).read()
results = json.loads(json_result)
    


# In[187]:


results[:2]


# In[188]:


yearly_ct = {}
for i in results[1:]:
    yearly_ct[int(i[0])] = int(i[1])

yearly_ct.keys()


# In[189]:


# 2000 Population Estimates - 2000-2010 Intercensal Estimates: Population
api_link = 'https://api.census.gov/data/2000/pep/int_population?get=GEONAME,POP,DATE_&for=us:1&key={}'.format(my_key)
json_result = urllib.request.urlopen(api_link).read()
results = json.loads(json_result)
    


# In[190]:


results[:2]


# In[191]:


# the first year is 2000, so add 1999. This overwrites year 2000 from the last method
for i in results[1:]:
    yearly_ct[1999+int(i[2])] = int(i[1])

yearly_ct.keys()


# In[194]:


# 2012 National Population Projections: Projected Population by Single Year of Age
year = 2012
api_link = '{}/{}/popproj/pop?get=YEAR,TOTAL_POP&key={}'.format(base_link, str(year), my_key)
json_result = urllib.request.urlopen(api_link).read()
results = json.loads(json_result)
yearly_ct[year] = int(results[1][1])

yearly_ct.keys()


# In[196]:


def get_result(link):
    json_result = urllib.request.urlopen(link).read()
    results = json.loads(json_result)
    time.sleep(0.5)
    return int(results[1][1])


# In[197]:


## 2013 - 2014: Vintage XXXX Population Estimates: US, State, and PR Total Population and Components of Change
# tricky part: 2013's DATE_ is 6 vs. 2014's DATE_ is 7, reason unknown yet

for year in range(2013, 2015):
    api_link = '{}/{}/pep/natstprc?get=STNAME,POP&for=us:*&DATE_={}&key={}'.format(base_link, 
                                                                                   str(year), 
                                                                                   str(year-2007),
                                                                                   my_key)
    yearly_ct[year] = get_result(api_link)


# In[198]:


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


# In[209]:


df = pd.DataFrame({'Year':yearly_ct.keys(), 'Pop':yearly_ct.values()})
df = df[df['Pop']!=0]
df['Population (Millions)'] = df['Pop'].apply(lambda x: x/1000000)
sns.relplot(data=df, x='Year', y = 'Population (Millions)', kind='line')
plt.ylim(0)


# In[ ]:




