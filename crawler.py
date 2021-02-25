from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import ssl
import os

def get_page_content(url):
  try:
    url_text = urlopen(url).read().decode('utf8')
    return url_text
  except Exception as e:
    return None
def save(title,content):
  f = open(title+".txt",'w',encoding = 'utf-8', errors = 'ignore')
  f.write(content)
  f.close()

def clean_title(title):
  invalid_char= ['<','>',':','"','/','\\','|','?','*']
  for c in invalid_char:
    title = title.replace(c,'')
  return title

def get_urls(soup):
  links = soup.find_all('a')
  urls = []
  for link in links:
    urls.append(link.get('href'))
  return urls

def is_url_valid(url):
  if url is None:
    return False
  if re.search('#',url):
    return False
  match = re.search('^/wiki/',url)
  if match:
    return True
  else:
    return False

def reformat_url(url):
  match = re.search('^/wiki/',url)
  if match:
    return "https://en.wikipedia.org"+url
  else:
    return url

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

seedUrls = ["https://en.wikipedia.org/wiki/Machine_learning","https://en.wikipedia.org/wiki/Artificial_intelligence"]
relatedTerms = ["artificial intelligence", "machine","machine learning","neural net","computer mind","statistics","learning","deep learning","optimization","data mining"]
q = []
visitedUrls = []
pageCounter = 0
savedUrls = []
savedtitle = []
for url in seedUrls:
    q.append(url)
    #visitedUrls.append(url)
while q:
    url = q[0]
    if is_url_valid(url) and url not in visitedUrls:
      visitedUrls.append(url)
    q.pop(0)
    page_text = get_page_content(url)
    if page_text is None:
      continue
    termCounter = 0
    soup = BeautifulSoup(page_text,'html.parser')
    main_text = soup.get_text()
    
    for term in relatedTerms:
      if re.search(term, main_text, re.I):
        termCounter+=1
        if termCounter >= 2 and url not in savedUrls:
          title = soup.title.string
          title = clean_title(title)
          if title not in savedtitle:
            savedtitle.append(title)
            save(title,main_text)
            savedUrls.append(url)
            pageCounter+=1
            print("page title:", title,"\nPage number:",pageCounter,"\nterm counter:", termCounter,"\nUrl:",url,"\n")
            break
    if pageCounter >= 500:
      break
    outGoingUrls = get_urls(soup)
    for url in outGoingUrls :
      if is_url_valid(url) and url not in visitedUrls:
        url = reformat_url(url)
        q.append(url)
        visitedUrls.append(url)
f = open("crawled_urls.txt","w")
i = 1
for url in visitedUrls:
  f.write(str(i)+': '+url+'\n')
  i+=1
f.close()