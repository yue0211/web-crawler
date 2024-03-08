import requests,bs4,json,pytz,datetime,time,schedule



def InsertUrl():
  global day
  Url = "https://acgsecrets.hk/bangumi/"

  for year in range(2022,2030):  #為了自動化執行程式，因此事先將2022到2030的所有新番的網址存進day
    for month in range(1,11,3):
      if month!=10:
        temp = Url+str(year)+"0"+str(month)+"/"
      else:
        temp = Url+str(year)+str(month)+"/"
      day.append(temp)


def validUrl(): #挑選出合法的url 

  global day
  now = datetime.datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y%m")  # 抓取當前時間,並設定時區

  nextseason = "https://acgsecrets.hk/bangumi/"+ now[:-2] #儲存下一季新番的網址

  if(now[-2:]=="02" or now[-2:]=="03"):  # 這些月份沒有新番資訊,因此要特別處理
    nextseason+="04"
    now = now[:-2]+"01"
  elif(now[-2:]=="05" or now[-2:]=="06"):
    nextseason+="07"
    now = now[:-2]+"04"
  elif(now[-2:]=="08" or now[-2:]=="09"):
    nextseason+="10"
    now = now[:-2]+"07"
  elif(now[-2:]=="11" or now[-2:]=="12"):
    year = int(now[:-2])+1
    nextseason = nextseason[0:30]+str(year)+"01"
    now = now[:-2]+"10"
  else:             # 這些月份有新番資訊
    if(now[4:]=="01"):
      nextseason+="04"
    elif(now[4:]=="04"):
      nextseason+="07"
    elif(now[4:]=="07"):
      nextseason+="10"
    elif(now[4:]=="10"):
      year = int(now[:-2])+1
      nextseason = nextseason[0:30]+str(year)+"01"


  for season in day:
    if(now == season[30:36]): # 挑出年月相同的Url作爬蟲
      print("準備爬取"+season[30:36]+"的新番資訊")
      print("準備爬取"+nextseason[30:36]+"的新番資訊")
      temp=[season,nextseason]
      return temp


def crawl(AnimeUrl,season): #爬蟲

  AnimeHeaders = {"Content-Type":"text/html","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"}

  AnimeResponse = requests.get(url=AnimeUrl, headers=AnimeHeaders)

  AnimeResponse.encoding = "utf-8" #為了避免爬蟲爬到的文字變成亂碼

  root = bs4.BeautifulSoup(AnimeResponse.text,"html.parser")

  AnimeAll = root.findAll(class_="card-like acgs-anime")

  if len(AnimeAll)==0:
    print("尚未更新此月份的新番資訊")
    return

  AnimeName = [] #儲存爬到的所有新番的名字
  AnimeTime = [] #儲存爬到的所有新番的時間

  totalAnime=[]

  for Anime in AnimeAll:
    Name = Anime.find(class_="anime_info anime_names site-content-float").find(class_="entity_localized_name").text
    # print(Name)
    Time = Anime.find(class_="time_today main_time").text
    # print(Time)
    index = Time.find("：")
    Time = Time[(index+1):].split("／")
    dictAnime = {}
    dictAnime["name"] = Name
    if len(Time)==1: # 時間未定
      dictAnime["first"] = Time[0]
      dictAnime["update"] = Time[0]
    elif len(Time)==2: # 時間資訊包含兩個的狀況
      dictAnime["first"] = "跨季撥放"
      dictAnime["update"] = Time[0][:3]
    else: #時間資訊包含三個的狀況(普遍狀況)
      dictAnime["first"] = Time[0][:-1]
      dictAnime["update"] = Time[1][:3]
    totalAnime.append(dictAnime)

  jsonUrl = "https://api.jsonstorage.net/v1/json/ed324453-ff9a-490e-b380-6b3f0bb931ae/f938fd06-ece7-4de7-b7b6-f34ebd399293" # 新番資訊儲存的開源json

  jsonHeaders = { "Content-Type": "application/json" ,"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"}

  if(season=="season"): #清除前一次的資料

    Empty={} #為了讓開源的json檔案的內容,變成空

    Emptyjson = requests.put(url=jsonUrl+"?apiKey=525992cb-0741-450f-92d3-37b9a9b1cc85",headers=jsonHeaders,json=json.dumps(Empty,ensure_ascii=False)) # ensure_ascii=False => 為了讓json檔案內的文字不是亂碼

    if Emptyjson.status_code == 200:
      print("已清空json")
    else:
      print("無法清空json")

  jsonResponse = requests.get(url=jsonUrl, headers=jsonHeaders)

  data = jsonResponse.json() #解析json檔案,讓data變成dictionary

  data[season]=totalAnime

  updatejson = requests.put(url=jsonUrl+"?apiKey=525992cb-0741-450f-92d3-37b9a9b1cc85",headers=jsonHeaders,json=json.dumps(data,ensure_ascii=False))

  if updatejson.status_code == 200:
    if season == "season":
      print("已更新本季新番的最新資訊")
    else:
      print("已更新下季新番的最新資訊")
  else:
    print("無法更新,新番的最新資訊")


def setSeason():
  seasons = validUrl() 
  for url,count in zip(seasons,range(2)): #分別對當季和下一季的新番資訊作爬蟲
    if(count==0):
      crawl(url,"season")
    else:
      crawl(url,"nextseason")



# schedule.every().day.at("09:00").do(setSeason) #每天9點執行一次
# schedule.every(5).seconds.do(setSeason) #每5秒執行一次

day=[]
InsertUrl()
setSeason()


# print("程式開始")
# while True:
#   try:
#     schedule.run_pending()
#     time.sleep(1)
#   except:
#     print("終止程式")
#     break
# print("程式結束")
