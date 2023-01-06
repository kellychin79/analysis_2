Repo for analyzing US population and meat consumption

# Statement
I am a failed vegetarian. I am also a data analyst that wants to look into open-source data and figure out something about this world. So I decided to take on an uneasy and comfortable topic - the relationship between meat consumption and population. 

# Assumptions
- The problem you decided to investigate
	- How much of the US population is vegetarian? Has it increased or remained? (KL: Increase)
	- Has the increase rate of meat consumption in the US surpass the growth rate of US population? (KL: Yes) By type?
	- For the increasing meat consumption, have more livestock been slaughtered or only more weights been processed? (KL: by 1990 more weights after 2000 more livestock) By type?
- How you are going to analyze data to answer that question
	- Combine the population data and Livestock and Meat Domestic Data from US Department of Agriculture 
- The results of your analysis, including how your visualizations are relevant and useful
- Suggestions for future research, including improvements to what you did (KL: Predict the C02 emissions from the numbers of livestock)

# Summary
The US population has increased by around 33% since 1990. By comparison, the relatively high-increasing meat consumption, especially 250% in broilers, is quite worrying and alarming. No wonder Chick-fil-A has more than 4 drive-thru lanes and people are lining up all the time. 


# Data Source
### Meat Data: U.S. Department of Agriculture 
https://www.ers.usda.gov/data-products/livestock-and-meat-domestic-data/

### Population Data: United States Census Bureau
https://www.census.gov/programs-surveys/popest/data/data-sets.html
I found a cool stuff - Census Data API. 
https://www.census.gov/data/developers/about.html
It is a data service that enables software developers to access and use Census Bureau data within their applications that provide users quick and easy access from an every increasing pool of publicly available datasets.
By scrutinizing the discovery tool, https://api.census.gov/data.html, I identified a handful of API base URLs that can be used in my analysis. A good understanding of dataset name helped me to grasp the nature of the API calls. Unfortunately, the data has no consistent design logic over the past three decades. Considering the drastic change of information technologies, the messy API endpoints and URLs are no one's faults.
- 2000 Population Estimates - 2000-2010 Intercensal Estimates
`http://api.census.gov/data/2000/pep/int_natmonthly?get=POP,MONTHLY_DESC&for=us:1&key={}'.format(my_key)`
- Vintage Population Estimates
`https://api.census.gov/data/2014/pep/natstprc?get=STNAME,POP&for=us:*&DATE_=7&key={}'.format(my_key)`
- Current Population Survey: Basic Monthly
`https://api.census.gov/data/1989/cps/basic/apr?get=A_AGE&key={}'`
After a few trials and seeing the results, I realized that this one reveals population survey data (a.k.a `CPS`) instead of the entire population data.
- 1990 Population Estimates - 1990-2000 Intercensal Estimates: United States Resident Population Estimates by Age and Sex
`https://api.census.gov/data/1990/pep/int_natrespop?get=YEAR,TOT_POP&key={}`

## Appendix
#### Terms of Meat Term
https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:Meat_production#:~:text=Meat%20production%20refers%20to%20the,%2C%20pork%2C%20lamb%20and%20mutton.
- Meat production: refers to the slaughter, in slaughterhouses and farms, of animals whose carcass is declared fit for human consumption. The definition applies to beef, pork, lamb and mutton.
https://beef2live.com/story-glossary-terms-livestock-slaughter-85-105350#:~:text=Average%20Live%20Weight%3A%20The%20weight,excludes%20animals%20slaughtered%20on%20farms.
- Commercial Production: Includes slaughter and meat production in federally inspected and other plants, but excludes animals slaughtered on farms. 
- Dressed Weight: The weight of a chilled animal carcass. Beef with kidney knob in; veal with hide off; lamb and mutton with pluck out; pork with leaf fat and kidneys out, jowls on and head off.

#### FIPS Code for the States and District of Columbia
https://www.census.gov/library/reference/code-lists/ansi/ansi-codes-for-states.html
Some API calls require FIPS code so I did some research about it even though it is not used in the final analysis. Although there are only 50 states, FIPS codes go up to 56.

