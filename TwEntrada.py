import time
starttime = time.time()
while True:
  
    time.sleep(50.0 - ((time.time() - starttime) % 50.0))
    
#uso de listas aleatorias bajo probabilidades.
    lista=''
    num=switch_demo()
    print('lista empleada: '+str(num))
    with open("Listas/Lista"+str(num)+".csv", newline='') as File:  
        reader = csv.reader(File)
        i=0
        for row in reader:
          if(i!=0):
            lista=lista+' OR '+str(row[0])
          else:
            lista=str(row[0])
            i=1
    
    tweets = tw.Cursor(api.search,
                          #--removido: q=(["#Emergencia since:{}".format(desde)]) and ("place:%s" % place_id),
                          q=("(place:%s)" % place_id)+ ' AND (' +(lista)+')',
                          #country='Ec',
                          ).items(900)
    
    
    for tweet in tweets:
      status = api.get_status(tweet.id_str)
      if((tweet.id_str in ids)==False):
        print('nuevo tuit')
        if(len(tweet._json['text'])==0):
          ids.append(tweet.id_str)
          continue
        ids.append(tweet.id_str)
        print(tweet._json['text'])
        created_at = status.created_at
        t=datetime.strptime(str(created_at),"%Y-%m-%d %H:%M:%S")
        t=t.replace(tzinfo=pytz.utc)
        t=t.astimezone(pytz.timezone("Etc/GMT+5"))
        lat=None
        lon=None
        place_full_name=None
        if hasattr(tweet.coordinates, 'coordinates'):
          lat = tweet.coordinates.coordinates[0]
          lon = tweet.coordinates.coordinates[1]
        else:
          if hasattr(tweet.place, 'bounding_box'):
            lat=(tweet.place.bounding_box.coordinates[0][1][0]+tweet.place.bounding_box.coordinates[0][3][0]) /2
            lon=(tweet.place.bounding_box.coordinates[0][1][1]+tweet.place.bounding_box.coordinates[0][3][1]) /2
          else:
            #En el peor de los casos, se colocan las coordenadas en una isla fantasma.
            lat = "-81.785017"
            lon = "-1.559331"
        if hasattr(tweet.place, 'full_name'):
          place_full_name = tweet.place.full_name
        else:
          place_full_name = None
        row=[tweet._json['user']['id'], tweet._json['id'], t, tweet._json['user']['screen_name'], tweet._json['text'],str('https://twitter.com/'+tweet._json['user']['screen_name']+'/status/'+tweet.id_str),lon,lat,place_full_name,'NO']    
        with open('data_streaming.csv', 'a') as f:
          writer = csv.writer(f, delimiter='|')
          writer.writerow(row)
    
    
