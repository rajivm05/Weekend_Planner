from bs4 import BeautifulSoup as BS
import requests
import re
from selenium import webdriver
import time as time_module
import datetime
import textwrap
from tabulate import tabulate
def venue_list(show_timings_soup):
    d={}
    for venue in show_timings_soup.find('ul',{'id':'venuelist'}).findAll('li',{'class':'list'}):
        l=[]
        for show_time in venue.findAll('div',{'class':'showtime-pill-container'}):
            l.append(show_time.find('a').text.replace('\n','').replace('\t',''))
        d[venue['data-name']]=l
    ven_list=[]
    for i in list(d.keys()):
        ven_list.append([i])
    print(tabulate(ven_list, headers=['Venue'], tablefmt='orgtbl'))
    venue=input("Select a venue: ")
    print('showtimes available: ')
    print(*d[venue])
    time_chosen=input('Enter the showtime: ')
    return venue,time_chosen
def get_date_to_plan():
    date_list=[((datetime.date.today()+datetime.timedelta(days=i)).strftime('%d-%m')) for i in range(3)]
    print("select day of planning:")
    print(*date_list,sep=' OR ')
    date_to_plan_for=input()
    for i in date_list:
        if date_to_plan_for==i:
            return date_list.index(i)
def choose_date_and_navigate(driver):
    date_plan=get_date_to_plan()
    if date_plan==0:
        pass
    elif date_plan==1:
        driver.find_element_by_xpath('//*[@id="showDates"]/div/div/li[2]/a').click()
    elif date_plan==2:
        driver.find_element_by_xpath('//*[@id="showDates"]/div/div/li[3]/a').click()
def extra_details(href):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    response=requests.get(href,headers=headers)
    details_soup=BS(response.text,'html.parser')
    try:
        print("Votes: ",details_soup.find('div',{'class':'heart-rating'}).find('span',{'class':'__percentage'}).text)
        print("Critic rating: ",details_soup.find('div',{'class':'critic-rating'}).find('span',{'class':'__rating'}).find('ul',{'class':'rating-stars'})['data-value'])
        print("User rating: ",details_soup.find('div',{'class':'user-rating'}).find('span',{'class':'__rating'}).find('ul',{'class':'rating-stars'})['data-value'])
    except:
        print("Movie doesn't have votes or critic rating or user rating yet!" )
    try:
        print('Number of people interested in the movie: ',details_soup.find('div',{'class':'mv-coming-soon'}).find('span',{'class':'__votes'}).text)
    except:
        pass
    print("Cast:")
    for actor in details_soup.findAll('span',{'itemprop':'actor'}):
        print(actor.findAll('div',{'class':'__cast-member'})[0]['content'])
    print('Synopsis: ')
    print(*textwrap.wrap(details_soup.findAll('div',{'class':'synopsis'})[0].text.strip(),100),sep='\n')
def print_title(movie_title_href):
    data=[]
    for title in list(movie_title_href.keys()):
        data.append([title])
    print(tabulate(data, headers=['Movie'], tablefmt='orgtbl'))
def choose_film(movie_title_href):
    print_title(movie_title_href)
    title=input("Enter title of movie you'd like to see: ")
    return title,movie_title_href[title]
def now_showing(search_soup):
    href_now_showing={}
    for list_container in search_soup.find('div',{'class':'grid'}).findAll('div',{'class':'list-container'}):
        for div in list_container.findAll('div',{'class':'__event-container'}):
            href_now_showing[div.find('a').text]='https://in.bookmyshow.com'+div.find('a')['href']
    return href_now_showing
def movie_scrape(time='',location=''):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    path=r'C:\\Users\\rajiv\\Desktop\\Notes\\SEM-4\\Python\\Notebooks\\chromedriver.exe'
    driver=webdriver.Chrome(path)
    driver.get('https://in.bookmyshow.com/mumbai')
    while(True):
        try:
            time_module.sleep(5)
            driver.find_element_by_xpath('//*[@id="wzrk-cancel"]').click()
        except:
            pass
        time_module.sleep(5)
        driver.find_element_by_xpath('//*[@id="input-search-box"]').click()
        search_soup=BS(driver.page_source,'html.parser')
        now_showing_href=now_showing(search_soup)
        title,href=choose_film(now_showing_href)
        driver.get(href)
        book_soup=BS(driver.page_source,'html.parser')
        if input('Do you want to see extra details? ').lower()=='yes':
            extra_details('https://in.bookmyshow.com/'+str(book_soup.find('h1').find('a')['href']))
        #choosing date
        if input('Do you want to see show timings? ').lower()=='yes':
            choose_date_and_navigate(driver)
            if time != '':
                #filter the time using drop down menu and selenium
                pass
            show_timings_soup=BS(driver.page_source,'html.parser')
            venue,time=venue_list(show_timings_soup)
            end_time=(datetime.datetime.strptime(time,'%H:%M')+datetime.timedelta( minutes=30, hours=2)).time()
            
            return [title,venue,time,end_time]
            break
        else:
            if input('Would you like to choose another movie? ').lower()=='yes':
                driver.back()
