from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

def load_data(data_file: str) -> pd.DataFrame:
    '''
    Load data from /data directory
    '''
    PATH = pathlib.Path(__file__).parent
    DATA_PATH = PATH.joinpath("data").resolve()
    return pd.read_csv(DATA_PATH.joinpath(data_file))

# Function to format date columns
def clean_dates(col):
    return pd.to_datetime(col.str.split(" ").str[0], format="mixed")


# Reading data
who = pd.read_csv("data/who_merged.csv")
gad = pd.read_csv("data/gad_merged.csv")
phq = pd.read_csv("data/phq_merged.csv")
pcl = pd.read_csv("data/ptsd_merged.csv")
ders = pd.read_csv("data/ders_merged.csv")

# Cleaning data (same as before)
# WHO

who["assessment_date"] = clean_dates(who["assessment_date"])
who["score"] = who.iloc[:, -5:].sum(axis=1)
who.sort_values(["initial_group_identifier", "assessment_date"], inplace=True)

# GAD

gad["assessment_date"] = clean_dates(gad["assessment_date"])
gad["5. * Being so restless that it is too hard to sit still"] = gad[
    "5. * Being so restless that it is too hard to sit still"
].combine_first(gad["5. * Being so restless that it’s hard to sit still"])
gad.drop("5. * Being so restless that it’s hard to sit still", inplace=True, axis=1)
gad["score"] = gad.iloc[:, -7:].sum(axis=1)
gad.sort_values(["initial_group_identifier", "assessment_date"], inplace=True)

# PHQ

phq["assessment_date"] = clean_dates(phq["assessment_date"])
phq["score"] = phq.iloc[:, -9:].sum(axis=1)
phq.sort_values(["initial_group_identifier", "assessment_date"], inplace=True)

# PCL

pcl["assessment_date"] = clean_dates(pcl["assessment_date"])
pcl["score"] = pcl.iloc[:, -20:].sum(axis=1)
pcl.sort_values(["initial_group_identifier", "assessment_date"], inplace=True)

# DERS

ders["assessment_date"] = clean_dates(ders["assessment_date"])
ders["score"] = ders.iloc[:, -36:].sum(axis=1)
ders.sort_values(["initial_group_identifier", "assessment_date"], inplace=True)

# Combine all assessment data into one dataframe
cols = ["initial_group_identifier", "assessment_date", "score"]
assessments = ["WHO", "GAD", "PHQ", "PCL", "DERS"]
df = who[cols].merge(
    gad[cols],
    how="outer",
    on=["initial_group_identifier", "assessment_date"],
    suffixes=("_WHO", "_GAD"),
)
df = df.merge(
    phq[cols],
    how="outer",
    on=["initial_group_identifier", "assessment_date"],
    suffixes=(None, "_PHQ"),
)
df = df.merge(
    pcl[cols],
    how="outer",
    on=["initial_group_identifier", "assessment_date"],
    suffixes=(None, "_PCL"),
)
df = df.merge(
    ders[cols],
    how="outer",
    on=["initial_group_identifier", "assessment_date"],
    suffixes=(None, "_DERS"),
)
df.columns = ["initial_group_identifier", "assessment_date"] + assessments

scores = df.groupby("initial_group_identifier")[assessments].mean()

# Total possible score for each assessment
totals = [25.0, 21.0, 27.0, 80.0, 180.0]

