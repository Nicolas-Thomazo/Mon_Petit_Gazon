# %%
import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv
import plotly.express as px
from datetime import datetime
import numpy as np

load_dotenv()
MPG_PATH = os.getenv("MPG_PATH")
DATA_PATH = Path(MPG_PATH, "DATA")
# %%

df = pd.read_csv(f"{DATA_PATH}/")
# %%
old_path = Path(DATA_PATH, "MPGStats_fr_export (3).xlsx")
path_file = Path(DATA_PATH, "export.csv")
# os.rename(old_path, path_file)
# %%
df = pd.read_excel(old_path, index_col=0, header=2)
df
# %%
df_temp = df[df["Poste"] == "A"]
px.bar(df_temp, "Enchère moy")
# %%
def get_excel_from_mpg() -> pd.DataFrame:
    """
    Merge all dataframes from mpg excel sheet and dataframe with all the data
    """
    all_files = os.listdir(DATA_PATH)
    df = pd.DataFrame()
    for filename in all_files:
        if filename[-4:] == "xlsx":
            df_sheet = pd.read_excel(Path(DATA_PATH, filename), index_col=0, header=2)
            df = pd.concat([df, df_sheet], axis=0)
    return df


def save_clean_csv_file(df: pd.DataFrame):
    """
    - Fortmat datetime
    - Save data to csv file
    """
    list_dates = df["Date"].values
    list_dates_formatted = [format_date(x) for x in list_dates]
    df["Date"] = list_dates_formatted
    d = list_dates_formatted[0]
    file_name = f"{d.day}_{d.month}_{d.year}"
    df.to_csv(Path(DATA_PATH, "clean", file_name).with_suffix(".csv"))
    print(f"Data exported to csv, name: {file_name}")
    move_raw_file(file_name)


def move_raw_file(file_name: str):
    """
    Save raw file to a location with new name
    """
    extension = "xlsx"
    count = 1
    for x in os.listdir(DATA_PATH):
        if x[-4:] == extension:
            old_path = os.path.join(DATA_PATH, x)
            new_path = os.path.join(DATA_PATH, f"{file_name}_mpg_{count}.{extension}")
            os.system(f"move {old_path} {new_path}")
            count += 1
    if count>1:
        print("raw data moved")


def format_date(date: str) -> datetime:
    """
    Transform string to datetime
    """
    y = datetime.now().year
    i = date.find("/")
    day = int(date[i - 2 : i])
    month = int(date[i + 1 : i + 3])
    date_formatted = datetime(year=y, month=month, day=day)
    return date_formatted


df = get_excel_from_mpg()
save_clean_csv_file(df)
#%%
