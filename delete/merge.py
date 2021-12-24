import os
import pandas as pd
import re
import unicodedata

CLUB ="CLUB"
JOUEUR = "JOUEUR"
ENCHERE_MOY = "ENCHERE_MOY"
COTE = "COTE"
POSTE = "POSTE"
BUTS = "BUTS"
NOTE = "NOTE"
NB_MATCH = "NB_MATCH"
TEMPS = "TEMPS"
EXPECTED_GOALS = "EXPECTED_GOALS"
EXPECTED_ASSISTS = "EXPECTED_ASSISTS"
ASSISTS = "ASSISTS"
SAISON = "SAISON"


def clean_col_externes(df:pd.DataFrame)->pd.DataFrame:
    """
    In externe data replace string column expected goals and assists by float type

    :param df: dataframe to replace column
    :type df: pd.DataFrame
    :return: dataframe cleaned
    :rtype: pd.DataFrame
    """
    df[EXPECTED_GOALS] = df[EXPECTED_GOALS].apply(lambda x: float(x[:4]))
    df[EXPECTED_ASSISTS] = df[EXPECTED_ASSISTS].apply(lambda x: float(x[:4]))
    return df
def clean_data_externe(df_externe:pd.DataFrame)->pd.DataFrame:
    df_externe = df_externe.rename(columns={"Player": JOUEUR, 'A': ASSISTS,"xG":EXPECTED_GOALS,"xA":EXPECTED_ASSISTS,"saison":SAISON,"G":BUTS})
    df_externe = df_externe[[JOUEUR,ASSISTS,EXPECTED_GOALS,EXPECTED_ASSISTS,SAISON,BUTS]]
    df_externe = clean_col_externes(df_externe)
    df_externe = df_externe[(df_externe[SAISON]==year-1) | (df_externe[SAISON]==year)]
    return df_externe

# --------------MPG by season--------------

def change_type_columns(df:pd.DataFrame)->pd.DataFrame:
    df["Note"]=df["Note"].apply(lambda x: x.replace(',','.') )
    df["Note 1 an"]=df["Note 1 an"].apply(lambda x: x.replace(',','.') )
    df["Note"] = pd.to_numeric(df["Note"])
    df["Note 1 an"] = pd.to_numeric(df["Note 1 an"])
    return df
def compute_notes_previous_season(df):
    """
    In Mpg data is regrouped not by season but for the current season and the previous season. We separate the data between the current season and the previous
    """
    df[f"NOTE"] = 1000
    note_count=0
    for i in range(df.shape[0]):
        note_all = df.loc[i,"Note 1 an"]
        all_nb_games = df.loc[i,"Nb match 1 an"]
        current_nb_games = df.loc[i,"Nb match"]
        current_notes = df.loc[i,"Note"]
        previous_nb_games = df.loc[i,f"NB_MATCH"]

        if (current_nb_games > 0) and (previous_nb_games>0):
            df.loc[i,f"NOTE"] = (note_all * all_nb_games - current_nb_games * current_notes) / previous_nb_games
        elif (current_nb_games ==0):
            note_count=note_count+1
            df.loc[i,[f"NOTE"]] = note_all
        else:
            df.loc[i,[f"NOTE"]] = 0
    return df
def compute_previous_season_statistics(df:pd.DataFrame)->pd.DataFrame:
    df_previous = df.copy()
    df_previous[f"NB_MATCH"]=df_previous.loc[:,"Nb match 1 an"] - df["Nb match"]
    df_previous[f"BUTS"]=df_previous.loc[:,"Buts 1 an"] - df["But"]
    df_previous = compute_notes_previous_season(df_previous)
    df_previous[f"TEMPS"] = df_previous["Tps 1 an"] - df["Temps"]
    return df_previous
def clean_regroup_mpg_data(df_mpg:pd.DataFrame)->pd.DataFrame:
    df_mpg_clean = change_type_columns(df_mpg)
    df_mpg_previous = compute_previous_season_statistics(df_mpg_clean)
    df_mpg_previous = df_mpg_previous.rename(columns={"Joueur":JOUEUR,"Poste":POSTE,"Côte":COTE,"Enchère moy":ENCHERE_MOY,"Club":CLUB})
    df_mpg_previous = df_mpg_previous[columns]
    df_mpg_previous.loc[:,SAISON] = year-1

    df_mpg_current = df_mpg_clean.rename(columns={"Joueur":JOUEUR,"Poste":POSTE,"Côte":COTE,"Enchère moy":ENCHERE_MOY,"Club":CLUB,"But": BUTS, 'Note': NOTE,"Nb match":NB_MATCH,"Temps":TEMPS})
    df_mpg_current = df_mpg_current[columns]
    df_mpg_current.loc[:,SAISON] = year

    df_mpg = pd.concat([df_mpg_previous,df_mpg_current])
    return df_mpg
