import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

from requests.api import head

headers = {"Accept-Language" : "en-US, en;q=0.5"} #translate the page into English

url = "https://www.imdb.com/search/title/?groups=top_1000&ref_=adv_prv" 

results = requests.get(url, headers=headers) # gets the contents of the page by requesting the URL

soup = BeautifulSoup(results.text, "html.parser") #BeautifulSoup specifies the desired format of results using the HTML parser
# print(soup.prettify()) #prints out the parsed html


#the following variables are the types of data we want to extract
titles = []
years = []
times = []
imdb_ratings = []
metascores = []
votes = []
us_gross = []

#each movie div container
movie_div = soup.findAll('div', class_='lister-item mode-advanced') #finds all divs that have the class "lister-item mode-advanced"


for container in movie_div:
    name = container.h3.a.text #the name of the movie is inside the container > div > h3 > a > NAME (text)
    titles.append(name)

    year = container.h3.find('span', class_='lister-item-year').text
    years.append(year)

    time = container.find('span', class_='runtime').text if container.p.find('span', class_='runtime') else ''
    times.append(time)

    imdb = float(container.strong.text)
    imdb_ratings.append(imdb)

    m_score = container.find('span', class_='metascore').text if container.find('span', class_='metascore') else ''
    metascores.append(m_score)

    nv = container.find_all('span', attrs={'name' : 'nv'})
    vote = nv[0].text
    votes.append(vote)
    grosses = nv[1].text if len(nv) > 1 else '-'
    us_gross.append(grosses)
    

#dataframe with Pandas to break the data down into a nice table
movies = pd.DataFrame({

    'movie' : titles,
    'year' : years,
    'timeMin' : times,
    'imdb' : imdb_ratings, 
    'metascore' : metascores,
    'votes' : votes,
    'us_grossMillions' : us_gross,
})


movies['year'] = movies['year'].str.extract('(\d+)').astype(int)
movies['timeMin'] = movies['timeMin'].str.extract('(\d+)').astype(int)
movies['metascore'] = movies['metascore'].astype(int)
movies['votes'] = movies['votes'].str.replace(',', '').astype(int)

movies['us_grossMillions'] = movies['us_grossMillions'].map(lambda x: x.lstrip('$').rstrip('M'))
movies['us_grossMillions'] = pd.to_numeric(movies['us_grossMillions'], errors='coerce')
# easier way to do this is 
# movies['us_grossMillions'] = movies['us_grossMillions'].str.extract('(\d+\.\d+)').astype(float)

movies.to_csv('movies.csv')
