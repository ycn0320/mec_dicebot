#-*- coding: utf-8 -*-

import StringIO
import json
import logging
import random
import urllib
import urllib2
import re

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = '192794280:AAFtJK70ZC2mPRH8uqwpx1-U2OwnQ8Bbzp4'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(required=True, indexed=True, default=False,)


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

  
def reply(chat_id, text, reply_to=None):
  params = {
        'chat_id': str(chat_id),
        'text': text.encode('utf-8'),
        }
  
  if reply_to:
    params['reply_to_message_id'] = reply_to
      
  try:
    urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode(params)).read()
  except Exception as e:
    logging.exception(e)


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

        message = body['message']
        message_id = message.get('message_id')
        text = message.get('text')
        chat = message['chat']
        chat_id = chat['id']
        try:          
          username = message['from']['last_name'] + message['from']['first_name']
        except Exception as e:
          username = message['from']['first_name']

        if not text:
            return
        
        if text == '/start':
          reply(chat_id, u'굴려 굴려 주사위!')
          setEnabled(chat_id, True)
          return
        if (not getEnabled(chat_id)):
          return
        if text == '/stop':
          reply(chat_id, u'보고 또 보고, 매일 또 보기 약속!')
          setEnabled(chat_id, False)
          return
        #if getEnabled(chat_id):
        if text.startswith('!'):
          cmd_dice = re.match('^' + '!dice' + ' (.*)', text)
          try:
            inputVal = int(cmd_dice.group(1))
            if cmd_dice:
              rand = random.randint(1, abs(inputVal))
              reply(chat_id, u'우리 [%s] 친구는 [%s] 이 나왔어요!' % (username, rand), message_id)
          except Exception as e:
            reply(chat_id, u'숫자만 입력해줘잉')

          return

        	

app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)