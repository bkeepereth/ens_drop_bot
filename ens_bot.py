#!/usr/bin/env python
import getopt
import logging
import requests
import os
import sys
import json
from pymongo import MongoClient
import datetime
import calendar
import discord
import time
import asyncio
import xml.etree.ElementTree as ET

ens_bot=discord.Client()
log=logging.getLogger()

def get_config(file_name):
    log.info(str(datetime.datetime.now())+"|get_config|starting")
    if (file_name=="" or file_name==None):
        raise Exception(str(datetime.datetime.now())+"|get_config|file_name is invalid|file_name="+str(file_name))

    result=dict()
    root=ET.parse(file_name).getroot()
    for prop in root.findall('property'):
        result[prop.find('name').text]=prop.find('value').text    

    log.info(str(datetime.datetime.now())+"|get_config|starting") 
    return result

def connect_to_endpoint(url, params, bearer_token):
    log.info(str(datetime.datetime.now())+"|connect_to_endpoint|starting")

    headers={"Authorization":f"Bearer {bearer_token}","User-Agent":"v2RecentSearchPython"}    
    response=requests.get(url, headers=headers, params=params)
    if (response.status_code!=200):
        raise Exception(response.status_code, response.text)

    log.info(str(datetime.datetime.now())+"|connect_to_endpoint|completed")
    return response.json()

# prepares and sends discord embed
def prep_msg(t_id, uname, username, created_at, delta, text): 
    #log.info(str(datetime.datetime.now())+"|prep_msg|starting")

    embed=discord.Embed(title="🚨 ENS DROP ALERT 🚨")
    embed.add_field(name="Link",value="https://twitter.com/i/web/status/"+str(t_id),inline=False)
    embed.add_field(name="User",value=uname+" / @"+username,inline=True)
    embed.add_field(name="Tweet Time",value=created_at,inline=False)
    embed.add_field(name="Time Elapsed",value=delta,inline=False)
    embed.add_field(name="Tweet",value=text,inline=False)

    #log.info(str(datetime.datetime.now())+"|prep_msg|completed") 
    return embed

async def ens_task(config):
    log.info(str(datetime.datetime.now())+"|ens_task|starting")

    uri=("mongodb://"+
         config.get("m_user")+":"+
         str(config.get("m_pwd"))+"@"+
         str(config.get("m_host"))+":"+
         str(config.get("m_port"))+"/"+
         str(config.get("db_name")))

    search_url="https://api.twitter.com/2/tweets/search/recent"
    query_params={'query':'drop your ens','tweet.fields':'author_id,created_at','expansions':'author_id','max_results':'99'}

    await ens_bot.wait_until_ready()
    channel=ens_bot.get_channel(id=int(config.get("CHANNEL_ID")))

    while not ens_bot.is_closed():  
        while True:
            client=MongoClient()
            db=client["ens_drop_daily"]
            col=db["tweet_24hr"]

            json_response=connect_to_endpoint(search_url, query_params, config.get("BEARER_TOKEN"))

            tweets=json_response.get("data")
            users=json_response.get("includes").get("users")

            counter=0
            for i in range(0,len(tweets)-1):
                try:
                    t_id=""
                    text=""
                    created_at=""
                    uname=""
                    username=""

                    t_id=tweets[i].get("id")
                    text=tweets[i].get("text")
                    created_at=tweets[i].get("created_at")
                    uname=users[i].get("name")
                    username=users[i].get("username")

                    # if any of the above values are null, discard 
                    # in my testing, len(data) and len(users) were inconsistent
                    if (str(t_id)=="" or str(t_id)==None):
                        raise Exception("t_id is invalid")
                    if (str(t_id)=="" or str(t_id)==None):
                        raise Exception("t_id is invalid")
                    if (str(text)=="" or str(text)==None):
                        raise Exception("text is invalid")
                    if (str(created_at)=="" or str(created_at)==None):
                        raise Exception("created_at is invalid")
                    if (str(uname)=="" or str(uname)==None):
                        raise Exception("uname is invalid")
                    if (str(username)=="" or str(username)==None):
                        raise Exception("username is invalid")

                    created_dt=created_at[:len(created_at)-5]
                    created_dt=datetime.datetime.strptime(created_dt,"%Y-%m-%dT%H:%M:%S")
                    created_dt=calendar.timegm(created_dt.utctimetuple())
                    elapsed_dt=(datetime.datetime.now()).timestamp()-created_dt
                    delta=str(datetime.timedelta(seconds=elapsed_dt))

                    search={"tweet_id":t_id}
                    docs=col.find(search)
                    doc_list=list(docs)

                    if (len(doc_list)==0):
                        doc={
                            "tweet_id":t_id,
                            "uname":uname,
                            "username":username,
                            "created_at":created_at,
                            "text":text
                        }
                        x=col.insert_one(doc)
                        #counter=counter+1

                        embed=prep_msg(t_id,uname,username,created_at,delta,text)

                        await channel.send(embed=embed)
                        await asyncio.sleep(5)
                except Exception as e:
                    log.error(e)
            
            log.info(str(datetime.datetime.now())+"|ens_task|sleeping for 180 secs....zZzZ")

            client.close()
            await asyncio.sleep(180)

def Usage():
    print("Usage:./ens_bot.py -c [config]")

@ens_bot.event
async def on_ready():
    print("Booting...")

def main(argv):
    logging.basicConfig(filename=str(datetime.datetime.now())+".ens_bot.log",filemode="w")
    log.setLevel(logging.INFO)
    log.info(str(datetime.datetime.now())+"|main|starting")

    try:
        (opts,args)=getopt.getopt(argv, "hc:", ["help"])
        file_name=""
  
        for (opt,arg) in opts:
            if (opt in ("-h","--help")):
                Usage()
                sys.exit()
            elif (opt in ("-c")):
                file_name=str(arg)
            else:
                Usage()
                sys.exit()        

        config=get_config(file_name)
        ens_bot.loop.create_task(ens_task(config))
        ens_bot.run(config.get("DS_TOKEN"))
    except Exception as e:
        log.error(e)

    log.info(str(datetime.datetime.now())+"|INFO|main|completed")

if __name__=="__main__":
    main(sys.argv[1:])

