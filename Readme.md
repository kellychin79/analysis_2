Repo for analyzing US population and meat consumption

# Question
- The problem you decided to investigate
	- How much of the US population is vegetarian? Has it increased or remained? (KL: Increase)
	- Has the increase rate of meat consumption in the US surpass the growth rate of US population? (KL: Yes) By type?
	- For the increasing meat consumption, have more livestock been slaughtered or only more weights been processed? (KL: by 1990 more weights after 2000 more livestock) By type?
- How you are going to analyze data to answer that question
	- Combine the population data and Livestock and Meat Domestic Data from US Department of Agriculture 
- The results of your analysis, including how your visualizations are relevant and useful
- Suggestions for future research (including improvements to what you did)
	- Predict the C02 emissions from the numbers of livestock


# Data Source
### Meat Data: U.S. Department of Agriculture 
https://www.ers.usda.gov/data-products/livestock-and-meat-domestic-data/

### Population Data: United States Census Bureau
https://www.census.gov/programs-surveys/popest/data/data-sets.html
I found a cool stuff - Census Data API. 
https://www.census.gov/data/developers/about.html
It is a data service that enables software developers to access and use Census Bureau data within their applications that provide users quick and easy access from an every increasing pool of publicly available datasets.
By examining the discovery tool, https://api.census.gov/data.html, I identified a handful of API base URLs that can be used in my analysis.
- 2000 Population Estimates - 2000-2010 Intercensal Estimates
`http://api.census.gov/data/2000/pep/int_natmonthly?get=POP,MONTHLY_DESC&for=us:1&key={}'.format(my_key)`
- Vintage Population Estimates
`https://api.census.gov/data/2014/pep/natstprc?get=STNAME,POP&for=us:*&DATE_=7&key={}'.format(my_key)`
- Current Population Survey: Basic Monthly
`https://api.census.gov/data/{}/cps/basic/apr?get=A_AGE&key={}'.format(str(year), my_key)`
The third one covers the most time period but the variables in different dataset have changed/evolved throughout the years. I need to find a more dynamic way to count the populate.

# Appendix
Terms of Livestock Slaughter
https://beef2live.com/story-glossary-terms-livestock-slaughter-85-105350#:~:text=Average%20Live%20Weight%3A%20The%20weight,excludes%20animals%20slaughtered%20on%20farms.
- Average Live Weight: The weight of the whole animal, before slaughter. Excludes post-mortem condemnations.
- Commercial Production: Includes slaughter and meat production in federally inspected and other plants, but excludes animals slaughtered on farms. 
- Dressed Weight: The weight of a chilled animal carcass. Beef with kidney knob in; veal with hide off; lamb and mutton with pluck out; pork with leaf fat and kidneys out, jowls on and head off.


