#Import library
import requests
import pandas as pd
import os
import pymongo
import time
from splinter import Browser
from flask_pymongo import PyMongo
from bs4 import BeautifulSoup 
from flask import Flask,render_template, redirect

def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    mars_dict ={}

    #Scraping Mars News

    news_url = 'https://redplanetscience.com/'
    browser.visit(news_url)
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    #Collect the latest News Title and Paragraph Text
    news_title = news_soup.find_all('div', class_='content_title')[0].text
    news_paragraph = news_soup.find_all('div',class_='article_teaser_body')[0].text


    #Scape Mars Image

    jpl_mars_url = 'https://spaceimages-mars.com/'
    browser.visit(jpl_mars_url)
    html = browser.html
    image_soup =  BeautifulSoup(html, 'html.parser')
    #Retrive featured image link
    featured_image_path = image_soup.find_all('img')[1]['src']
    featured_image_url = jpl_mars_url+featured_image_path
    #print(featured_image_url )

    #Scrape Mars Fact complete table
    
    mars_fact_url = 'https://galaxyfacts-mars.com'
    mars_fact_table =pd.read_html(mars_fact_url)
    mars_fact_table[0]
    mars_fact_df = mars_fact_table[0]
    #Format the header
    new_header = mars_fact_df.iloc[0] 
    mars_fact_df = mars_fact_df[1:]
    mars_fact_df.columns = new_header 
    #Remove Earth Data
    mars_fact_df =mars_fact_df[['Mars - Earth Comparison', 'Mars']]
    #Rename columns
    mars_fact_df.rename(columns = {'Mars - Earth Comparison':'Mars Fact', 'Mars':'Value'}, inplace = True)
    mars_fact_df
    #Remove ":"
    facts = pd.Series(mars_fact_df['Mars Fact'])
    mars_fact_df['Mars Fact'] = facts.str.strip(':')
    mars_fact_df
    #Convert the data to a HTML table string
    fact_html_table = mars_fact_df.to_html()
    fact_html_table.replace('\n','')

    # Scrape Mars hemisphere name and images
    hermisphere_url ='https://marshemispheres.com/'
    browser.visit(hermisphere_url)
    html = browser.html
    hemispheres_soup =  BeautifulSoup(html, 'html.parser')
    #Retrieve mars hemisphere data
    hemispheres_data = hemispheres_soup.find('div', class_ ='collapsible results')
    mars_hemispheres = hemispheres_data.find_all('div',class_='item')
    #Iterate through each data point to get the title and url
    hemisphere_image_urls = []
    for i in mars_hemispheres:
        #Retrieve title
        hemisphere =i.find('div', class_="description")
        title= hemisphere.h3.text
        #print(title) --testing
        #Retrieve image link by browsing to hemisphere page
        hemisphere_link = hemisphere.a["href"]
        browser.visit(hermisphere_url +hemisphere_link)
        image_html = browser.html
        image_soup = BeautifulSoup(image_html, 'html.parser')
    
        image_link = image_soup.find('div', class_='downloads')
        image_url = image_link.find('li').a['href']
        #print (image_url) --testing
        #Create dictonary to store title and image_url
        mars_hemisphere_dict = {}
        mars_hemisphere_dict['title'] = title
        mars_hemisphere_dict['img_url'] = hermisphere_url+image_url
        hemisphere_image_urls.append(mars_hemisphere_dict)

    # Mars 
    mars_dict = {
        "news_title": news_title,
        "news_p": news_paragraph,
        "featured_image_url": featured_image_url,
        "fact_table": str(fact_html_table ),
        "hemisphere_images": hemisphere_image_urls
        }
    return mars_dict
    