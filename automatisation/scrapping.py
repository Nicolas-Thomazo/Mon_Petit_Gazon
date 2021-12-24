from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import numpy as np
from selenium.webdriver.support.ui import WebDriverWait
import time
import os
import glob

def _get_info_player(player):
    player_infos = np.array([])
    for column in player.find_elements_by_tag_name("td"):
        player_infos=np.append(player_infos,column.text)
    return player_infos

def _create_data_page(driver):
    data =driver.find_element_by_id("league-players").find_element_by_tag_name("table")
    header = data.find_element_by_tag_name("thead")
    columns = []
    for col_name in header.find_element_by_tag_name("tr").find_elements_by_tag_name("th"):
        #print(col_name.get_attribute("title"))
        columns.append(col_name.text)
    
    data_array = np.array([])
    for player in data.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr"):
        player_info = _get_info_player(player)
        if data_array.size>0:
            data_array = np.vstack([data_array, player_info])
        else:
            data_array = np.array(player_info)
    
    df = pd.DataFrame(columns=columns,data=data_array)
    return df

    
def _find(driver):
    """
    find if the selector if found in the web page and return true or false consequently
    """
    element = driver.find_element_by_xpath('//*[@class="page current"]//following-sibling::li')
    if element:
        return element
    else:
        return False

def _create_data_by_season(url,driver):
    """
    For one season generate a dataframe with all infos on players
    """
    driver.get(url)
    df_all = pd.DataFrame()
    #count
    last_selector = driver.find_element_by_xpath('//*[@class="pagination"]/li[last()]')
    count = int(last_selector.text)
    for i in range(1,count):
        WebDriverWait(driver, 5).until(_find)
        df=_create_data_page(driver)
        df_all=df_all.append(df)
        driver.find_element_by_xpath('//*[@class="page current"]//following-sibling::li').click()
    return df_all

def _find_mpg(driver):
    """
    find if the selector if found in the web page and return true or false consequently
    """
    element = driver.find_element_by_xpath('//*[ text() = "Excel"]')
    if element:
        return element
    else:
        return False

def scrapping_mpg(PATH_NEW_DIR,driver):
    url = "https://www.mpgstats.fr/top/Ligue-1/custom"
    driver.get(url)
    WebDriverWait(driver, 5).until(_find_mpg)
    driver.find_element_by_xpath('//*[ text() = "Excel"]').click()
    time.sleep(3)

    #find last downloaded file
    path=os.path.join("C:",os.sep,"Users","nicol","Downloads")
    file_type = '\*xlsx'
    files = glob.glob(path + file_type)
    last_file = max(files, key=os.path.getctime)
    print("last_file",last_file)
    #rename file
    new_file = "mpg_stats.xlsx"
    print("new file",new_file)
    os.system(f"ren {last_file} {new_file}")
    #move file
    PATH_FILE = os.path.join(path,new_file)
    os.system(f"move {PATH_FILE} {PATH_NEW_DIR}")
    print("mpg data downloaded and moved")

def scrapping_externes_data(PATH_NEW_DIR,start,end,driver):
    df=pd.DataFrame()
    for i in range(start,end+1):
         url = f"https://understat.com/league/Ligue_1/{i}"
         df_saison=_create_data_by_season(url,driver)
         df_saison["saison"] = i
         df=df.append(df_saison)
    path_data = os.path.join(PATH_NEW_DIR,f"data_ligue1_players_{start}_{end}.csv")
    df.to_csv(path_data)
    print("Externe data downloaded")    

    



