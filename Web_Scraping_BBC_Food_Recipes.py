import os
import urllib.request
import re
import pandas as pd
from bs4 import BeautifulSoup
import time
import requests


BBC_MAIN_URL = 'https://www.bbc.co.uk/'
current_folder = os.getcwd()


def make_directories(folder):
    #make a new directory to save the images
    if not os.path.exists(folder):
        os.makedirs(folder)
        
def dataset(index_images_list, categories, names_recipes_list, links_to_recipes, ingredients_plus_quantities, methods, chef_list, images_yes_no,alphabetic_letter, newpathcsv):    
    list_all = []
    for i in range(len(links_to_recipes)):
        
        
        new_ls = [categories[i], names_recipes_list[i], links_to_recipes[i] , '; '.join(ingredients_plus_quantities[i]), methods[i], chef_list[i], images_yes_no[i], index_images_list[i]]
        list_all.append(new_ls)
    data = pd.DataFrame(list_all, columns = ['category', 'name_recipe', 'links', 'ingred_and_quant', 'descr_method', 'chef', 'images_yes_no', 'index_images'])
    name_dataset = 'dataset_'+alphabetic_letter.upper()+'.csv'
    data = data.to_csv(os.path.join(newpathcsv, name_dataset), index = True)


def web_scraper_bbc_food(letter = 'a'):
    
    newpathcsv = os.path.join(current_folder,'csv_data')
    newpathimages = os.path.join(current_folder,'images')
    make_directories(newpathcsv)
    make_directories(newpathimages)
    
    #homepage with the indexes pages to find the recipes https://www.bbc.co.uk/food/recipes/a-z/a/1#featured-content
    url_initial_page = ''.join((BBC_MAIN_URL,'/food/recipes/a-z/', letter ,'/1#featured-content'))
    headers = {'connection':'close','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
    
    time.sleep(3)

    reqpage = urllib.request.Request(url_initial_page, headers = headers)
    respagep = urllib.request.urlopen(reqpage)
    respagepData = respagep.read()


    #alphabetic links at the top page
    links_alphabetic = re.findall(r'<ul class="az-keyboard__list">(.*?)</ul>',  respagepData.decode('UTF-8'))
    links_alphabetic = re.findall(r'<a class=.*? href=(.*?)>', str(links_alphabetic))
    
    
    #links = ['/food/recipes/a-z/0-9/1#featured-content']
    links_top_page = []
    for i in links_alphabetic:
        links_from_letter = ''.join(('/food/recipes/a-z/', letter ,'/1#featured-content'))
        if i[1:-1] >= links_from_letter:
            links_top_page.append(i)
    
    print(links_top_page)
    count_recipes_w_images = 0
    count_pages = 1
    for link_top_page in links_top_page:
        
        lk = link_top_page[1:-1]
        url = ''.join((BBC_MAIN_URL,lk))
        print(url, 'url')
        headers = {'connection':'close','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
        time.sleep(3)


        alphabetic_letter = re.findall(r'/food/recipes/a-z/(.*?)/[0-9]+#', lk)
        page = urllib.request.Request(url,headers = headers)
        reqpage = urllib.request.urlopen(page)
        reqpagepData = reqpage.read()

        #links at the bottom page 
        links_on_index = re.findall(r'<a class="pagination__link gel-pica-bold" href=(.*?)>', reqpagepData.decode('UTF-8'))


        #find the maxiumn number of pages in the alphabetic section of each main pages
        num_pages = []
        for i in links_on_index:
            num = re.findall(r'([0-9]+)#', i)
            num_pages.extend(num)
            
        if len(num_pages) == 0:
            num_max_index = 1
        else:
            num_max_index = int(max(num_pages))


        index_images_list, categories, names_recipes_list, links_to_recipes, ingredients_plus_quantities, methods, chef_list, images_yes_no, = ([]for i in range(8))

        for index_link in range(1,num_max_index+1):
            print(alphabetic_letter,'alphabetic_letter')
            url = ''.join((BBC_MAIN_URL,"food/recipes/a-z/"+alphabetic_letter[0]+"/"+str(index_link)+"#featured-content"))
            headers = {'connection':'close','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}

            time.sleep(3)

            page_index = urllib.request.Request(url,headers = headers)
            reqpage_index = urllib.request.urlopen(page_index)
            reqpageData_idex = reqpage_index.read()

             #links to the recipes
            links_on_main_page = re.findall(r'<div class="gel-layout__item gel-1/2 gel-1/3@m gel-1/4@xl">(.*?)</div>', reqpageData_idex.decode('UTF-8'))
            links_on_main_page = list(set(links_on_main_page))


            #extracts links to recipes and their food categories
            links_and_categories = []
            for link in links_on_main_page:
                link_temp = re.findall(r'<a class="promo promo__(.*?)" href=(.*?)>', link)
                links_and_categories.extend(link_temp)

            for category, link in links_and_categories:
                
                #separate in tuples the caterigories of the food from their web page links
                link_bbc = ''.join((BBC_MAIN_URL, link[2:-1]))
                categories.append(category)
                links_to_recipes.append(link_bbc)
                

                url = link_bbc
                headers = {'connection':'close','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}

                time.sleep(3)

                req = urllib.request.Request(url, headers = headers)
                resp = urllib.request.urlopen(req)
                respData = resp.read()

                #finds the chef or author of the recipe
                chef = re.findall(r'<a class="chef__link" href="/food/chefs/.*?">(.*?)</a>', respData.decode('UTF-8'))
                chef_list.append(chef[0])

                #find image if any
                image = re.findall(r'<div class="recipe-media__image responsive-image-container__16/9">(.*?)</div>', respData.decode('UTF-8'))
                image_links = re.findall(r'<.*?src="(.*?)"', str(image))

                #name recipe
                name = re.findall(r'<h1 class="gel-trafalgar content-title__text">(.*?)</h1>',respData.decode('UTF-8') )
                names_recipes_list.append(name[0])

                #description of the method to prepare the recipes
                method = re.findall(r'<ol class="recipe-method__list">(.*?)</ol>',  respData.decode('UTF-8'))
                method = re.sub(r'<.*?>|\\',"",str(method)).strip()
                methods.append(method[1:-1])

                #search for the ingredients
                ingr = re.findall('<ul class="recipe-ingredients__list">(.*?)</ul>', respData.decode('UTF-8'))
                ingred = re.findall(r'.+>(.*?)<.+', str(ingr))
                ingredients = re.findall('<li class="recipe-ingredients__list-item"> *(.*?)</li>', str(ingr))#just ingredients
                
                
                ing = []
                for i in ingredients:
                    ingred = re.sub(r'<.*?>',"",str(i).strip())
                    ing.append(ingred)
                ingredients_plus_quantities.append(ing)

                if len(image_links) != 0:

                    # set filename and image URL
                    index_name_image = ''.join((alphabetic_letter[0], str(count_recipes_w_images)))
                    filename = 'image_'+ index_name_image +'.jpg'
                    filename_path = os.path.join(newpathimages, filename)
                    image_url = image_links[0]

                    # call urlretrieve function to download image
                    urllib.request.urlretrieve(image_url, filename_path)
                    images_yes_no.append('yes')
                    index_images_list.append(index_name_image)
                else:
                    images_yes_no.append('no')
                    index_images_list.append('')

                count_recipes_w_images +=1
        count_pages +=1
        dataset(index_images_list, categories, names_recipes_list, links_to_recipes, ingredients_plus_quantities, methods, chef_list, images_yes_no, alphabetic_letter[0],newpathcsv)


web_scraper_bbc_food('a')    

