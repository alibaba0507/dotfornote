import re
#from words_db import loadWords
from words_db import Words
import logging
from google.appengine.api import memcache

# this function will remove the while tag and everything
# between <tag></tag>
def replaceHTMLTag( text, startTag, endTag, replaceWith, skipIfFound = '' ):
  indx = text.find(startTag)
  while (indx > -1):
    end_indx = text.find(endTag,indx + 1)
    if end_indx == -1:
      break
    txt = text[indx:end_indx + len(endTag)] # maybe need +1 for end_indx maybe is 1 based not 0 based
    if skipIfFound == '' or (skipIfFound != '' and txt.index(skipIfFound,0) < 0):
      text = text.replace(txt,replaceWith)
      indx = 0
    else : 
     indx += 1
    indx = text.find(startTag,indx);
  
  return text


# Strip the text out of the html tags between '>' and '<'
# @return array of 0 - end_indx of '<', 1 - extracted text
def stripHtmlText(text,indx = 0):
  ret = []
  txt = ''
  start_indx = text.find('>',indx)
  if start_indx == -1: return None
  end_indx = text.find('<',start_indx + 1)
  if end_indx == -1:
   txt = text[start_indx + 1:len(text)] # the rest of the text
  else:
    txt = text[start_indx + 1:end_indx]
  if len(txt.strip()) == 0 and end_indx > -1: # we found text
    return stripHtmlText(text,end_indx + 1)
  #else:
  #  return 'we r here'
  start_len = len(txt)
  txt = txt.replace(',',' , ').replace('.',' . ').replace('-',' - ')
  txt = txt.replace('\'',' \' ').replace('"',' " ').replace('+',' + ')
  txt = txt.replace('-',' - ').replace('=',' = ').replace('!',' ! ')
  tx = txt.replace('@', ' @ ').replace('#',' # ').replace('$',' $ ')
  txt = txt.replace('%',' % ').replace('^',' ^ ').replace('&',' & ')
  txt = txt.replace('*',' * ').replace('(',' ( ').replace(')',' ) ')
  txt = txt.replace('{',' { ').replace('}',' } ').replace('[',' ] ')
  txt = txt.replace(':',' : ').replace(';',' ; ').replace('?',' ? ')
  txt = txt.replace('\r',' ').replace('\n',' ')  
  end_len = len(txt)
  len_diff = end_len - start_len
  ret.append(end_indx)
  ret.append( txt)
  ret.append(len_diff)
  #logging.debug('Html strip [' + txt  +']')
  return ret
  #else: return None
  

def parseText(text):
  i_start = 0
  while (i_start > -1):
    i_end = i_end = text.find(' ',i_start + 1)
    s = ''
    if i_end < 0: # no space
      s = text[i_start:]
    else:
      s = text[i_start:i_end]
    
    i_start = i_end
    #logging.debug('parseText [' + s + ']')
 
