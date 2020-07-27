from flask import Flask, jsonify
from flask_apscheduler import APScheduler
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import os
#from firebase import firebase as firebase

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random
import string

def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


cred = credentials.Certificate("bitwits-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

#firebaseApp = firebase.FirebaseApplication('https://your_storage.firebaseio.com', None)

app = Flask(__name__)
scheduler = APScheduler()

@app.route('/', methods=['GET'])
def linkScrapper():
    with app.app_context():
        d = []
        url_news = "https://www.vjti.ac.in"  # link to scrape links from
        r = requests.get(url=url_news)  # , headers=headers
        soup = BeautifulSoup(r.text, "html.parser")
        customs = soup.find_all("div", {"class": "custom"})
        for custom in customs:
            try:
                links = custom.find_all("a")
                for link in links:
                    if "https" in link.get("href"):
                        Links = link.get("href")  # adding URI to source IDs of links to get URL
                        #print(Links)
                        d.append(Links)
                    else:
                        Links = url_news + link.get("href")
                        # print(Links)
                        d.append(Links)
            except Exception:
                links = None

        d.pop(-1)  # removing last item for list which is not required
        json_dict = defaultdict(list)
        try:
            for item in d:
                title = item.split('/')[4]
                try:
                    json_dict[title].append(item)
                    #print(json_dict)
                except Exception as e:
                    print(e)

        except Exception as e:
            print(e)

        for a in json_dict:
            for link in json_dict[a]:
                print(f"{a} : {link}")

        d_ref = db.collection(u'Announcements')
        dd_ref = d_ref.stream()

        existing_links = []
        for d in dd_ref:
            existing_links.append(d.to_dict()["link"])

        print(existing_links)
        print(len(existing_links))

        for a in json_dict:
            for link in json_dict[a]:

                if link not in existing_links:
                    print("--------------------------------------------------------------------------------")
                    print("new : " + link)

                    ref = db.collection(u'Announcements').document("a" + randomString())

                    ref.set({
                        u'title' : a,
                        u'link' : link
                    })
                else:
                    print("No updates")

        return jsonify(json_dict)  # to decode JSON later in Flutter, converting obtained data to JSON

if __name__ == '__main__':
    scheduler.add_job(id='Scheduled Task', func=linkScrapper, trigger='interval', minutes=5)
    scheduler.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port)
