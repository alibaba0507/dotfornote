import logging
import urllib
import json
from google.appengine.api import urlfetch
from google.appengine.api import memcache
import codecs

# will check if the words are loaded into
# the cache if not will be loaded
def loadCache():
  url = 'https://script.google.com/macros/s/AKfycbxMrN4dIegTkVc7f_zwOeTv-mWFEWlsJJYNEuevshPbLhjzmAk/exec'
  urlfetch.set_default_fetch_deadline(45)
  pos_wrd = memcache.Client().get("1") # positive words
  #pos_cnt = memcache.Client().get("cnt_1") # how manny records

  neg_wrd = memcache.Client().get("0") # neg words
  #neg_cnt = memcache.Client().get("cnt_0") # how manny records
  
  if pos_wrd is None or len(pos_wrd) < 1:
    result = urlfetch.fetch(url + '?json=1&t=1') # positive words library
    if pos_wrd is not None:
      logging.debug(' No Pos Words from DB [' + str(len(pos_wrd)) + '][' + str(result.status_code) + ']')
    if result.status_code == 200:
      content = result.content
      resultJSON = json.loads(content)
      #memcache.add(key="cnt_1", value=str(len(resultJSON)), time=3600)
      #logging.debug(' Pos words from url [' + str(len(resultJSON))  + '][')
      p_word = {}
      #i = len(pos_wrd)
      #j = 0
      #pos_cnt = len(resultJSON)
      #logging.debug(' Before Loop save ' + ". [".join(map(str, p_word)))
      for e in resultJSON:
        #if i < pos_cnt and j >= i:
          #content = unicode(e.lower().strip(codecs.BOM_UTF8), 'utf-8')          
        try:
            #content = unicode(e.lower().strip(codecs.BOM_UTF8), 'utf-8')
            #logging.debug(' Pos Word is [' + str(e.lower()) + ']')
          p_word[str(e.lower())] = 1
          #logging.debug(' Pos Word is [' + str(e.lower()) + ']')
        except:
          logging.debug(' Error Pos Word is [' + e.lower() + ']')
          pass
            
        #i += 1
        #j += 1
      logging.debug(' Before save [' + str(len(p_word)) + ']')
      memcache.add(key="1", value=p_word, time=3600)
  
  if neg_wrd is None or len(neg_wrd) < 1:
    result = urlfetch.fetch(url + '?json=1&t=0') # positive words library
    if neg_wrd is not None:
      logging.debug(' No Neg Words from DB [' + str(len(neg_wrd))  + ']')
    if result.status_code == 200:
      content = result.content
      m_resultJSON = json.loads(content)
      #logging.debug(' Neg words from url [' + str(len(m_resultJSON))  + ']')
      n_word = {}
      for e in m_resultJSON:
        try:
            #logging.debug(' Neg Word is [' + str(e.lower()) + ']')
            #content = unicode(e.lower().strip(codecs.BOM_UTF8), 'utf-8')
          n_word[str(e.lower())] = 0
        except:
          pass
        
      logging.debug(' Before save Neg Words  [' + str(len(n_word)) + ']')
      memcache.add(key="0", value=n_word, time=3600)