# search for negative positive words modified text
# and create analythics
def analyzeText(text):
  L = {} # empty list
  txt = ''
  ret  =[]
  ret = stripHtmlText(text)
  if ret is None: return text
  end_indx = ret[0] #text.find('>')
  txt =  ret[1]
  len_diff = int(ret[2])
  parseText(txt)
  #loadWords() # load words db (positive and negative)
  b_mod = 0
  pos_wrd = memcache.Client().get("1") # positive words
  neg_wrd = memcache.Client().get("0") # neg words
  
  pos_cnt = 0
  neg_cnt = 0
  words_before = []
  #logging.debug("Pos words [" + ". [".join(map(str, pos_wrd)) + "]")
  while (end_indx > -1): # extracting all vizible text between tags
    #end_indx = text.find('<',start_indx + 1)
    #extract all text between tags
    #end_indx = ret[0]
    #mod_txt = ret[1]
    i_start = 0
    b_mod = 0
    mod_txt = txt
    i_end = mod_txt.find(' ')
    start_indx = end_indx - (len(txt) - len_diff)
    while (i_start > -1):
      if i_end == -1: # end of parsing
        s = mod_txt[i_start]
        i_end = len(mod_txt)
      else:
        s =  mod_txt[i_start:i_end]
        
      # loop till we have more then 3 last saved words  
      while len(words_before) > 3:
        words_before.pop(0) 
      
      
      #return txt  
      # Words counting 
      if len(L) == 0:
        L[s.lower()] = 1
      else:
        i = L.get(s.lower())
        if i is None:
          L[s.lower()] = 1 # initilize
        else:
          L[s.lower()] += 1 # increase counter with 1
      
      if len(s.strip()) == 0:
        #logging.debug(' //********* [' + s + '] [' + str(i_start) + '][' + str(len(mod_txt)) + ']*********')
        if (i_end + 1) >= len(mod_txt) : 
          i_start = -1
        else: 
          i_start = i_end  + 1
          i_end = mod_txt.find(' ',i_start)
          #logging.debug(' i_start len [' +str( i_start)  + ']')
        continue
        
      #logging.debug('  /-*************** [' + s + '] *********')
      #check for end of line
      s = s.replace('\n','') 
      s = s.replace('\r','')
     
      #w_rec = Words(word=s.lower()) # check 
      
      
      if pos_wrd.has_key(s.lower()) : # positive
        # check for negative sign before positive words
        if len(words_before) > 0:
         if words_before[-1].lower() != 'not' and words_before[-1].lower() != 'don\'t' and words_before[-1] != 'doesn\'t' and words_before[-1] != 'can\'t':
          pos_cnt += 1
        else:
         pos_cnt += 1 # we found positive
        #logging.debug(' Line is [' + mod_txt + ']' )   
        #logging.debug(' Pos start [' + mod_txt[:i_end - len(s)] + '] End [' + mod_txt[i_end:] + ']')
        mod_txt = mod_txt[:i_end - len(s)] + '<span style="color:Green;">' + s  + '</span>'  + mod_txt[i_end:]
        i_end += len('<span style="color:Green;"></span>')
        end_indx += len('<span style="color:Green;"></span>')
        b_mod = 1 # mark if the text has been modified 
      if neg_wrd.has_key(s.lower()) : # negative
        neg_cnt += 1 # we found negative one
        mod_txt = mod_txt[:i_end - len(s)] + '<span style="color:Red;">' + s  + '</span>'  + mod_txt[i_end:]
        i_end += len('<span style="color:Red;"></span>')
        end_indx += len('<span style="color:Red;"></span>')
        b_mod = 1 # mark if the text has been modified
      if (i_end + 1) >= len(mod_txt) : 
        i_start = -1
      else: 
        i_start = i_end  + 1
        i_end = mod_txt.find(' ',i_start)
        
      words_before.append(s) # add words to list
    if b_mod > 0: # text has been modified
      #logging.debug('Old text [' + txt + '] new text[' + mod_txt + ']')
      text = text[:start_indx] + mod_txt + text[start_indx + (len(txt) - len_diff):]
      #text = text.replace(txt,mod_txt,1)
    txt = '' # clear temp text buffer
    ret = stripHtmlText(text,end_indx + 1)
    end_indx = ret[0]
    txt = ret[1]
    len_diff = int(ret[2])
    #parseText(txt)
    #start_indx = text.find('>',end_indx) # position for new search
    #logging.debug(' new text [' + txt  + ']')
    #logging.debug("[" + ". [".join(map(str, L)) + "]")
  ret_wrd = countMostUsedWords(text,L)
  #logging.debug('/*********************************************/[' + str(ret_wrd[0]) + '][' + str(ret_wrd[1]) + ']')
  ret = []
  ret.append(ret_wrd[0]) # most used words
  #ret.append('Nothing')
  ret.append( pos_cnt) # pos words
  ret.append(neg_cnt) # neg words
  #ret.append(text)
  ret.append(ret_wrd[1])
  return ret
  
  