def scrape_food(time='',location=''):
    url='https://www.zomato.com/mumbai'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    response=requests.get(url,headers=headers)
    page=BS(response.text,'html.parser')
    meal_type_box = page.findAll("div",{"class":"ui segment eight column doubling padded grid"})

    #get a list of available meal categories
    keys=[]
    for a in meal_type_box[0].findAll('div'):
        keys.append(a.text)
    keys.pop(0)
    keys.pop(0)
    if(time!=''):
        if datetime.datetime.strptime(time,'%H:%M').time()>datetime.datetime.strptime("7:00",'%H:%M').time() and datetime.datetime.strptime(time,'%H:%M').time()<datetime.datetime.strptime("12:00",'%H:%M').time():
            pass
        else:
            keys.remove("Breakfast")
        if datetime.datetime.strptime(time,'%H:%M').time()>datetime.datetime.strptime("12:00",'%H:%M').time() and datetime.datetime.strptime(time,'%H:%M').time()<datetime.datetime.strptime("16:00",'%H:%M').time():
            pass
        else:
            keys.remove("Lunch")
        if datetime.datetime.strptime(time,'%H:%M').time()>datetime.datetime.strptime("19:00",'%H:%M').time() and datetime.datetime.strptime(time,'%H:%M').time()<datetime.datetime.strptime("23:59",'%H:%M').time():
            pass
        else:
            keys.remove("Dinner")
        if datetime.datetime.strptime(time,'%H:%M').time()>datetime.datetime.strptime("20:00",'%H:%M').time():
            pass
        else:
            keys.remove("Drinks & Nightlife")
        
    keys_table=[]
    for i in keys:
        keys_table.append([i])
    print()
    print(tabulate(keys_table, headers=['Meal type'], tablefmt='orgtbl'))
    print()

    #get links to each category
    href=[]
    for a in meal_type_box[0].findAll('a'):
            href.append(a['href'])
    href.pop(0)
    href.pop(0)

    d1={}
    for i in range(len(keys)):
        d1[keys[i]]=href[i]

    choice=input("\nEnter type of meal: ")
    return sorting_order(choice,d1,keys)
def sorting_order(choice,d1,keys):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    #go to page corresponding to chosen meal type
    for i in range(len(keys)):
        if(choice==keys[i]):
            url2=d1[keys[i]]
    #print(url2)
    response1=requests.get(url2,headers=headers)
    page2=BS(response1.text,'html.parser')
    sort1=page2.findAll("div",{"class":"filter-padding search-filter-tab pt0 pb0"})

    sort_choice=[]
    for a in sort1[0].findAll('span'):
        if(a.text[0]!=" "):
            sort_choice.append(a.text.strip())
    sort_table=[]
    for i in sort_choice:
        sort_table.append([i])
    print()
    print(tabulate(sort_table, headers=['Sort By:'], tablefmt='orgtbl'))
    print()

    sort_href=[]
    for a in sort1[0].findAll('a'): 
        sort_href.append(a['href'])

    d2={}
    for i in range(len(sort_choice)):
        if re.search('https://www.zomato.com',sort_href[i]):
            d2[sort_choice[i]]=sort_href[i]
        else:
            d2[sort_choice[i]]='https://www.zomato.com'+sort_href[i]

    choice2=input("\nEnter how you want to sort: ")
    return restaurant_list(choice2,d2,sort_choice)
def restaurant_list(choice2,d2,sort_choice):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    #get url for restaurants
    for i in range(len(sort_choice)):
        if(choice2==sort_choice[i]):
            url3=d2[sort_choice[i]]
    #print(url3)
    response2=requests.get(url3,headers=headers)
    page3=BS(response2.text,'html.parser')
    details=page3.find("div",{"id":"orig-search-list"})
    cards=details.findAll("div",{"class":"content"})

    restaurant=[]
    href=[]
    address=[]
    search=[]
    search1=[]
    
    for card in cards:
        search.append(card.find('article').findAll('a',{'data-result-type':'ResCard_Name'}))
        search1.append(card.find('article').findAll('div',{'class':'col-m-16 search-result-address grey-text nowrap ln22'}))
        
    #fetch restaurant list
    for j in range(len(search)):
        for i in search[j]:
            restaurant.append(i.text.strip())
            href.append(i['href'])
            
    #fetch address of each restaurant
    for j in range(len(search1)):
        for i in search1[j]:
            address.append(i.text)
    rest_table=[]
    for i in restaurant:
        rest_table.append([i])
    print()
    print(tabulate(rest_table, headers=['Restaurants:'], tablefmt='orgtbl'))
    print()
    
    choice3=input("\nEnter name of restaurant: ")
    return get_address(choice3,address,restaurant)
def get_address(choice3,address,restaurant):
    for i in range(len(restaurant)):
        if(choice3==restaurant[i]):
            loc=address[i]
    print("\nThe address of %s is %s"%(choice3,loc))
    print()
    return get_time(loc)
def get_time(loc):
    start_time=input("Enter time at which you will visit the restaurant: ")
    #assuming person takes 1.5 hours to finish meal
    end_time=(datetime.datetime.strptime(start_time,'%H.%M')+datetime.timedelta( minutes=30, hours=1)).time()
    print("\nThe finish time of the meal is %s"%end_time)
    return [end_time,loc]
if __name__=='__main__':
    print("****************************WELCOME TO THE WEEKEND PLANNER****************************")
    choice=input('Would you like to go for a movie first or would you like to eat first?(Movie/Eating): ')
    if choice=='Movie':
        #the person chooses movie first
        details=movie_scrape()#details should be a list containing movie name, movie theatre, time of the movie,time of end of the movie
        details2=scrape_food(details[-1],details[1])#time of end of the movie will be passed 
        pass
    elif choice=='Eating':
        #the person chooses to eat first
        details=scrape_food()#details should be a list containing what meal it is(lunch,dinner,breakfast), place,what time the meal ends(consider 1.5-2 hours)
        details2=movie_scrape(details[0],details[1])#put in time here in the argument
        pass
    # print details and details 2
