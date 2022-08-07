from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time
import os.path
import json
import csv

# header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}

opsi = webdriver.ChromeOptions()
opsi.add_argument('--headless')

### Must Be changed according to the user's user-agent ###
opsi.add_argument("user-agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36")

### chomediver must match user's chrome version ###
servis = Service('chromedriver.exe')

driver = webdriver.Chrome(service=servis, options=opsi)

df = pd.DataFrame()

def csv_to_json(csvFilePath, jsonFilePath):
    jsonArray = []
      
    #read csv file
    with open(csvFilePath, encoding='utf-8') as csvf: 
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf) 

        #convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            jsonArray.append(row)
  
    #convert python jsonArray to JSON String and write to file
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf: 
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)

def write_json(new_data, filename='product.json'):
    with open(filename,'r+') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data.append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file)

def product_scrape(url):

    driver.set_window_size(1300, 800)
    driver.get(url)
    time.sleep(5)
    
    content = driver.page_source

    data = BeautifulSoup(content, 'html.parser')

    category = data.find('ol', class_="css-1a6fy1g")

    i = 0
    main_category = ""
    sub_category = ""
    final_category = ""
    name = ""

    for j in category.find_all('li', class_='css-3a7rwp'):
        if i == 1:
            main_category = j.get_text()
        elif i == 2:
            sub_category = j.get_text()
        elif i == 3:
            final_category = j.get_text()
        elif i == 4:
            name = j.get_text()     
        i+=1
    
    png_name = "screenshots/" + name + ".png"
    driver.save_screenshot(png_name)
    driver.quit()

    etc = data.find('div', class_="css-1fogemr")

    sold_temp = etc.find('div', {"data-testid":"lblPDPDetailProductSoldCounter"})
    sold = ""

    if sold_temp != None:
        for k in sold_temp:
            sold = sold + k.get_text()
    else:
        sold = "Terjual 0"

    rating = etc.find('span', {"data-testid":"lblPDPDetailProductRatingNumber"})

    if rating == None:
        rating = "No Ratings"
    else:
        rating = rating.get_text()

    rating_counter = etc.find('span', {"data-testid":"lblPDPDetailProductRatingCounter"})

    if rating_counter == None:
        rating_counter = "0 rating"
    else:
        rating_counter = rating_counter.get_text()
        rating_counter = rating_counter[1:len(rating_counter)-1]
    
    price = etc.find('div', {"data-testid":"lblPDPDetailProductPrice"}).get_text()

    temp_seller = data.find('div', class_="css-d1nhq9")

    seller = temp_seller.find('h2').get_text()

    df = pd.DataFrame({
        'Product Name':name, 
        'Seller':seller, 
        'Main Category':main_category,
        'Sub Category': sub_category,
        'Category':final_category,
        'Price':price, 
        'Sold':sold, 
        'Rating':rating, 
        'Total Rating':rating_counter,
        'Link': url}, index=[0])

    check_csv = os.path.exists('product.csv')
    check_json = os.path.exists('product.json')

    if check_csv == False and check_json == False:
        df.to_csv('product.csv', index=False)
        df.to_json('product.json', orient="records")
    else:
        df.to_csv('product.csv', mode='a', index=False, header=False)
        csv_to_json('product.csv', 'product.json')
    
    # json_name = name + ".json"
    # df.to_json(json_name, orient="records")
 


search = input("Enter the url of the product: ")
product_scrape(search)
