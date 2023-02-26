from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import time
import re

driver = webdriver.Chrome('/home/dabyzness/chromedriver/stable/chromedriver')
driver.get("https://menu.thecheesecakefactory.com/nj/jersey-city-194/small-plates-snacks/")
# Page doesn't load fast enough so I need to pause before continuuing
time.sleep(1)

content = driver.page_source
soup = BeautifulSoup(content, "html.parser")

# Grab menu categories
categories = soup.find_all('button', attrs={"class": "button-menu-main"})
categoriesText = [x.text for x in categories]

# Store list of categories we want to skip:
skip = ['Welcome', 'From the Bar', 'Lunch Favorites', 'Beverages', 'Kids Menu', 'Happy Hour', 'Temporarily Unavailable' ]

# Grab the actual menu sections
sections = soup.find_all('section', attrs={"class": "menu-area"})

# Create dictionary to store items
menu = {}

for i, category in enumerate(categoriesText):
  if category in skip:
    continue
  
  subcategories = sections[i].find_all("ul", attrs={'class': 'menu-section'})

  # This is where I'm storing the menu
  subcategoryMenu = []
  
  for subcategory in subcategories:
    subcategoryName = subcategory.find('h2', attrs={'class': 'menu-subsection-title'}).text
    items = subcategory.find_all("li", attrs={"class": "menu-item"})
    
    # We're not including any drinks
    if subcategoryName == "Skinny Cocktails":
      continue
    
    # Price isn't listed for these -- only a range so I took the average
    if subcategoryName == 'Cheesecakes':
      itemsList = [{item.find('h3').text: {'calories': int(re.search('(?<=\()[0-9]{1,}', item.find('p', attrs={'class': 'menu-item-description'}).text).group(0)), 'price': 10.25}} for item in items]
    else: 
      # No real reason to have a list comprehension be so long, just for fun.
      # Turning each item into --> { itemName: { calories: num, price: num }}
      # Also had to take into account calories that are listed: 240-480 cal.
      # Fun fact, Cheesecake factory doesn't use "-", they use "–" ...
      itemsList = [{item.find('h3').text: {'calories': int(item.find('span', attrs={'class': 'menu-item-option-calories'}).text.split(" ")[0].split("–")[0]), 'price': float(item.find('span', attrs={'class': "menu-item-option-price"}).text[1:])}} if item.find('span', attrs={'class': 'menu-item-option-calories'}) else {item.find('h3').text: {'calories': int(re.search('(?<=\()[0-9]{1,}', item.find('p', attrs={'class': 'menu-item-description'}).text).group(0)), 'price': float(item.find('span', attrs={'class': "menu-item-option-price"}).text[1:])}} for item in items]
      
    subcategoryMenu.append({subcategoryName: itemsList})
    
  if len(subcategoryMenu) > 1:
    tempField = {'subcategories': subcategoryMenu}
    menu[category] = tempField
  else:
    menu[category] = list(subcategoryMenu[0].values())[0]
  
# Unsure whether I want a TypeScript or JavaScript file so I made both
with open('src/output/cheesecakeMenu.ts', 'w') as file:
  file.write('export const cheesecakeMenu = { menu: ' + str(menu) + '};')
  
with open('src/output/cheesecakeMenu.js', 'w') as file:
  file.write('export const cheesecakeMenu = { menu: ' + str(menu) + '};')