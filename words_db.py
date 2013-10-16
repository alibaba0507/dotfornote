import urllib
import json
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api import memcache
import logging

# Where to store all selected words 
# based on there type 1 positive 0 negative
#
class Words(db.Model):
    type = db.IntegerProperty(required=False)
    word = db.StringProperty(required=True)



def deleteWords():
  results = db.GqlQuery("SELECT * FROM Words")
  results.fetch(None)
  for a in results:
    logging.debug('[' + a.word + '][' + str(a.type) + ']')
    a.delete()
    
# Check for memecashe if can not find
# will try to load from Db if not there
# will requesed from url load in db and load into 
# memcache
def loadWords():
 # memcache.add(key="weather_USA_98105", value="raining", time=3600)
  
  #key_cnt = Words.all(keys_only=True).count()

  url = 'https://script.google.com/macros/s/AKfycbxMrN4dIegTkVc7f_zwOeTv-mWFEWlsJJYNEuevshPbLhjzmAk/exec'
  urlfetch.set_default_fetch_deadline(45)
  #wrd = Words(type=1)
  pos_wrd = memcache.get('1') # positive words
  if pos_wrd is not None and len(pos_wrd) > 0:
   logging.debug(' Check For Pos Words is None [' + str(len(pos_wrd)) + ']')
  if pos_wrd is None or len(pos_wrd) == 0:
    logging.debug(' Pos Words is None')
    results = db.GqlQuery("SELECT * FROM Words where type = 1")
    ret_obj = results.fetch(None)
    pos_wrd = {}
    max_len = memcache.get('max_1') # keep all records cnt in db
    if max_len is None or len(max_len) == 0:
      max_len = 0
    else: 
      max_len = int(max_len)
    if len(ret_obj) == 0 or max_len > len(ret_obj): # no records
      result = urlfetch.fetch(url + '?json=1&t=1') # positive words library
      logging.debug(' No Pos Words from DB')
      if result.status_code == 200:
        content = result.content
        resultJSON = json.loads(content)
        logging.debug(' Loaded from URL')
        memcache.set('max_1',str(len(resultJSON)))
        i = 0
        for e in resultJSON:
          if i >= max_len:
            w = Words(type=1, word=urllib.unquote(e.lower()).decode("utf-8"))
            w.put() #add record to db
            pos_wrd[urllib.unquote(e.lower()).decode("utf-8")] = 1
          memcache.put('max_1',str(i),time=3600)
          i += 1
    else:
      for e in ret_obj:
        pos_wrd[e.word] = e.type
        logging.debug(' Loaded from DB [' + e.word + ']')
    memcache.add("1", pos_wrd, time=3600) # loaded for hour
    
  neg_wrd = memcache.get('0') # positive words
  if neg_wrd is None or len(neg_wrd) == 0:
    results = db.GqlQuery("SELECT * FROM Words where type = 0")
    ret_obj = results.fetch(None)
    neg_wrd = {}
    max_len = memcache.get('max_0') # keep all records cnt in db
    if max_len is None or len(max_len) == 0:
      max_len = 0
    else: 
      max_len = int(max_len)
      
    if len(ret_obj) == 0 or max_len > len(ret_obj):
      result = urlfetch.fetch(url + '?json=1&t=0') # negative words library
      if result.status_code == 200:
        content = result.content
        resultJSON = json.loads(content)
        i =0 
        for e in resultJSON:
          if i >= max_len:
            w = Words(type=0,word=urllib.unquote(e.lower()).decode("utf-8"))
            w.put() #add record to db
            neg_wrd[urllib.unquote(e.lower()).decode("utf-8")] = 0
          memcache.add('max_0',str(i),time=3600)
          i += 1
    else:
      for e in ret_obj:
        neg_wrd[e.word] = e.type
    
    memcache.add("0", neg_wrd, time=3600) # loaded for hour
    
  logging.debug("[" + ". [".join(map(str, pos_wrd)) + "]")
  logging.debug("[" + ". [".join(map(str, neg_wrd)) + "]")
  
  