def countMostUsedWords(text,L):
  #logging.debug('/*********************************************/' + text)
  words = {} # contains 3 most used words
  i = 1
  last_cnt = 0
  for v,k in sorted(L.items(),reverse=False):# sort items witch is number DESC order
    if i > 3: # we need to collect only the tree most used words
      break
    if len(v) > 3: # Add words bigger then 3 characters only
      words[v] = i # rate the most used = 1 to least used = 3
      if last_cnt != k:
        i += 1
        last_cnt = k
      #logging.debug('List [' + str(v) + '][' + str(k) + ']')
  
  cnt = 0
  ret = []
  txt = ''
  ret = stripHtmlText(text)
  if ret is None: return text
  end_indx = ret[0]
  txt = ret[1]
  len_diff = ret[2]
  
  pos_wrd = memcache.Client().get("1") # positive words
  neg_wrd = memcache.Client().get("0") # neg words
  while (end_indx > -1): # extracting all vizible text between tags
    i_start = 0;
    mod_txt = txt
    i_end = mod_txt.find(' ',i_start)
    b_mod = 0
    start_indx = end_indx - (len(txt) - len_diff)
    while (i_start > -1):
      if i_end == -1: # end of parsing
        s = mod_txt[i_start:]
        i_end = len(mod_txt)
      else:
        s =  mod_txt[i_start:i_end]
      if len(s) == 0: #empty
        if (i_end + 1) >= len(mod_txt): i_start = -1
        else: i_start = i_end  + 1
        i_end = mod_txt.find(' ',i_start)
        continue
      
      if words.has_key(s.lower()) :
        #logging.debug(' found word  = [' + s.lower() + ']')
        if words[s.lower()] == 1: # most used word
          cnt += 1
          #w_rec = Words(word=s.lower()) # check 
          if pos_wrd.has_key(s.lower()) or neg_wrd.has_key(s.lower()): #w_rec is not None:
            mod_txt = mod_txt[:i_end - len(s)] + '<span style="font-size:25px;">' + s  + '</span>'  + mod_txt[i_end:]
            i_end += len('<span style="font-size:25px;"></span>')
            end_indx += len('<span style="font-size:25px;"></span>')
          else:
            mod_txt = mod_txt[:i_end - len(s)] + '<span style="font-size:25px; color:Gray;">' + s  + '</span>'  + mod_txt[i_end:]
            i_end += len('<span style="font-size:25px; color:Gray;"></span>')
            end_indx += len('<span style="font-size:25px; color:Gray;"></span>')
          b_mod = 1
        elif words[s.lower()] == 2: # most used word
          cnt += 1
          #w_rec = Words(word=s.lower()) # check 
          if pos_wrd.has_key(s.lower()) or neg_wrd.has_key(s.lower()): #if w_rec is not None:
            mod_txt = mod_txt[:i_end - len(s)] + '<span style="font-size:20px;">' + s  + '</span>'  + mod_txt[i_end:]
            i_end += len('<span style="font-size:20px;"></span>')
            end_indx += len('<span style="font-size:20px;"></span>')
          else:
            mod_txt = mod_txt[:i_end - len(s)] + '<span style="font-size:20px; color:Gray;">' + s  + '</span>'  + mod_txt[i_end:]
            i_end += len('<span style="font-size:20px; color:Gray;"></span>')
            end_indx += len('<span style="font-size:20px; color:Gray;"></span>')
          b_mod = 1
        elif words[s.lower()] == 3: # most used word
          cnt += 1
          #w_rec = Words(word=s.lower()) # check
          if pos_wrd.has_key(s.lower()) or neg_wrd.has_key(s.lower()): #if w_rec is not None:
            mod_txt = mod_txt[:i_end - len(s)] + '<span style="font-size:18px;">' + s  + '</span>'  + mod_txt[i_end:]
            i_end += len('<span style="font-size:18px;"></span>')
            end_indx += len('<span style="font-size:18px;"></span>')
          else:
            mod_txt = mod_txt[:i_end - len(s)] + '<span style="font-size:18px; color:Gray;">' + s  + '</span>'  + mod_txt[i_end:]
            i_end += len('<span style="font-size:18px; color:Gray;"></span>')
            end_indx += len('<span style="font-size:18px; color:Gray;"></span>')
          b_mod = 1
      if (i_end + 1) >= len(mod_txt): i_start = -1
      else: i_start = i_end  + 1
      i_end = mod_txt.find(' ',i_start)
    if b_mod > 0: # text has been modified
      #text = text.replace(txt,mod_txt,1)
      text = text[:start_indx] + mod_txt + text[start_indx + (len(txt) - len_diff):]
      #logging.debug(' Original [' + txt + ']')
      #logging.debug(' Modified [' + mod_txt + ']')
      #logging.debug(' Whole Text [' + str(text.find(mod_txt)) + ']')
      #logging.debug(' Whole Text [' + str(text.find(txt)) + ']')
    txt = '' # clear temp text buffer
    ret_app = stripHtmlText(text,end_indx + 1)
    end_indx = ret_app[0]
    txt = ret_app[1]
    len_diff = ret_app[2]
  ret = []
  ret.append( cnt)
  ret.append(text)
  
  return ret
  