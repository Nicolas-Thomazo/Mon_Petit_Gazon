from merge import merge_mpg_externe
from scrapping import scrapping_mpg,scrapping_externes_data
import os
from selenium import webdriver

if __name__ == "__main__":

    PATH_NEW_DIR = os.path.join("C:",os.sep,"Users","nicol","Documents","ProjetsPerso","mpg","ligue1_data")
    start = 2020
    end = 2021
    driver = webdriver.Chrome('chromedriver/chromedriver')

    #mpg
    scrapping_mpg(PATH_NEW_DIR,driver)

    #externe data
    scrapping_externes_data(PATH_NEW_DIR,start,end,driver)

    #merge and save data
    file_name="data_final2.csv"
    merge_mpg_externe(PATH_NEW_DIR,start,end,file_name)