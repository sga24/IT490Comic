#!/usr/bin/python3
import requests
import pika
import json
import random
import datetime
from datetime import timedelta
RABBIT_HOST = '127.0.0.1'
RABBIT_PORT = 5672
RABBIT_Q = '*'
RABBIT_USER = 'test'
RABBIT_PASS = 'test'
RABBIT_VH = 'testHost'
RABBIT_EX = 'superExchange'

apiKey = '?api_key=afbe58eef9e2d34188a29ebf707d671bde76e1a1&format=json'
fields= '&field_list=id,powers,image'
url = 'https://comicvine.gamespot.com/api/publisher/4010-31/' + apiKey
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
#result = requests.get(url, headers=headers)
#print(result.status_code)
#print(result.text)
def getCharData():
    with open("DCJSON.json", "r") as read_file:
        data = json.load(read_file)
    with open("MarvelJSON.json","r") as read_file:
        mData= json.load(read_file)

    print("Here are 5 DC characters")
    for x in range(5):
        offset= random.randint(1,10000)
        dcCharacterName = data["results"]["characters"][offset]["name"]
        dcCharacterURL = data["results"]["characters"][offset]["api_detail_url"]
        fullCharDetailURL = dcCharacterURL + apiKey+ fields
        print(dcCharacterName)
        print(dcCharacterURL)
        print (fullCharDetailURL)
        sendCharData(fullCharDetailURL,dcCharacterName, "DC Comics")

    print("Here are 5 Marvel characters")
    for x in range(5):
        offset= random.randint(1,18000)
        marvelCharacterName=mData["results"]["characters"][offset]["name"]
        marvelCharacterURL= mData["results"]["characters"][offset]["api_detail_url"]
        fullCharDetailURL = marvelCharacterURL + apiKey+ fields
        print (marvelCharacterName)
        print (marvelCharacterURL)
        print (fullCharDetailURL)
        sendCharData(fullCharDetailURL, marvelCharacterName, "Marvel")

def sendCharData(fullCharDetailURL, name, publisher):
    date = datetime.date.today() - timedelta(1)
    date = date.isoformat().replace("-"," ")
    try:
        result = requests.get(fullCharDetailURL, headers=headers)
        resultJSON = json.loads(result.text)
        charID = resultJSON["results"]["id"]
        print(charID)
        print(resultJSON["results"]["image"]["super_url"])
        imgURL = resultJSON["results"]["image"]["super_url"]
        powers = []
        for power in resultJSON["results"]["powers"]:
            print(power["name"])
            powerID = power["id"]
            powers.append(powerID)
        print(powers)
        #error catch? 
        sendRequest(RABBIT_HOST, RABBIT_Q,RABBIT_USER, RABBIT_PASS, RABBIT_VH, RABBIT_EX, RABBIT_PORT, date, charID, name, imgURL, powers,publisher)
    except requests.exceptions.RequestException:
        print('REQUEST FAILED, TOO MANY KNOCKS?')


def sendRequest(rabbitServer, rabbitQ, rabbitUser, rabbitPass, rabbitVHost, rabbitEx, rabbitPort, date, charID, name ,imgURL, powers, publisher):
    rabbitMSG = json.dumps( {'date': date,
                             'charID': charID,
                             'name': name,
                             'image': imgURL,
                             'powers': powers,
                             'publisher': publisher
                             })      
    creds = pika.PlainCredentials(rabbitUser, rabbitPass)
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitServer, rabbitPort, rabbitVHost, creds))
    channel = connection.channel()
    channel.basic_publish(exchange=rabbitEx, routing_key=rabbitQ, body=rabbitMSG)
    
getCharData()
print ("Who Would Win?")
