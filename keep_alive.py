from flask import Flask, render_template
from threading import Thread
import random
import time
import requests
import logging
from datetime import datetime
import pytz

app = Flask('')
@app.route('/')

def home():
    return '<h1>Discord Bot is Online!</h1>'

def run():
  app.run(host='0.0.0.0',port=8888) 

def ping(target, debug):
    while(True):
        r = requests.get(target)
        if(debug == True):
            aware_us_central = datetime.now(pytz.timezone('Asia/Jakarta'))
            print(f"--- {aware_us_central.strftime('%Y-%m-%d %H:%M:%S %Z')} == Status Code : {str(r.status_code)} ---")
        time.sleep(random.randint(280,300)) #alternate ping time between 3 and 5 minutes

def awake(target, debug=False):  
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.logger.disabled = True  
    t = Thread(target=run)
    r = Thread(target=ping, args=(target,debug))
    t.start()
    r.start()