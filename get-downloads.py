import requests
import json
import datetime
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import urllib.request

def getEvaStats():
    urllib.request.urlretrieve("https://sites.imagej.net/stats.json", "stats_eva.json")
    nrTotal = 0
    with open('stats_eva.json') as f:
        stats = json.load(f)
        ev = stats["evanalyzer"]
        for date, nr in ev.items():
            print(date + " " + str(nr))
            nrTotal = nrTotal + nr

def getStats(token):

    url = "https://api.github.com/repos/joda01/imagec/releases"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "joda01",
        "Authorization": "token "+token
    }

    
    downloadCountAssets = {}

    while url:
        response = requests.get(url, headers=headers)
        url = ""
        if response.status_code == 200:
            data = response.json()

            for employee in data:
                for asset in employee["assets"]:
                    assetId = str(asset["id"])
                    downloadCountAssets[assetId]= {}
                    downloadCountAssets[assetId]["downloadCount"] = asset["download_count"]
                    downloadCountAssets[assetId]["name"] = asset["name"]
                    downloadCountAssets[assetId]["tagName"] = employee["tag_name"]
                    downloadCountAssets[assetId]["publishedAt"] = employee["published_at"]

            link_header = response.headers.get("Link")
            if link_header:
                links = link_header.split(",")
                index = 0
                while index < len(links):
                    link = links[index]
                    if "next" in link:
                        link = link.split(";")[0]
                        url = link.replace("<", "").replace(">", "")
                    index += 1

                print(url)
            else:
                print("No next link found.")
        else:
            print("Error:", response.status_code, response.reason)


    now = datetime.datetime.now()
    date_string_now = now.strftime("%Y-%m-%d")

    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    date_string_yesterday = yesterday.strftime("%Y-%m-%d")

    daysToSubtract = 1
    dataToWrite={}
    with open("stats.json", "r") as f:
        json_string = f.read()
        dataToWrite = json.loads(json_string)
        
        while date_string_yesterday not in dataToWrite:
            daysToSubtract = daysToSubtract + 1
            yesterday = datetime.date.today() - datetime.timedelta(days=daysToSubtract)
            date_string_yesterday = yesterday.strftime("%Y-%m-%d")

        print(date_string_yesterday)
        downloadCountAssetsYesterday = dataToWrite[date_string_yesterday]["downloadCountAssets"]
        downloadCountAssetsYesterday.update(downloadCountAssets)

        downloadCount = 0
        downloadCountWinCount = 0
        downloadCountMacOsCount = 0
        downloadCountLinuxCount = 0
        downloadCountSourceCount = 0
        downloadCountOtherCount = 0

        for assetKey, assetValue in downloadCountAssetsYesterday.items():
            downloadCount = downloadCount + assetValue["downloadCount"]

            name = assetValue["name"]
            if "win" in name:
                downloadCountWinCount = downloadCountWinCount + assetValue["downloadCount"]
            elif "macos" in name:
                downloadCountMacOsCount = downloadCountMacOsCount + assetValue["downloadCount"]
            elif "linux" in name:
                downloadCountLinuxCount = downloadCountLinuxCount + assetValue["downloadCount"]
            elif "Source" in name:
                downloadCountSourceCount = downloadCountSourceCount + assetValue["downloadCount"]
            else:
                downloadCountOtherCount = downloadCountOtherCount + assetValue["downloadCount"]


        downloadsYesterday = dataToWrite[date_string_yesterday]["downloadsCountAccumulated"]
        downloadsToday = downloadCount - downloadsYesterday
        
        downloadsWinYesterday = dataToWrite[date_string_yesterday]["downloadCountDetails"]["win"]["downloadsCountAccumulated"]
        downloadsWinToday = downloadCountWinCount - downloadsWinYesterday

        downloadsMacOsYesterday = dataToWrite[date_string_yesterday]["downloadCountDetails"]["macos"]["downloadsCountAccumulated"]
        downloadsMacOsToday = downloadCountMacOsCount - downloadsMacOsYesterday

        downloadsLinuxYesterday = dataToWrite[date_string_yesterday]["downloadCountDetails"]["linux"]["downloadsCountAccumulated"]
        downloadsLinuxToday = downloadCountLinuxCount - downloadsLinuxYesterday
        
        downloadsSourceYesterday = dataToWrite[date_string_yesterday]["downloadCountDetails"]["source"]["downloadsCountAccumulated"]
        downloadsSourceToday = downloadCountSourceCount - downloadsSourceYesterday
        
        downloadsOtherYesterday = dataToWrite[date_string_yesterday]["downloadCountDetails"]["other"]["downloadsCountAccumulated"]
        downloadsOtherToday = downloadCountOtherCount - downloadsOtherYesterday

        dataToWrite[date_string_now] = {"downloadsToday": downloadsToday, 
                                        "downloadsCountAccumulated" : downloadCount,
                                        "downloadCountDetails":{
                                            "win":   {"downloadsToday":downloadsWinToday ,  "downloadsCountAccumulated":downloadCountWinCount }, 
                                            "macos": {"downloadsToday":downloadsMacOsToday ,"downloadsCountAccumulated":downloadCountMacOsCount }, 
                                            "linux": {"downloadsToday":downloadsLinuxToday ,"downloadsCountAccumulated":downloadCountLinuxCount },
                                            "source": {"downloadsToday":downloadsSourceToday ,"downloadsCountAccumulated":downloadCountSourceCount },
                                            "other": {"downloadsToday":downloadsSourceToday ,"downloadsCountAccumulated":downloadCountOtherCount }
                                        },
                                        "downloadCountAssets": downloadCountAssetsYesterday}
        
        #
        # Cleanup the history from the day after tomorrow
        #
        daysToSubtract = daysToSubtract + 1
        yesterday = datetime.date.today() - datetime.timedelta(days=daysToSubtract)
        date_string_yesterday = yesterday.strftime("%Y-%m-%d")
        while date_string_yesterday not in dataToWrite:
            daysToSubtract = daysToSubtract + 1
            yesterday = datetime.date.today() - datetime.timedelta(days=daysToSubtract)
            date_string_yesterday = yesterday.strftime("%Y-%m-%d")
        
        dataToWrite[date_string_yesterday].pop("downloadCountAssets",None)

                        


    json_string = json.dumps(dataToWrite, indent=4)
    with open("stats.json", "w") as f:
        f.write(json_string)

