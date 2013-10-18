import webapp2
import os
import utils
import dictionary
import dictionary
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
from google.appengine.api import memcache
import pagerank
from rank_provider import AlexaTrafficRank
from rank_provider import GooglePageRank


  
class MainHandler(webapp2.RequestHandler):
  def get(self):
    if self.request.get('pr'): # google page rank
     url = self.request.get('pr') #"http://www.archlinux.org"
     providers = (AlexaTrafficRank() , GooglePageRank(),)

     self.response.write("Traffic stats for: %s" % (url))
     for p in providers:
       self.response.write( '<br/> Class is ' + str(p.__class__.__name__) + ' - Rank is ' + str(p.get_rank(url)) + '<br />')


    elif self.request.get('url'):
      url_hist = self.request.get('url')#"http://www.tutorialspoint.com/python/python_lists.htm"
      load_header = self.request.get('h')
      scan = self.request.get('s')
      words_only = self.request.get('wrds')
      urlfetch.set_default_fetch_deadline(45)
      result = urlfetch.fetch(url_hist)
      if result.status_code == 200:
        content = result.content
        i_head = content.find('</head>')
        if i_head > -1:
          header = content[:i_head + len('</head>')]
          header = utils.replaceHTMLTag( header, '<script','</script>','')
        content = utils.replaceHTMLTag( content, '<head','</head>','')
        content = utils.replaceHTMLTag( content, '<script','</script>','')
        ret = []
        #words_db.deleteWords()
        if len(scan) > 0:
          if header is not None and len(load_header) > 0:
           self.response.write(header + content)
          else:
           self.response.write(content)
        else:
          cont = dictionary.loadCache()
          ret = utils.analyzeText( content)
          if header is not None and len(load_header) > 0:
            self.response.write(header + ret[3])
          elif words_only == '1':
            response = {}
            response['used'] = ret[0]
            response['positive'] = ret[1]
            response['negative'] = ret[2]
            #write json string to output
            self.response.write(json.dumps(response))
            #self.response.write('<p> Most used words :[' + str(ret[0]) + ']<br/>')
            #self.response.write('<p> Positive words :[' + str(ret[1]) + ']<br/>')
            #self.response.write('<p> Negative words :[' + str(ret[2]) + ']<br/>')
          else:
            self.response.write(ret[3])
        #self.response.write(ret[3])

app = webapp2.WSGIApplication([
  ('/.*', MainHandler),
], debug=True)