# Web Scrape BBC Food recipes

This is a small script to web scrape all the recipes published on https://www.bbc.co.uk/food/recipes

There are two version of the same script, a .py and a Jupyter versions. 

This is a small *working-in-progress* project for training purpose.

The recipes are order in alphabetic order and for each of the letters there are more than one pages of recipes. 

The script scrapes any images of the meal, the category of the meal, the ingredients, preparetion, url and chef name. It saves a CSV file of for each letters. 

The main function allows to scrape starting from a specific letter. 

If we want to start scrapping from the recipes under a different alphabetic letter, it is enough to change the parameter in the call function  ```web_scraper_bbc_food('a') ``` 
