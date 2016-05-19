#-*- coding: utf-8 -*-

import StringIO
import json
import logging
import random
import urllib
import urllib2
import re

#from operator import itemgetter

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = '192794280:AAFtJK70ZC2mPRH8uqwpx1-U2OwnQ8Bbzp4'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


#dicDiceResult = { '' : '' }

# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False

  
def reply(chat_id, text):
  params = {
        'chat_id': str(chat_id),
        'text': text.encode('utf-8'),
        }
  urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode(params)).read()


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']
      # username = fr['username']
        
      #  global dicDiceResult
        
        if not text:
            return
        
        if text.startswith('/'):
          if text == '/start':
            reply(chat_id, u'굴려 굴려 주사위!')
            setEnabled(chat_id, True)
            return
          if text == '/stop':
            reply(chat_id, u'보고 또 보고, 매일 또 보기 약속!')
            setEnabled(chat_id, False)
            return
          if getEnabled(chat_id):
            cmd_dice = re.match('^' + '/dice' + ' (.*)', text)
            if cmd_dice and bool(abs(int(cmd_dice.group(1)))):
              rand = random.randint(1, abs(int(cmd_dice.group(1))))
              reply(chat_id, u'우리 친구는 [%s] 이 나왔어요!' % rand)
              return


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)