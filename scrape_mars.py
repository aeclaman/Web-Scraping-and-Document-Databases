import os
import time
import requests
import pandas as pd
from datetime import datetime

from bs4 import BeautifulSoup as bs, Tag
from selenium import webdriver

from splinter import Browser
from splinter.exceptions import ElementDoesNotExist

def init_browser():
    print("**********Environmental Variables:")
    print(os.environ)
    # @NOTE: Replace the path with your actual path to the chromedriver
    if os.getenv('MONGODB_URI'):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.getenv('GOOGLE_CHROME_SHIM')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('headless')
        executable_path = {"executable_path": "/app/.chromedriver/bin/chromedriver"}
        return Browser("chrome", **executable_path, options=chrome_options)
    else:
        executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
        return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()
    print('browser is ready')
    #define dictionary to hold scraped data
    mars_dict = {}

    #Mars News scraping
    mars_news_url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    
    # Retrieve page with the requests module
    ##response = requests.get(mars_news_url, timeout=5)
    browser.visit(mars_news_url)
    time.sleep(3)
    html = browser.html

    # Create BeautifulSoup object; parse with 'html.parser'
    ##soup = bs(response.text, 'html.parser')
    soup = bs(html, 'html.parser')

    # find the list of news articles
    section = soup.find('div', class_='grid_layout').parent
    # get the unordered list tag of the articles list
    news_list = section.find_next('ul').find_all('li')
    for item in news_list:
        if isinstance(item, Tag): 
            # Grab first image
            image_src = item.find('div', class_='list_image')
            link = image_src.find('img')
            href = link['src']
            # Grab first title and teaser
            news_title = item.find('div', class_='content_title').text.strip()
            news_p = item.find('div', class_="article_teaser_body").text.strip()
            # append href with prefix
            featured_image_url = 'https://mars.nasa.gov'+ href
            break

    #Add scraped data to dictionary
    mars_dict["news_title"] = news_title
    mars_dict["news_p"] = news_p
    mars_dict["featured_image_url"] = featured_image_url
    print("Featured image, headline and teaser complete")

    ##Mars Weather scraping
    weather_url = 'https://twitter.com/marswxreport?lang=en'
    #response = requests.get(weather_url, timeout=5)
    browser.visit(weather_url)
    time.sleep(3)
    html = browser.html
    soup = bs(html, 'html.parser')

    mars_weather = soup.find('div', attrs={"data-testid":"tweet"}).text
    #mars_weather = soup.find('div', "data-testid_="tweet").text
    mars_dict["mars_weather"] = mars_weather
    print("Weather complete")

    ##Mars Facts Table scraping
    facts_url = "https://space-facts.com/mars/"
    tables = pd.read_html(facts_url)
    df = tables[0]
    df.columns = ['Description', 'Value']
    df.set_index('Description', inplace=True)
    df.head()
    html_table = df.to_html()
    html_table = html_table.replace('\n', '')
    
    mars_dict["mars_facts"] = html_table
    print("Facts complete")

    ##Mars Hemispheres scraping
    hemisphere_image_urls = []

    if os.getenv('MONGODB_URI'):
        # if running on heroku, use static images of mars hemisphere data so as not to time out the web server. Images don't change anyway. Scraping them each time is not necessary.
        static_hemisphere_dict = {'Cerberus Hemisphere Enhanced':'https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/valles_marineris_enhanced.tif/full.jpg',
                                  'Schiaparelli Hemisphere Enhanced':'https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/schiaparelli_enhanced.tif/full.jpg',
                                  'Syrtis Major Hemisphere Enhanced': 'https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/syrtis_major_enhanced.tif/full.jpg',
                                  'Valles Marineris Hemisphere Enhanced': 'https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/valles_marineris_enhanced.tif/full.jpg'}
        for k, v in static_hemisphere_dict.items():
            hemisphere_dict = {}
            hemisphere_dict["img_url"] = v
            hemisphere_dict["title"] = k
            hemisphere_image_urls.append(hemisphere_dict)
    else:
        hemisphere_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
        browser.visit(hemisphere_url)
        time.sleep(3)
        html = browser.html
        soup = bs(html, 'html.parser')

        items = soup.find_all('div', class_='item')
    
        for item in items:
            item_url = item.find('h3').text
            title = item_url
    
            try:
                browser.find_link_by_partial_text(item_url)[0].click()
            except ElementDoesNotExist:
                print("Scraping Complete")
        
            html = browser.html
            soup = bs(html, 'html.parser')
            wide_image = soup.find('img', class_='wide-image')['src']
            #title = soup.find('h2', class_='title').text
    
            hemisphere_dict = {}
            hemisphere_dict["img_url"] = "https://astrogeology.usgs.gov" + wide_image
            hemisphere_dict["title"] = title
            hemisphere_image_urls.append(hemisphere_dict)
            time.sleep(3)
    
            browser.back()

    mars_dict["hemisphere_list"] = hemisphere_image_urls
    print("hemispheres complete")

    # Close the browser after scraping
    browser.quit()
    print("Quitting browser")
    
    # add a timestamp to collected data
    mars_dict["data_timestamp"] = datetime.now()

    return mars_dict


