import requests
import json
import datetime
import sys


url = "https://api.github.com/repos/joda01/imagec/releases"
token = sys.argv[1]

headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "joda01",
    "Authorization": "token "+token
}

downloadCount = 0
while url:
    response = requests.get(url, headers=headers)
    url = ""
    if response.status_code == 200:
        data = response.json()

        for employee in data:
            for asset in employee["assets"]:
                count = asset["download_count"]
                downloadCount = downloadCount + count

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
yesterday = datetime.date.today() - datetime.timedelta(days=1)

date_string_now = now.strftime("%Y-%m-%d")
date_string_yesterday = yesterday.strftime("%Y-%m-%d")

dataToWrite={}
with open("stats.json", "r") as f:
    json_string = f.read()
    dataToWrite = json.loads(json_string)
    downloadsYesterday = dataToWrite[date_string_yesterday]["downloadsCountAccumulated"]
    downloadsToday = downloadCount - downloadsYesterday
    dataToWrite[date_string_now] = {"downloadsToday": downloadsToday, "downloadsCountAccumulated" : downloadCount}


json_string = json.dumps(dataToWrite, indent=4)
with open("stats.json", "w") as f:
    f.write(json_string)
