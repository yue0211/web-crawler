import requests,bs4,json,time,schedule,re

def crawl_website():
    crawl("https://www.cartoonmad.com/comic99.html")


def updateJson(totalComic):
  jsonResponse = requests.get(url=jsonUrl, headers=jsonHeaders)
  data = jsonResponse.json() #解析json檔案,讓data變成dictionary
  data["comic"]=totalComic
  updatejson = requests.patch(url=jsonUrl+"?apiKey=a3b601e2-ddac-4f01-92f3-920db456c913",headers=jsonHeaders,json=json.dumps(data,ensure_ascii=False))
  if updatejson.status_code == 200:
    print("已更新json")
  # print(data["comic"])


def catchPage(mainComicUrl):
  mainComicHeaders = {"Content-Type":"text/html","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"}
  mainComicResponse = requests.get(url=mainComicUrl, headers=mainComicHeaders)
  mainComicResponse.encoding = "Big5 " #為了避免爬蟲爬到的文字變成亂碼
  root = bs4.BeautifulSoup(mainComicResponse.text,"html.parser")
  pages = root.find_all("font",{"style":"font-size:8pt;color: #888888;" })
  page=[]
  for p in pages:
    page.append(re.search(r'\d+', p.text).group())
  return page

def catchEpisode(mainComicUrl):
  mainComicHeaders = {"Content-Type":"text/html","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"}
  mainComicResponse = requests.get(url=mainComicUrl, headers=mainComicHeaders)
  mainComicResponse.encoding = "Big5 " #為了避免爬蟲爬到的文字變成亂碼
  root = bs4.BeautifulSoup(mainComicResponse.text,"html.parser")
  fieldsets = root.find_all("fieldset")
  tables=fieldsets[1].find_all("table",{"width":"800","align":"center" })
  href=[]
  for table in tables:
    hrefs=table.find_all("a")
    for h in hrefs:
      href.append(h.text)
  return href

  
def crawl(comicUrl): #爬蟲
  totalComic=[]
  with open("urlUpdate.txt", 'r') as file:
    content = file.read()
  print("動漫狂的圖片網址:"+content)
  comicHeaders = {"Content-Type":"text/html","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"}
  comicResponse = requests.get(url=comicUrl, headers=comicHeaders)
  comicResponse.encoding = "Big5 " #為了避免爬蟲爬到的文字變成亂碼
  root = bs4.BeautifulSoup(comicResponse.text,"html.parser")
  covertexts = root.find_all(class_="covertxt")
  titles = root.find_all(class_="a1")
  # print(len(covertexts))
  # print(len(titles))
  for covertext,title in zip(covertexts,titles):
    my_dict = {}
    my_dict["name"] = title.text
    my_dict["update"] = re.search(r'\d+',covertext.text).group()
    my_dict["comicImgUrl"] = content+re.search(r'\d+', title["href"]).group()+"/"
    new_dict = dict(zip(catchEpisode("https://www.cartoonmad.com/"+title["href"]), catchPage("https://www.cartoonmad.com/"+title["href"])))
    my_dict["pages"] = new_dict
    totalComic.append(my_dict)
    # break #記得刪掉
  
  updateJson(totalComic)




# schedule.every().day.at("09:00").do(crawl_website) #每天9點執行一次

# print("程式開始了")
# while True:
#   try:
#     schedule.run_pending()
#     time.sleep(1)
#   except:
#     print("終止程式")
#     break
# print("程式結束")


Empty={} #為了讓開源的json檔案的內容,變成空
jsonUrl = "https://api.jsonstorage.net/v1/json/6ac1356d-f534-42c8-96d0-b02a2d0b8b4c/30fadcf0-af3e-4798-bb6a-43eb9941d7db"
jsonHeaders = { "Content-Type": "application/json" ,"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"}
EmptyJson = requests.put(url=jsonUrl+"?apiKey=525992cb-0741-450f-92d3-37b9a9b1cc85",headers=jsonHeaders,json=json.dumps(Empty,ensure_ascii=False)) # ensure_ascii=False => 為了讓json檔案內的文字不是亂碼

# if EmptyJson.status_code==200:   #無法正常運作
#   print("已清空json")
# else:
#   print(EmptyJson.status_code)


for i in range(1,3):
  URL="https://www.cartoonmad.com/comic99.0"+str(i)+".html"
  crawl(URL)





