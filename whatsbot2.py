from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from multiprocessing import Process, Queue
import subprocess
from numpy.random import choice
from os import path
import pandas as pd
import numpy as np
import tkinter as tk

xpaths={
    'input':'//*[@id=\"main\"]/footer/div[1]/div[2]/div/div[2]',
    'attach':'//*[@id=\"main\"]/header/div[3]/div/div[2]/div/span',
    'select_photo':'//*[@id=\"main\"]/header/div[3]/div/div[2]/span/div/div/ul/li[1]/input',
    'send_photo':'//*[@id=\"app\"]/div/div/div[1]/div[2]/span/div/span/div/div/div[2]/span[2]/div/div',
    'caption':'//*[@id=\"app\"]/div/div/div[1]/div[2]/span/div/span/div/div/div[2]/div/span/div/div[2]/div/div[3]/div[1]/div[2]',
    'select_doc':'//*[@id="main"]/header/div[3]/div/div[2]/span/div/div/ul/li[3]/input',
    'audios':'/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[3]/div/span/button',
    'send_audio':'/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[3]/div/span/div/button[2]'
}
selectors={
    'conversations':'#pane-side > div:nth-child(1) > div > div > div',
    'conv_title':'div > div > div._2WP9Q > div.KgevS > div._3H4MS > span',
    'conv_unread':'div > div > div._2WP9Q > div.xD91K > div._0LqQ > span:nth-child(1) > div > span',

    'messages':'#main > div._1_q7u > div > div > div._1ays2 > div.message-in',
    'msg_time':'div > div > div > div._1RNhZ > div > span',
    'msg_text':'div > div > div > div.copyable-text > div > span._F7Vk.selectable-text.invisible-space.copyable-text > span',
    'msg_author':'div > div > div > div._1QjgA._2q8oz > span',
}

msg_params=['msg_author','msg_time','msg_text']

keys_dict={}
for key in xpaths.keys():
    keys_dict[key]='xpath'

for key in selectors.keys():
    keys_dict[key]='css'
driver=None
rules=None
stop=False

def process_str(str1):
    return str1.lower\
        .replace('á','a')\
        .replace('é','e')\
        .replace('í','i')\
        .replace('ó','o')\
        .replace('ú','u')

def equals_str(str1,str2):
    return process_str(str1)==process_str(str2)

def init_driver():
    global driver 
    if driver is None:
        with open('driver_location.txt', 'r') as f:
            driver_location=f.read()
        driver=webdriver.Chrome(driver_location)
        driver.get("https://web.whatsapp.com/")
        load_rules()
    else:
        driver.close()
        driver=None

def load_rules():
    global rules
    rules=pd.read_excel('rules.xlsx')
    rules=rules.fillna('')
    rules['specifity']=np.zeros(rules.shape[0],dtype=np.int32)
    for col in ['Conversation','Author','Time','Text']:
        rules['specifity']+=rules[col].str.len()
    rules=rules.sort_values('specifity',ascending=False)

def query(key,parent=None):
    if parent is None:
        parent=driver
    target_type=keys_dict[key]
    if target_type=='xpath':
        return parent.find_element_by_xpath(xpaths[key])
    elif target_type=='css':
        res=parent.find_elements_by_css_selector(selectors[key])
        if key[-1]!='s':
            return res[0] if len(res)>0 else None
        return res

def send_msg(inputfield,m):
    inputfield.clear()
    inputfield.send_keys([m,Keys.RETURN])

def send_attach(filepath,caption=''):
    query('attach').click()
    if filepath.endswith('mp3'):    
        query('select_doc').send_keys(filepath)
    else:
        query('select_photo').send_keys(filepath)
        if caption:
            query('caption').send_keys(caption)
    query('send_photo').click()

def send_mp3(texto,nombre='bot',idioma='spanish'):
    subprocess.call(['espeak','-w'+nombre+'.mp3','-v'+idioma,texto])
    send_attach(path.dirname(path.abspath(__file__))+'/'+nombre+'.mp3')

def check_conversations():
    conversations=query('conversations')
    all_dict={}
    new_messages_read=False
    for conv in conversations:
        n_unread_msgs=query('conv_unread',conv)
        conv_title=query('conv_title',conv).text
        if n_unread_msgs is not None and n_unread_msgs.text !='':
            new_messages_read=True
            n_unread_msgs=int(n_unread_msgs.text)
            unread_msgs=[]
            conv.click()
            msgs=query('messages')[-n_unread_msgs:]
            curr_author=conv_title
            inputfield=query('input')
            for msg in msgs:
                msg_dict={}
                for msg_param in msg_params:
                    msg_res=query(msg_param,msg)
                    if msg_res is not None:
                        msg_res=msg_res.text
                    msg_dict[msg_param]=msg_res
                if msg_dict['msg_author'] is None:
                    msg_dict['msg_author']=curr_author
                else:
                    curr_author=msg_dict['msg_author']
                unread_msgs.append(msg_dict)
            
                for _, row in rules.iterrows():
                    try:
                        if equals_str(row['Conversation'],conv_title) and equals_str(row['Author'],msg_dict['msg_author']) and equals_str(row['Time'],msg_dict['msg_time']) and equals_str(row['Text'],msg_dict['msg_text']):
                            best_answer=row['Answer']
                            print(best_answer)
                            send_msg(inputfield,best_answer)
                            break
                    except Exception as e: #some weird message came?
                        print(e)
            
            all_dict[conv_title]=unread_msgs
    if new_messages_read:
        driver.refresh()
        print(all_dict)

class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.pack()
        self.activebot=False
        self.create_widgets()
        self.periodic_call()

    def create_widgets(self):
        self.init_driver_btn=tk.Button(self,text='init whatsapp',command =self.init_driver)
        self.init_driver_btn.pack(side="top")
        self.load_rules_btn=tk.Button(self, text='load rule sheet', command =load_rules)
        self.load_rules_btn.pack(side="top")
        self.activate_bot_btn=tk.Button(self, text='activate bot', command =self.activate_bot)
        self.activate_bot_btn.pack(side="top")
        self.close_driver_btn=tk.Button(self, text='Quit', command =self.destroy)
        self.close_driver_btn.pack(side="top")

    def init_driver(self):
        init_driver()
        if driver is None:
            self.init_driver_btn["text"] = "init whatsapp"
        else:
            self.init_driver_btn["text"] = "close whatsapp"

    def periodic_call(self):
        if self.activebot:
             check_conversations()
        self.after(60000, self.periodic_call)

    def activate_bot(self):
        self.activebot=not self.activebot
        if self.activebot:
            self.activate_bot_btn["text"] = "deactivate bot"
        else:
            self.activate_bot_btn["text"] = "activate bot"

app = Application()
app.mainloop()

