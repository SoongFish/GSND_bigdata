'''
    @Filename | CN.py (ClienNews.py)
    @Author   | SoongFish
    @Date     | 2020.09.04.
    @Desc     | Scrape news on "clien.net/service/board/news" and send your Telegram.
'''

import requests
import lxml.html
import time
import telegram

temp = "init"
cnt = 0

my_token = '1234567890:ABCDEF..' # Input own's Telegram token
bot = telegram.Bot(token = my_token)
chat_id = 123456789 # Input own's Telegram chat_id

while(True):
    response = requests.get("https://www.clien.net/service/board/news")
    response.encoding = 'euc-kr'
    root = lxml.html.fromstring(response.content.decode('UTF-8'))
    root.make_links_absolute(response.url)
    
    for line in root.xpath('//*[@id="div_content"]/div[7]/div'):
        data_url = line.xpath('div[2]/a[1]')[0] 
        url = data_url.get("href")
        
        data_title = line.xpath('div[2]/a[1]/span')[0]
        title = data_title.get("title")
        if title.startswith("\""):
            title = "test!!" + title[1:]
        
        #data_reply = line.xpath('div[2]/a[2]/span')[0]
        #reply = data_reply.get("")
        #print(title, url, sep = "\t", end = "\n")
        
        if temp == "init":
            cnt += 1
            print(str(cnt) + ". " + title)
            temp = title  
            bot.sendMessage(chat_id = chat_id, text = str(cnt) + ". [" + title + "]\n\n" + url)
        else:
            if temp != title:
                cnt += 1
                print(str(cnt) + ". " + title)
                temp = title
                bot.sendMessage(chat_id = chat_id, text = str(cnt) + ". [" + title + "]\n\n" + url)
        break
    
    time.sleep(60)