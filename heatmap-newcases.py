import numpy as np
import seaborn as sns
import matplotlib.pylab as plt
import pandas as pd
import csv
import datetime

reader = csv.reader(open('StatePopulations.csv'))

statePopulations = {}
for row in reader:
    key = row[0]
    if key in statePopulations:
        pass
    statePopulations[key] = row[1:]

filename = "us-states.csv"
fullTable = pd.read_csv(filename)
fullTable = fullTable.drop(['fips'], axis=1)
fullTable = fullTable.drop(['deaths'], axis=1)

# generate a list of the dates in the table
dates = fullTable['date'].unique().tolist()
states = fullTable['state'].unique().tolist()

result = pd.DataFrame()
result['date'] = fullTable['date']

states.remove('Northern Mariana Islands')
states.remove('Puerto Rico')
states.remove('Virgin Islands')
states.remove('Guam')

states.sort()

for state in states:
    # create new dataframe with only the current state's date
    population = int(statePopulations[state][0])
    print(state + ": " + str(population))
    stateData = fullTable[fullTable.state.eq(state)]

    newColumnName = state
    stateData[newColumnName] = stateData.cases.diff()
    stateData[newColumnName] = stateData[newColumnName].replace(np.nan, 0)
    stateData = stateData.drop(['state'], axis=1)
    stateData = stateData.drop(['cases'], axis=1)

    stateData[newColumnName] = stateData[newColumnName].div(population)
    stateData[newColumnName] = stateData[newColumnName].mul(100000.0)

    result = pd.merge(result, stateData, how='left', on='date')

result = result.drop_duplicates()
result = result.fillna(0)

for state in states:
    result[state] = result[state].add(1.0)
    result[state] = np.log10(result[state])
    #result[state] = np.sqrt(result[state])

result['date'] = pd.to_datetime(result['date'])
result = result[result['date'] >= '2020-02-15']
result['date'] = result['date'].dt.strftime('%Y-%m-%d')

result.set_index('date', inplace=True)
result.to_csv("result.csv")
result = result.transpose()

plt.figure(figsize=(16, 10))
g = sns.heatmap(result, cmap="coolwarm", linewidth=0.05, linecolor='lightgrey')
plt.xlabel('')
plt.ylabel('')

plt.title("Daily New Covid-19 Cases Per 100k Of Population", fontsize=20)

updateText = "Updated " + str(datetime.date.today()) + \
    ". Scaled with Log(x+1) for improved contrast due to wide range of values. Data source: NY Times Github. Visualization by @JRBowling"

plt.suptitle(updateText, fontsize=8)

plt.yticks(np.arange(.5, 51.5, 1.0), states)

plt.yticks(fontsize=8)
plt.xticks(fontsize=8)
g.set_xticklabels(g.get_xticklabels(), rotation=90)
g.set_yticklabels(g.get_yticklabels(), rotation=0)
plt.savefig("covidNewCasesper100K.png")
