#!/usr/bin/env python
# coding: utf-8

# In[85]:


import pandas as pd
import numpy as np
import re


# In[7]:


xlsx = pd.ExcelFile('meat_statistics.xlsx')


# The original excel file was designed for human readable, including merged cells for the first category (a.k.a Commerical vs. Federally Inspected below) and then individual cells for the secondary category (a.k.a row 0). 

# In[80]:


raw_data = pd.read_excel(xlsx, sheet_name = 'RedMeatPoultry_Prod-Full', header = 1)
raw_data.head()


# There are two types - Commerical vs. Federally Inspected. Their numbers are pretty close. I decided to use the numbers under Federally Inspected because it contains more information in terms of meat types. 

# In[81]:


idx = list(raw_data.columns).index('Federally inspected')
idxs = [0]
for i in range(len(raw_data.columns)):
    if i >= idx:
        idxs.append(i)


# In[82]:


raw_data = raw_data.iloc[:, idxs]
raw_data.head()


# Replace the current header with the first row (a.k.a the secondary categories) and remove the empty column

# In[83]:


new_header = raw_data.iloc[0, :-1]
meat_prod = raw_data.iloc[1:, :-1]
meat_prod.columns = new_header
meat_prod.head()


# Transform the header by removing space and notation, explained below
# - 1/ Excludes slaughter on farms.																
# - 2/ Production in federally inspected and other plants.															
# - 3/ Based on packers' dressed weights.																
# - 4/ Totals may not add due to rounding.																
# - 5/ Ready-to-cook.																
# - 6/ Includes geese, guineas, ostriches, emus, rheas, squab, and other poultry.																

# In[84]:


current_header = meat_prod.columns[1:] 
transformed_header = ['Month']
for i in current_header:
    transformed_header.append(word.lower())
meat_prod.columns = transformed_header
meat_prod.head()


# In[ ]:




