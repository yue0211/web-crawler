import schedule
import time  
import requests,bs4,json
from datetime import datetime



def crawl():

  AnimeUrl = "https://acgsecrets.hk/bangumi/202204/"

  AnimeHeaders = {"Content-Type":"text/html","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"}

  AnimeResponse = requests.get(url=AnimeUrl, headers=AnimeHeaders)

  AnimeResponse.encoding = "utf-8" #為了避免爬蟲爬到的文字變成亂碼

  root = bs4.BeautifulSoup(AnimeResponse.text,"html.parser")

  AnimeAll = root.findAll(class_="card-like acgs-anime")

  AnimeName = [] #儲存爬到的所有新番的名字
  AnimeTime = [] #儲存爬到的所有新番的時間

  for Anime in AnimeAll:
    Name = Anime.find(class_="anime_info anime_names site-content-float").find(class_="entity_localized_name").text
    Time = Anime.find(class_="anime_info site-content-float").find(class_="anime_onair time_today").text
    index = Time.find("：")
    Time = Time[(index+1):].split("／")
    AnimeName.append(Name)
    AnimeTime.append(Time)

  jsonUrl = "https://api.jsonstorage.net/v1/json/ed324453-ff9a-490e-b380-6b3f0bb931ae/bc878350-0808-4916-b60c-dce3f6eee694" # 新番資訊儲存的開源json

  jsonHeaders = { "Content-Type": "application/json" ,"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"}

  Empty={} #為了讓開源的json檔案的內容,變成空

  Emptyjson = requests.put(url=jsonUrl+"?apiKey=525992cb-0741-450f-92d3-37b9a9b1cc85",headers=jsonHeaders,json=json.dumps(Empty,ensure_ascii=False)) # ensure_ascii=False => 為了讓json檔案內的文字不是亂碼

  if Emptyjson.status_code == 200:
    print("已清空json")
  else:
    print("無法清空json")

  jsonResponse = requests.get(url=jsonUrl, headers=jsonHeaders)

  data = jsonResponse.json() #解析json檔案,讓data變成disctionary

  count = 0 # 為了讓json檔的每個key值不相同

  for Title,Time in zip(AnimeName,AnimeTime):
    tempTitle = "Anime "+ str(count)
    tempTime = "Time "+ str(count)
    data[tempTitle] = Title
    data[tempTime] = Time
    count = int(count)
    count+=1
    
  updatejson = requests.put(url=jsonUrl+"?apiKey=525992cb-0741-450f-92d3-37b9a9b1cc85",headers=jsonHeaders,json=json.dumps(data,ensure_ascii=False))

  if updatejson.status_code == 200:
    print("已更新,新番的最新資訊")
  else:
    print("無法更新,新番的最新資訊")


schedule.every().day.at("8:00").do(crawl) #每天8點執行一次


while True:
  try:
    schedule.run_pending()
    time.sleep(1)
  except:
    print("終止程式")
    break