# --------------Merge--------------

def strip_accents(text:str)->str:
    """
    Remove accents in a string
    """
    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3 
        pass

    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")
    return str(text)
def clean_names(name:str)->str:
    """
    Normalize string, remove accent, and put to lower string
    """
    name = strip_accents(name)
    name = name.replace('-',' ')
    name = name.lower()
    return name
def normalize_names(players_names:pd.Series)->pd.Series:
    """
    Apply cleaning names to the dataframe column

    :param players_names: series with the
    :type players_names: pd.Series
    :return: normalized strings
    :rtype: pd.Series
    """
    players_names = players_names.apply(lambda x : clean_names(x))
    return players_names

def compare_strings(str1:str,str2:str)->float:
    """
    compare 2 strings and give the proportion of the letters of the first string present in the second string. Useful for mapping the differents players names
    """
    c = 0
    for i in str1:
        if re.search(i,str2):
            c=c+1
    prop = c/len(str1)
    return prop
def compute_similarity(player_name:str,df:pd.DataFrame,nb_goals:int):
    """
    For a given player, check in the mpg statistics the player that have the more correspondance with the player_name. 
    Return the score and name in the mpg statistics data of the players
    """
    score = 0
    player_higher_sim = ""
    for name in df[JOUEUR]:
        similarity = compare_strings(name,player_name)
        nb_goals_check = df.loc[df[JOUEUR] == name,BUTS].values[0]
        if (similarity > score and nb_goals_check == nb_goals):
            score = similarity
            player_higher_sim = name
    return player_higher_sim,score
def merge_data(df1:pd.DataFrame,df2:pd.DataFrame)->pd.DataFrame:
    """Merge the mpg data and the externes data into one dataframe

    :param df1: externe data
    :type df1: pd.DataFrame
    :param df2: mpg data
    :type df2: pd.DataFrame
    :return: merge dataframe
    :rtype: pd.DataFrame
    """
    for saison in df1[SAISON].unique():
        df1_saison = df1[df1[SAISON]==saison]
        for player in df1_saison[JOUEUR]:
            nb_goals = df1_saison.loc[df1_saison[JOUEUR] == player,BUTS].values[0]
            similarity_name,score = compute_similarity(player,df2[df2[SAISON]==saison],nb_goals)
            if score >0.95:
                data=df1_saison.loc[df1_saison[JOUEUR] == player,[ASSISTS,EXPECTED_GOALS,EXPECTED_ASSISTS]]      
                cond_saison = df2[SAISON]==saison
                df2.loc[(df2[JOUEUR] == similarity_name) & (cond_saison),ASSISTS]=data[ASSISTS].values[0]
                df2.loc[(df2[JOUEUR] == similarity_name) & (cond_saison),EXPECTED_GOALS]=data[EXPECTED_GOALS].values[0]
                df2.loc[(df2[JOUEUR] == similarity_name) & (cond_saison),EXPECTED_ASSISTS]=data[EXPECTED_ASSISTS].values[0]
    return df2



if __name__ == "__main__":
    year = 2021
    PATH_EXTERNES_DATA = os.path.join("..","ligue1_data","data_ligue1_players_2014_2021.csv")
    PATH_MPG_DATA = os.path.join("..","ligue1_data","mpg_stats.csv")

    df_externe=pd.read_csv(PATH_EXTERNES_DATA,index_col=0)
    df_mpg=pd.read_csv(PATH_MPG_DATA,sep=';',header=2)
    columns = [JOUEUR,POSTE,COTE,ENCHERE_MOY,CLUB,NOTE,NB_MATCH,BUTS,TEMPS]

    #Externe data
    df_externe=clean_data_externe(df_externe)

    #MPG
    df_mpg=clean_regroup_mpg_data(df_mpg)

    #Merge
    df_externe.loc[:,JOUEUR] = normalize_names(df_externe.loc[:,JOUEUR])
    df_mpg.loc[:,JOUEUR] = normalize_names(df_mpg.loc[:,JOUEUR])

    df_mpg.loc[:,ASSISTS] = 0
    df_mpg.loc[:,EXPECTED_GOALS] = 0
    df_mpg.loc[:,EXPECTED_ASSISTS] = 0
    df_merge = merge_data(df_externe,df_mpg)

    df_merge.to_csv("../ligue1_data/data_final.csv")


    
    