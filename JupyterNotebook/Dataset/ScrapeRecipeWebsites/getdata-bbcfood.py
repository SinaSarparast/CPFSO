# coding=utf-8
'''
Created on 06 February 2018
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
#from unidecode import unidecode
import unidecode
from string import ascii_lowercase
from net import geturlcontents




foodletterurls = []
allrecipedetails = {}

'''
for letter in ascii_lowercase:
    foodletterurl = "http://www.bbc.co.uk/food/dishes/by/letter/" + letter
    #print foodletterurl
    foodletterurls.append(foodletterurl)
'''
 
#for url in foodletterurls:
#print "here is the recipe dictionary so far",allrecipedetails
#print "it has got this many items", len(allrecipedetails)

# doing one letter of the alphabet at a time.
# To do the whole alphabet at once may not be possible / may need to code in a delay to stop server blocking us.

url = "http://www.bbc.co.uk/food/dishes/by/letter/b" 

print("I am going to this url now %s" % url)
(webpage,alink)=geturlcontents(url)
print("I have collected the food links page from  %s" % alink)


#print webpage

#print "I am diagnosing the webpage with beautiful soup"
#with webpage as fp:
#    data = fp.read()
#diagnose(webpage)


print("i am using BeautifulSoup")

soup = BeautifulSoup(webpage, "html.parser")

print("I made some soup with the food links page")
genericrecipepagelinks = [];
recipelinks = [];
recipesandlinks = [];
limitedlistfortesting = [];
allmycollectedlinks = [];

counter=0;

#limiting the output to 10 for testing / remove this while condition to do all recipes

for olinrecipespage in soup.findAll("ol", class_="resources foods grid-view"):

    print("i found a list of recipe index pages to crawl %s" % olinrecipespage)
    #print(olinrecipespage)

    for alinkfound in olinrecipespage.findAll("a", href=True):
        print(alinkfound)
        allmycollectedlinks.append(alinkfound)
    


print("here are my links (full a tags)")

print(allmycollectedlinks)

# limitedlistfortesting = allmycollectedlinks[:10]
 
    #use allmycollectedlinks instead of limitedlistfortesting to do the whole lot
#print("here are my links for testing")
#print(limitedlistfortesting)

#for a in limitedlistfortesting:

for a in allmycollectedlinks:
    #if((len(allrecipedetails))<10):
    combinedlink = "http://www.bbc.co.uk" + a['href']
    print(combinedlink)
    recipeandlink = str(a.text),combinedlink
    genericrecipepagelinks.append(combinedlink)
    print("here are the links to recipe index pages to crawl")

print(genericrecipepagelinks)
#to crawl all recipes use the whole of the genericrecipepagelinks list
    #for pagerecipegeneric in genericrecipepagelinks:
    
print("just four")
print(genericrecipepagelinks[:4])

finalrecipecombinedlinks = []
for pagerecipegeneric in genericrecipepagelinks[:4]:
    print("I am going to this link: %s" % pagerecipegeneric)
    (webpage,alink)=geturlcontents(pagerecipegeneric)
    print("I have collected the food links page from  %s" % alink)
    

    recipeindexpagesoup = BeautifulSoup(webpage, "html.parser")
    print("I made some soup of the page which has a link to the actual recipe pages")

    for lirecipeindex in recipeindexpagesoup.findAll("li", class_="with-image"):
        print("i found a list in the recipe index page", lirecipeindex)
        for a in lirecipeindex.findAll("a", href=True):
            print("here finally is a link to crawl for the actual recipe page")
            finalrecipecombinedlink = "http://www.bbc.co.uk" + a['href']
            print(finalrecipecombinedlink)
            finalrecipecombinedlinks.append(finalrecipecombinedlink)
            


print("list of links")

print(finalrecipecombinedlinks)

print("getting final recipe")
        
listforjsonoutput=[];

for gogetrecipe in finalrecipecombinedlinks:
    #if counter<10:
    print("I am going to this url now %s" % gogetrecipe)
    (webpage,alink)=geturlcontents(gogetrecipe)
    print("I have collected the recipe page from  %s" % alink)
    finalrecipepagesoup = BeautifulSoup(webpage, "html.parser")
    print("I made some soup of the recipe page, here is the recipe title:")
    for item in finalrecipepagesoup.findAll("title"):
        recipetitle = item.get_text()
        recipetitle = recipetitle.replace("BBC Food - Recipes - ", "")
        recipetitle = recipetitle.strip("\\")
        print(recipetitle)
    ingredientslist = []
    for item in finalrecipepagesoup.findAll("li", class_="recipe-ingredients__list-item"):
        print(item.get_text())
        print("here is some ingredients")
        # these ingredients need to be fixed there are some issues with characters like \\u00bd and \\u00e9
        toaddthis =  item.get_text()
        toaddthis = toaddthis.strip("\\")
        ingredientslist.append(toaddthis)       
    print("here is my ingredients for this recipe", ingredientslist)                        
    print("here is the dictionary with all the recipes now:")
    
    allrecipedetails[recipetitle] = ingredientslist
    
    print("storing for json")
    
    makejsonready = {u"id": recipetitle, u"ingredients": ingredientslist}
    
    print(makejsonready)
    listforjsonoutput.append(makejsonready)
    
    #counter=counter+1
    #print(counter)
    print(allrecipedetails)
                

print("I have finished this letter %s woohoo!!!!!")
print("here is all the recipe details")
print(allrecipedetails)

print("here is the json")
print(listforjsonoutput)


print("here is the dictionary woohoo!!!!! I have got it")
print(allrecipedetails)
#recipes_json = json.dumps(allrecipedetails)
#print(recipes_json)


print("woohoo!!!!! I am writing all the recipe data to the file")  
with io.open('bbcgoodfoodrecipessample.json', 'w', encoding='utf-8') as f:
    json.dump(listforjsonoutput, f, ensure_ascii=False, indent=4, sort_keys=True)
    
  