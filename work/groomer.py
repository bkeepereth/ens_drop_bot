# groom mongodb
tmp_tweets=col.find()
log.info(str(datetime.datetime.now())+"|ens_task|groomer starting")

for tweet in tmp_tweets:
    ts=tweet['created_at']
    ts=ts[:len(ts)-5]
    ts=datetime.datetime.strptime(ts,"%Y-%m-%dT%H:%M:%S")
    ts=calendar.timegm(ts.utctimetuple())

    log.info("HERE7")

    ct=datetime.datetime.now()
    if ((ct.timestamp()-(86400*2)) > ts):
        remove_query={"tweet_id":t_id}
        y=col.delete(remove_query)
log.info(str(datetime.datetime.now())+"|ens_task|groomer completed")


