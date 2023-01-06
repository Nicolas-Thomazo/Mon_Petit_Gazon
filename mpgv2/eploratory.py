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
DATA_PATH = Path(MPG_PATH, "DATA","clean","6_11_2022.csv")
# %%
df=pd.read_csv(DATA_PATH)
# %%
df["diff_price"] = df["Enchère moy"]-df["Cote"]
# %%
# Normalisé Notes/Buts/Cote
c=["Joueur","Cote","Enchère moy","diff_price","Note","Poste","But","%Titu","Pass decis.","Club","Interceptions","%Passes","Tacles","Fautes"]
df_utils = df.loc[:,c].copy()
df_utils = df_utils[df_utils["Enchère moy"].isnull()==False]
# %%
df_utils.fillna(0,inplace=True)
df_utils.drop_duplicates(inplace=True)
# %%
m1,m2=min(df_utils["But"]),max(df_utils["But"])
df_utils["But_norm"] = (df_utils["But"]-m1)/(m2-m1)

m1,m2=min(df_utils["Note"]),max(df_utils["Note"])
df_utils["Note_norm"] = (df_utils["Note"]-m1)/(m2-m1)

m1,m2=min(df_utils["Cote"]),max(df_utils["Cote"])
df_utils["Cote_norm"] = (df_utils["Cote"]-m1)/(m2-m1)
df_utils["Cote_norm"] = 1-df_utils["Cote_norm"]

m1,m2=min(df_utils["diff_price"]),max(df_utils["diff_price"])
df_utils["diff_price_norm"] = (df_utils["diff_price"]-m1)/(m2-m1)

m1,m2=min(df_utils["%Titu"]),max(df_utils["%Titu"])
df_utils["%Titu_norm"] = (df_utils["%Titu"]-m1)/(m2-m1)

# %%
df_utils["aggregate"] =  (df_utils["Note_norm"] + df_utils["But_norm"] + df_utils["Cote_norm"] + df_utils["%Titu"])/4
# %%
df_utils_sort = df_utils.sort_values(by="aggregate",ascending=False)
df_utils_sort.loc[:,["Joueur","Cote","But","Note","%Titu","aggregate"]].iloc[:30,:]
# %%
