#!/usr/bin/env python
# coding: utf-8

# In[165]:


import pandas as pd
import numpy as np
import re
from datetime import datetime


# In[166]:


xlsx = pd.ExcelFile('data/meat_statistics.xlsx')


# The original excel file was designed for human readable, including merged cells for the first category (a.k.a Commerical vs. Federally Inspected below) and then individual cells for the secondary category (a.k.a row 0). 

# In[167]:


raw_data = pd.read_excel(xlsx, sheet_name = 'RedMeatPoultry_Prod-Full', header = 1)
raw_data.head()


# There are two types - Commerical vs. Federally Inspected. Their numbers are pretty close. I decided to use the numbers under Federally Inspected because it contains more information in terms of meat types. 

# In[168]:


idx = list(raw_data.columns).index('Federally inspected')
idxs = [0]
for i in range(len(raw_data.columns)):
    if i >= idx:
        idxs.append(i)


# In[169]:


raw_data = raw_data.iloc[:, idxs]
raw_data.head()


# Replace the current header with the first row (a.k.a the secondary categories) and remove the empty column

# In[170]:


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

# In[171]:


current_header = raw_data.columns[1:] 
transformed_header = ['Month']
for i in current_header:
    word = re.search('\D+', i).group().strip().replace(' ', '_')
    transformed_header.append(word.lower())
raw_data.columns = transformed_header
raw_data.head()


# Remove the rows containing additional information

# In[172]:


raw_data.tail(10)


# In[175]:


trim_data = raw_data[~raw_data['Month'].str.contains('/ |Source|Date run')]
trim_data.tail()


# Keep only the monthly data and then convert to datetime data type

# In[185]:


trim_data.head()


# In[184]:


meat_prod = trim_data.copy()
meat_prod = meat_prod[meat_prod['Month'].str.contains(r'\w{3}-\d{4}', regex=True)]
meat_prod.head()


# In[188]:


meat_prod['Month'] = meat_prod['Month'].apply(lambda x: datetime.strptime(x, '%b-%Y'))
meat_prod.head()


# In[189]:


meat_prod.info()


# In[ ]:




