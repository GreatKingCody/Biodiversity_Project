import pandas as pd
import numpy as np
from scipy import stats
from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from scipy.stats import chi2_contingency

observations = pd.read_csv('observations.csv')
species = pd.read_csv('species_info.csv')

# print(observations.head())
# print(species.head())

# print(observations.info())
# print('\n')
# #Observations does not include any nan values
# print(species.info())
# print('\n')
#It appears conservation_status contains nan values

# print(observations.scientific_name.nunique())
#5541 unique scientific names

# print(species.scientific_name.nunique())
#5541 unique scientific names. We could cross reference these with the other table.

# print(observations.park_name.nunique())
#4 unique parks

# print(species.conservation_status.nunique())
#4 conservation_status contains 4 uniques

# print(species.conservation_status.unique())
#Unique values are [nan 'Species of Concern' 'Endangered' 'Threatened' 'In Recovery']
#My guess is that the nan values are == 'non-concerning'

# print(observations.observations.head())
#Observations is not descriptive. When graphed, it needs to be 'number of sitings'.

# print(species.category.nunique())
#7 unique values 

# print(species.category.unique())
#Uniques are ['Mammal' 'Bird' 'Reptile' 'Amphibian' 'Fish' 'Vascular Plant' 'Nonvascular Plant']

species.conservation_status.fillna('Not_Concerning', inplace = True)
species.conservation_status.replace({'Species of Concern': 'Species_of_Concern'}, inplace = True)
species.conservation_status.replace({'In Recovery': 'In_Recovery'}, inplace = True)
# print(species.conservation_status.unique())
#I'm changing some values to make calling these a little easier if I choose to do so.

observations.drop_duplicates(inplace = True)
species.drop_duplicates(inplace = True)
#I noticed we had some duplicates, so lets see if this did anything.

# print(species[species.scientific_name == 'Cervus elaphus'])
#It doesnt appear the overall drop duplicate did anything so we need to go a little further into depth.

species.drop_duplicates(subset = 'scientific_name', inplace = True)
# print(species[species.scientific_name == 'Cervus elaphus'])
#dropping it like this worked it seems. Lets print the info again and see what info we get.

# print(species.info())
#Great, this will make my life easier for data analysis.


# print(species.info())
# print('\n')
# print(observations.info())

df = observations.merge(species, how = 'outer')
#Okay, hard part over, this will merge the two tables together. Makes my life easier.

# print(df.info())
# print(df.sample(10))
#Random sample of the dataset to make sure we are doing everything right. It looks good.


# print(df.conservation_status.unique())
conservation_count = df[df.conservation_status != 'Not_Concerning'].groupby(['conservation_status', 'category'])['scientific_name'].count().unstack()
# print(conservation_count)


#Lets make a plot below for the conservation status of animals:
# conservation_count.plot(kind = 'bar', stacked = True, xlabel = ('Conservation Status'), ylabel = 'Number of Animals', figsize = (10, 8))
# plt.show()
# plt.clf()



# print(df.info())
# print(df.category.unique())


#Creating a boolean column where True = some category of protection and False = Not_Concerning
df['Protected?'] = df.conservation_status != 'Not_Concerning'
# print(df.head())

#Lets make a table to easily compare if the species is protected or not.
protected_groupby = df.groupby(['category', 'Protected?']).scientific_name.nunique().reset_index()
# print(protected_groupby)

#Okay, the previous table didn't look good, lets change that.
protected_pivot = protected_groupby.pivot(index = 'category', columns = 'Protected?', values = 'scientific_name').reset_index()
protected_pivot.columns = ['Category', 'Not_Protected', 'Protected']
# print(protected_pivot)
#Much better. Lets compare them to a whole, meaning convert these values to a percentage.

#Okay so lets add the column and use the calculation from the last table. If your calculation does not work, make sure to reset_index() in the last table after you call pivot()
protected_pivot['Percent_Protected'] = round((protected_pivot.Protected / (protected_pivot.Protected + protected_pivot['Not_Protected'])) * 100, 2)
# print(protected_pivot)



#Let's do some fun statistical tests. This function sets up a chi2 test and was a pain to make.
#Add your df, first category, and second category as arguments to get the pval between the two.
def chi2(df, category1, category2):
    Not_Protected1 = []
    Protected1 = []
    Not_Protected2 = []
    Protected2 = []
    
    
    Not_Protected1.append(protected_pivot.Not_Protected[protected_pivot.Category == category1].reset_index().drop('index', axis = 1).pop('Not_Protected').pop(0))
    Protected1.append((protected_pivot.Protected[protected_pivot.Category == category1].reset_index().drop('index', axis = 1).pop('Protected').pop(0)))
    
    Not_Protected2.append(protected_pivot.Not_Protected[protected_pivot.Category == category2].reset_index().drop('index', axis = 1).pop('Not_Protected').pop(0))
    Protected2.append((protected_pivot.Protected[protected_pivot.Category == category2].reset_index().drop('index', axis = 1).pop('Protected').pop(0)))
    
    np1 = Not_Protected1[0]
    p1 = Protected1[0]
    np2 = Not_Protected2[0]
    p2 = Protected2[0]
    
    array = [np1, p1], [np2, p2]
    
    chi2, pval, dof, expected = chi2_contingency(array)
    print('The pval is between {} and {} is: {}'.format(category1, category2, round(pval, 3)))
        
#This is an example calculation.           
chi2(df, 'Mammal', 'Bird')
#The print out reads: The pval is between Mammal and Bird is: 0.688
#We can see there is no statistical significance at a 95% confidence interval between the two.
