def consulta(xpath):
    while True:
        try:
            element=driver.find_element_by_xpath(xpath)
            return element
        except:
            time.sleep(0.25)
def send_msg(m):
    inputfield.clear()
    inputfield.send_keys([m,Keys.RETURN])
def recv_msgs(last_id):
    msgs=driver.find_elements_by_class_name('Tkt2p')
    new_msgs=[]
    if len(msgs)>0:
        new_last_id=msgs[-1].id
        for msg in reversed(msgs):
            if msg.id == last_id:
                break
            new_msgs.append(msg)
        return reversed(new_msgs), new_last_id
    return [],last_id
def send_attach(filepath,caption=''):
    consulta(xpaths['attach']).click()
    if filepath.endswith('mp3'):
        consulta(xpaths['select_doc']).send_keys(filepath)
    else:
        consulta(xpaths['select_photo']).send_keys(filepath)
        if caption:
            consulta(xpaths['caption']).send_keys(caption)
    consulta(xpaths['send_photo']).click()
def send_mp3(texto,nombre='bot',idioma='spanish'):
    subprocess.call(['espeak','-w'+nombre+'.mp3','-v'+idioma,texto])
    send_attach(path.dirname(path.abspath(__file__))+'/'+nombre+'.mp3')
def infiniteloop(q):
    try:
        f=open('last_id.txt','r')
        last_id=f.read()
        f.close()
    except:
        last_id=''
        print('Error reading last_id')
        
    print('Start. Last message read: ',last_id)
    while q.empty():
        try:
            msgs,last_id=recv_msgs(last_id)
            for msg in msgs:
                print('['+msg.text+']')
                splitmsg=msg.text.split('\n')
                if splitmsg[0]=='Echo' or (splitmsg[1]=='Echo' and len(splitmsg)>3):
                    send_msg(splitmsg[-2])
                    send_mp3(splitmsg[-2])
            msgs,last_id=recv_msgs(last_id)
        except Exception as e:
            print(e)
        time.sleep(1)
    f=open('last_id.txt','w')
    f.write(last_id)
    f.close()
    print('Terminate. Last message read: ',last_id)


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from multiprocessing import Process, Queue
import subprocess
from numpy.random import choice
from os import path
driver = webdriver.Chrome()
driver.get("https://web.whatsapp.com/")
inputfield=consulta('//*[@id=\"main\"]/footer/div[1]/div[2]/div/div[2]')
xpaths={
    'input':'//*[@id=\"main\"]/footer/div[1]/div[2]/div/div[2]',
    'attach':'//*[@id=\"main\"]/header/div[3]/div/div[2]/div/span',
    'select_photo':'//*[@id=\"main\"]/header/div[3]/div/div[2]/span/div/div/ul/li[1]/input',
    'send_photo':'//*[@id=\"app\"]/div/div/div[1]/div[2]/span/div/span/div/div/div[2]/span[2]/div/div',
    'caption':'//*[@id=\"app\"]/div/div/div[1]/div[2]/span/div/span/div/div/div[2]/div/span/div/div[2]/div/div[3]/div[1]/div[2]',
    'select_doc':'//*[@id="main"]/header/div[3]/div/div[2]/span/div/div/ul/li[3]/input'

}


while True:
    qorders = Queue() 
    proc = Process(target=infiniteloop,args=(qorders,))
    proc.start()
    order=input()
    qorders.put('')
    if order.lower()=='exit':
        break

driver.close()

