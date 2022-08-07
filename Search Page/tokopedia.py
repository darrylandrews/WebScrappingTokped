from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time

opsi = webdriver.ChromeOptions()
opsi.add_argument('--headless')
opsi.add_argument("user-agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36")
servis = Service('chromedriver.exe')
driver = webdriver.Chrome(service=servis, options=opsi)

df = pd.DataFrame()

def web_scraping(search):
    src = search.split()
    n = len(src)
    new_search = ""
    new_title = ""

    if n > 1:
        for i in range(n):
            if i < n-1:
                new_search = new_search + src[i] + "%20"
                new_title = new_title + src[i] + "_"
            else:
                new_search = new_search + src[i]
                new_title = new_title + src[i]
    else:
        new_search = search
        new_title = search

    tokped = "https://www.tokopedia.com/search?st=product&q="+ new_search +"&srp_component_id=02.01.00.00&srp_page_id=&srp_page_title=&navsource="

    driver.set_window_size(1300, 800)
    driver.get(tokped)

    ranges = 500
    for i in range(1, 7):       # scroll the page to load more data 
        end = ranges * i
        order = "window.scrollTo(0, "+str(end)+")"
        driver.execute_script(order)
        time.sleep(1)

    time.sleep(5)

    png_title = "screenshots/" + new_title + ".png"
    driver.save_screenshot(png_title)
    content = driver.page_source
    driver.quit()

    data = BeautifulSoup(content, 'html.parser')

    name_list, price_list, sold_list, location_list, seller_list, rating_list, link_list = [], [], [], [], [], [], []

    for area in data.find_all('div', class_="css-12sieg3"):
        name = area.find('div', class_="css-1b6t4dn").get_text()
        price = area.find('div', class_="css-1ksb19c").get_text()
        sold = area.find('span', class_="css-1duhs3e")

        if sold != None:
            sold = sold.get_text()
        else:
            sold = "Terjual 0"

        temp = area.find_all('span', class_="css-1kdc32b flip") #location
        location = ""
        seller = ""
        i = 0
        for j in temp:
            if i == 0:
                location += j.get_text()
            elif i == 1:
                seller += j.get_text()
            i += 1

        rating = area.find('span', class_="css-t70v7i")
        if rating != None:
            rating = rating.get_text()
        else:
            rating = "No Ratings"

        link = area.find('a')['href']

        name_list.append(name)
        seller_list.append(seller)
        location_list.append(location)
        price_list.append(price)
        sold_list.append(sold)
        rating_list.append(rating)
        link_list.append(link)

    df = pd.DataFrame({'Product Name':name_list, 'Seller':seller_list, 'Location':location_list, 'Price':price_list, 'Sold': sold_list, 'Rating': rating_list, 'Link': link_list})   

    title_csv = "csv/" + new_title + ".csv"
    title_json = "json/" + new_title + ".json"

    df.to_csv(title_csv, index=False)
    df.to_json(title_json, orient="records")
    

search = input("Enter name or catagory: ")
web_scraping(search)
