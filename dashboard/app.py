# Import packages
from dash import Dash, html, dash_table, dcc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from spiderChart import spider
from lineChart import time_series


# Function to format date columns
def clean_dates(col):
    return pd.to_datetime(col.str.split(' ').str[0], format='mixed')

# Reading in data files and cleaning
# WHO
who = pd.read_csv('~\Downloads\Capstone\capstone\data\who_merged.csv')
who['assessment_date'] = clean_dates(who['assessment_date'])
who['score'] = who.iloc[:, -5:].sum(axis=1)
who.sort_values(['initial_group_identifier', 'assessment_date'], inplace=True)


# GAD
gad = pd.read_csv('~\Downloads\Capstone\capstone\data\gad_merged.csv')
gad['assessment_date'] = clean_dates(gad['assessment_date'])
# combining duplicate column
gad['5. * Being so restless that it is too hard to sit still'] = gad['5. * Being so restless that it is too hard to sit still'].combine_first(
  gad['5. * Being so restless that it’s hard to sit still'])
gad.drop('5. * Being so restless that it’s hard to sit still', inplace=True, axis=1)

gad['score'] = gad.iloc[:, -7:].sum(axis=1)
gad.sort_values(['initial_group_identifier', 'assessment_date'], inplace=True)


# PHQ
phq = pd.read_csv('~\Downloads\Capstone\capstone\data\phq_merged.csv')
phq['assessment_date'] = clean_dates(phq['assessment_date'])
phq['score'] = phq.iloc[:, -9:].sum(axis=1)
phq.sort_values(['initial_group_identifier', 'assessment_date'], inplace=True)


# PCL
pcl = pd.read_csv('~\Downloads\Capstone\capstone\data\ptsd_merged.csv')
pcl['assessment_date'] = clean_dates(pcl['assessment_date'])
pcl['score'] = pcl.iloc[:, -20:].sum(axis=1)
pcl.sort_values(['initial_group_identifier', 'assessment_date'], inplace=True)


# DERS
# some questions in DERS have reverse scoring
reversed = [1,2,6,7,8,10,17,20,22,24,34]
reversed_elements = [str(x) for x in reversed]

ders = pd.read_csv('~\Downloads\Capstone\capstone\data\ders_merged.csv')
ders['assessment_date'] = clean_dates(ders['assessment_date'])

ders['score'] = ders.iloc[:, -36:].sum(axis=1)
ders.sort_values(['initial_group_identifier', 'assessment_date'], inplace=True)

# DERS2
ders2 = pd.read_csv('~\Downloads\Capstone\capstone\data\ders2_merged.csv')
ders2['assessment_date'] = clean_dates(ders2['assessment_date'])

# reveres scored questions in DERS2 files need to be reformatted
reverse_cols2 = ders2.loc[:, ders2.columns.str.split('.').str[0].isin(reversed_elements)].columns
mapping = {"'-1":1,"'-2":2,"'-3":3,"'-4":4,"'-5":5}
ders2[reverse_cols2] = ders2[reverse_cols2].replace(mapping)

ders2['score'] = ders2.iloc[:, -36:].sum(axis=1)
ders2.sort_values(['initial_group_identifier', 'assessment_date'], inplace=True)

# Combining DERS files
ders2.columns=ders.columns
ders = pd.concat([ders,ders2])
ders.sort_values(['initial_group_identifier', 'assessment_date'], inplace=True)

# Combine all assessment data to one dataframe
cols = ['initial_group_identifier', 'assessment_date', 'score']
assessments = ['WHO', 'GAD', 'PHQ', 'PCL', 'DERS']

df = who[cols].merge(gad[cols], how='outer', on=['initial_group_identifier', 'assessment_date'], suffixes=('_WHO', '_GAD'))
df = df.merge(phq[cols], how='outer', on=['initial_group_identifier', 'assessment_date'], suffixes=(None, '_PHQ'))
df = df.merge(pcl[cols], how='outer', on=['initial_group_identifier', 'assessment_date'], suffixes=(None, '_PCL'))
df = df.merge(ders[cols], how='outer', on=['initial_group_identifier', 'assessment_date'], suffixes=(None, '_DERS'))
df.columns = ['initial_group_identifier', 'assessment_date'] + assessments

scores = df.groupby('initial_group_identifier')[assessments].mean()

# Total possible score for each assessment
totals = [25.0, 21.0, 27.0, 80.0, 180.0]

# Select a patient --NOTE: need to make this dynamic
patient_id = '45f6c6e54bbf'

# Creating a radar chart of assessment scores for a single patient
radar_chart = spider(scores, totals,
                     assessments, patient_id,
                     'Assessment Scores for Patient: ' + patient_id)

line_chart = time_series(df, 'WHO', patient_id)

# Initialize the app
app = Dash()

# App layout
app.layout = [
    dash_table.DataTable(data=df.to_dict('records'), page_size=10),
    dcc.Graph(figure=radar_chart),
    dcc.Graph(figure=line_chart)
]

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
