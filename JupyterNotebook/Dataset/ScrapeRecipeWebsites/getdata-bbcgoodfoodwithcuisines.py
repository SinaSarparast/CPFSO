# coding=utf-8
'''
Created on 24 April 2018
@author: Mariam
'''

import csv
import operator
import re
import string
import bs4
import io, json
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
import unidecode
from string import ascii_lowercase
from net import geturlcontents


'''


15 relevant cuisines

Go and get recipe data that sits on pages two levels beneath this page: https://www.bbc.com/food/cuisines
Things to watch out for:
Extra headings in pages
Only 1 - 15 recipes per page but this may actually be handy to stop us getting blocked by server
Rate limits

First page is reached like this: "https://www.bbc.com/food/recipes/search?cuisines[]="+cuisine_name

Pages after that are reached like this:
https://www.bbc.com/food/recipes/search?page=2&cuisines%5B0%5D=caribbean&sortBy=lastModified

Need to use try/except when scraping all data as we do not know how many pages of recipes each cuisine has got 

 - next link to try - https://www.bbcgoodfood.com/recipes/category/cuisines

'''

#all recipe cuisines
allcuisinesbbcfood=["african","american","british","caribbean","chinese","east european","french","greek","indian","irish","italian","japanese","mexican","nordic","north african","portuguese","south american","spanish","thai_and_south-east_asian","turkish_and_middle_eastern"]

#recipe cuisines within this list we have from the kaggle set
#Keeping Caribbean, see if same as Jamaican
#keeping North African, see if same as Morroccan
#South American is Southern US
#Thai and South-East Asian should be matched to Thai

selectedcuisinesbbcfood=["caribbean","chinese","french","greek","indian","irish","italian","japanese","mexican","north african","portuguese","south american","spanish","thai_and_south-east_asian"]

recipe_page_urls = []

for cuisine_name in selectedcuisinesbbcfood:
    build_recipes_url="https://www.bbc.com/food/recipes/search?cuisines[]="+cuisine_name
    print(build_recipes_url)
    recipe_page_urls.append(build_recipes_url)

print(recipe_page_urls)
#going to get 15 recipes from each cuisine first

#url = recipe_page_urls[0]

mycuisine_index=0;
listforjsonoutput=[];
for linkto_recipe in recipe_page_urls:

    url = linkto_recipe

    print("I am going to this url now %s" % url)
    (webpage,alink)=geturlcontents(url)
    print("I have collected the food links page from  %s" % alink)
    print(webpage)
    
    print("i am using BeautifulSoup to parse the recipe index page")
    soup = BeautifulSoup(webpage, "html.parser")
    
    linkstocrawl=[];
    
    print("I made some soup with the food links page")
    for h3inrecipespage in soup.findAll("h3", class_=""):
        print("i found a h3 %s" % h3inrecipespage)
        for a in h3inrecipespage.findAll("a", href=True):
            print("got a link woohoo!!")
            print(a['href'])
            finalrecipecombinedlink = "https://www.bbc.com" + a['href']
            print(finalrecipecombinedlink)
            linkstocrawl.append(finalrecipecombinedlink)
                    
    print("here are all my links to crawl")
    print(linkstocrawl)
    
    print("going to get the recipes now")
    
    for recipe_page in linkstocrawl:
        print("I am going to this recipe page now %s" % recipe_page)
        (webpage,alink)=geturlcontents(recipe_page)
        print("I have collected the food links page from  %s" % alink)
        print("i am using BeautifulSoup to parse the recipe page")
        soup = BeautifulSoup(webpage, "html.parser")
        for h1found in soup.findAll("h1"):
            print("got a recipe name woohoo!!")
            print(h1found.text)
        ingredients_for_recipe=[];
        for li in soup.findAll("li", class_="recipe-ingredients__list-item"):
            print("got an ingredient woohoo!!")
            print(li)
            print(li.text)
            ingredients_for_recipe.append(li.text)
        makejsonready = {u"id": h1found.text, u"cuisine": selectedcuisinesbbcfood[mycuisine_index], u"ingredients": ingredients_for_recipe}
        print(makejsonready)
        
        listforjsonoutput.append(makejsonready)


print("now I am going to the next page of recipes for each cuisine, and getting their recipes, this will take a while!!!")

#scrape 10 more pages max
pagestocrawl = [2,3,4,5,6,7,8,9,10,11]


for recipe_in_list in selectedcuisinesbbcfood:
    for anumber in pagestocrawl:
        try:
            build_additional_recipes_url = "https://www.bbc.com/food/recipes/search?page="+str(anumber)+"&cuisines%5B0%5D="+recipe_in_list+"&sortBy=lastModified"
            print(build_additional_recipes_url)
            
            print("I am going to this url now %s" % build_additional_recipes_url)
            (webpage,alink)=geturlcontents(build_additional_recipes_url)
            print("I have collected the food links page from  %s" % alink)
            #print(webpage)
            
            print("i am using BeautifulSoup to parse the recipe index page")
            soup = BeautifulSoup(webpage, "html.parser")
            
            print("I made some soup with the food links page")
            
            linkstocrawl=[];
            for h3inrecipespage in soup.findAll("h3", class_=""):
                print("i found a h3 %s" % h3inrecipespage)
                for a in h3inrecipespage.findAll("a", href=True):
                    print("got a link woohoo!!")
                    print(a['href'])
                    finalrecipecombinedlink = "https://www.bbc.com" + a['href']
                    print(finalrecipecombinedlink)
                    linkstocrawl.append(finalrecipecombinedlink)
            
            print("here are all my links to crawl")
            print(linkstocrawl)
            
            print("going to get the recipes now")
            
            for recipe_page in linkstocrawl:
                print("I am going to this recipe page now %s" % recipe_page)
                (webpage,alink)=geturlcontents(recipe_page)
                print("I have collected the food links page from  %s" % alink)
                print("i am using BeautifulSoup to parse the recipe page")
                soup = BeautifulSoup(webpage, "html.parser")
                for h1found in soup.findAll("h1"):
                    print("got a recipe name woohoo!!")
                    print(h1found.text)
                ingredients_for_recipe=[];
                for li in soup.findAll("li", class_="recipe-ingredients__list-item"):
                    print("got an ingredient woohoo!!")
                    print(li)
                    print(li.text)
                    ingredients_for_recipe.append(li.text)
                makejsonready = {u"id": h1found.text, u"cuisine": selectedcuisinesbbcfood[mycuisine_index], u"ingredients": ingredients_for_recipe}
                print(makejsonready)
        
                listforjsonoutput.append(makejsonready)

        except: 
            print("I cannot find another recipe index page, sorry!")

print("that's it I have done all the recipes woohoo!!!!!!!!!!!!!!!")
#mycuisine_index=mycuisine_index+1
             
print("here is the json")
print(listforjsonoutput)


print("woohoo!!!!! I am writing all the recipe data to the file")
  
with io.open('bbcfoodcuisines-10pages.json', 'w', encoding='utf-8') as f:
    json.dump(listforjsonoutput, f, ensure_ascii=False, indent=4)

print("Total recipes saved:")
print(len(listforjsonoutput))
   
