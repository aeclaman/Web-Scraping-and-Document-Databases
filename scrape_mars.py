import os
import time
import requests
import pandas as pd

from bs4 import BeautifulSoup as bs
from selenium import webdriver

from splinter import Browser
from splinter.exceptions import ElementDoesNotExist


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()
    mars_dict = {}

    #Mars News scraping
    mars_news_url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    
    # Retrieve page with the requests module
    response = requests.get(mars_news_url, timeout=5)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(response.text, 'html.parser')

    # Grab first title and teaser
    news_title = soup.find('div', class_='content_title').text.strip()
    news_p = soup.find('div', class_='rollover_description_inner').text.strip()

    mars_dict["news_title"] = news_title
    mars_dict["news_p"] = news_p


    #Featured Image scraping
    featured_image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(featured_image_url)

    html = browser.html
    soup = bs(html, "html.parser")

    #Click full image button to get image file
    browser.click_link_by_partial_text('FULL IMAGE')
    html = browser.html
    soup = bs(html, 'html.parser')
    time.sleep(5)

    #Click more info button to get full image file
    browser.click_link_by_partial_text('more info')
    html = browser.html
    soup = bs(html, 'html.parser')

    img = soup.find('figure', class_='lede')

    link = img.find('a')
    href = link['href']

    featured_image_url = 'https://www.jpl.nasa.gov'+ href

    #Add scraped data to dictionary
    mars_dict["featured_image_url"] = featured_image_url


    ##Mars Weather scraping
    weather_url = 'https://twitter.com/marswxreport?lang=en'
    response = requests.get(weather_url, timeout=5)
    soup = bs(response.text, 'html.parser')

    mars_weather = soup.find('p', class_="tweet-text").text
    mars_dict["mars_weather"] = mars_weather


    ##Mars Hemispheres scraping
    #browser = init_browser()
    hemisphere_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemisphere_url)

    html = browser.html
    soup = bs(html, 'html.parser')

    items = soup.find_all('div', class_='item')
    hemisphere_image_urls = []

    for item in items:
        item_url = item.find('h3').text
    
        try:
            browser.find_link_by_partial_text(item_url)[0].click()
            time.sleep(10)
        except ElementDoesNotExist:
            print("Scraping Complete")
        
        html = browser.html
        soup = bs(html, 'html.parser')
        wide_image = soup.find('img', class_='wide-image')['src']
        title = soup.find('h2', class_='title').text
    
        hemisphere_dict = {}
        hemisphere_dict["img_url"] = "https://astrogeology.usgs.gov" + wide_image
        hemisphere_dict["title"] = title
        hemisphere_image_urls.append(hemisphere_dict)
    
        browser.back()

    mars_dict["hemisphere_list"] = hemisphere_image_urls


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


    # Close the browser after scraping
    browser.quit()

    return mars_dict