def generateFigure(y_values,y_valueAccumulatedEva, time_values, fileName):
    # Plot the graph
    plt.figure(figsize=(10, 5))
   
    time_values_dt = [datetime.datetime.strptime(d, "%Y-%m-%d") for d in time_values]

    plt.plot(time_values_dt, y_valueAccumulatedEva, marker='', linestyle='-', color='b', label="Line 2")

    plt.plot(time_values_dt, y_values, marker='', linestyle='-', color='g')



    # Set labels and title
    plt.xlabel("")
    plt.ylabel("Downloads", fontsize=16)
    plt.title("")
    plt.grid(True)  # Display the grid


    # Limit to 10 x-axis ticks
    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=4))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    plt.xticks(rotation=45, fontsize=16) # X-axis tick labels
    plt.yticks(fontsize=16)              # Y-axis tick labels
    plt.tight_layout()
    plt.savefig(fileName)
    plt.close()


def generateGraph(lastXDays):
    with open("stats.json", "r") as f:
        json_string = f.read()
        parsedData = json.loads(json_string)
        time_values=[]
        y_values=[]
        y_valuesEva=[]
        y_valueAccumulated=[]
        y_valueAccumulatedEva=[]

    with open("stats_eva.json", "r") as f:
        json_string_eva = f.read()
        parsedDataEva = json.loads(json_string_eva)["evanalyzer"]

        # Get today's date
        today = datetime.date.today()
        x_days_ago = datetime.date(2022, 1, 1)
        
        current = x_days_ago
        lastAccu = 0
        lastAccuEva = 0
        while current <= today:
            current_day_str = current.strftime("%Y-%m-%d")
            current_day_str_Ax = current.strftime("%Y")
            
            if current_day_str in parsedData:
                data = parsedData[current_day_str]
                time_values.append(current_day_str)
                y_values.append(int(data["downloadsToday"]))
                y_valueAccumulated.append(int(data["downloadsCountAccumulated"]))
                lastAccu = int(data["downloadsCountAccumulated"])
            else:
                time_values.append(current_day_str)
                y_values.append(int(0))
                y_valueAccumulated.append(int(lastAccu))

            if current_day_str in parsedDataEva:
                data = parsedDataEva[current_day_str]
                lastAccuEva = int(data)+lastAccuEva
                y_valuesEva.append(int(data))
                y_valueAccumulatedEva.append(lastAccuEva)
            else:
                y_valueAccumulatedEva.append(lastAccuEva)
                y_valuesEva.append(int(0))


            current += datetime.timedelta(days=1)


                
        generateFigure(y_values,y_valuesEva,time_values, "downloads_per_day.png")
        generateFigure(y_valueAccumulated,y_valueAccumulatedEva,time_values, "downloads_accumulated.png")





token = sys.argv[1]
getStats(token)
getEvaStats()
generateGraph(90)