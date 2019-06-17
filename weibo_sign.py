# -*- coding: UTF-8 -*-
'''
@author: 'FenG'
@date: 2018/7/7 17:27
@file: $NAME.py
'''
from __future__ import unicode_literals

import sys

from requests import session
import re
from config import Config
from libs.stmp_email import send_email
import urllib
import random
import time

#USERNAME = Config.USERNAME  # weibo 账号
#PASSWORD = Config.PASSWORD  # weibo 密码
USERDICT = Config.USERDICT
MESSAGE = Config.MESSAGE

class WeiboSign():
    def __init__(self,USERNAME,PASSWORD):
        self.session = session()
        self.USERNAME = USERNAME
        self.PASSOWRD = PASSWORD

    def login(self):
        '''
        登录微博
        :return:
        '''
        data = {
            'username':self.USERNAME,
            'password':self.PASSOWRD
        }
        self.headers = {
            'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&r=http%3A%2F%2Fm.weibo.cn',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        login_url = 'https://passport.weibo.cn/sso/login'
        resp = self.session.post(login_url,data,headers=self.headers)

        if resp.json()['retcode'] != 20000000:
            print('登录失败，错误原因为：{}'.format(resp.json()['msg']))
            sys.exit(1)
        else:
            self.cookie = resp.headers['Set-Cookie']  # 获取cookie
            return resp.json()

    def get_chat_list(self):
        '''
        获取超级话题列表
        :return:
        '''
        chaohua_list = 'https://m.weibo.cn/api/container/getIndex?containerid=100803_-_page_my_follow_super'
        resp_list = self.session.get(chaohua_list).json()
        if resp_list['ok'] != 1:
            print('获取超级话题失败')
            sys.exit(1)
        else:
            return resp_list


    def chat_sign(self):
        '''
        话题签到
        :return:
        '''
        datas = self.get_list_data()
        chat_result = list()
        for data in datas:
            print("准备签到 %s" % data['title_sub'])
            sign_url = "https://weibo.com/p/aj/general/button?ajwvr=6&api=http://i.huati.weibo.com/aj/super/checkin&id={}".format(data['id'])
            print(sign_url)
            req = urllib.request.Request(sign_url)
            req.add_header('cookie', self.cookie)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36')
            resp = urllib.request.urlopen(req)
            data=resp.read().decode('utf-8')
            #print(data)	
            if('100000' in data): print("签到成功")		
            if('100003' in data): 
                print("你最近的行为存在异常，请先验证身份后再进行操作")			
                print(data)            
            if('382004' in data): print("今天已签到")	            
            
            #超话评论
            response = self.session.get(super_url, headers=headers)
            htmlBody = response.text
            #print(htmlBody)
			            
            uid = re.findall(r"CONFIG\[\'uid\'\]=\'\d{0,20}\'", htmlBody)[0].replace("CONFIG['uid']=","").replace("'","")
            #page_id = re.findall(r"CONFIG\[\'page_id\'\]=\'\d{0,30}\'", htmlBody)[0].replace("CONFIG['page_id']=","").replace("'","")
            domain = re.findall(r"CONFIG\[\'domain\'\]=\'\d{0,10}\'", htmlBody)[0].replace("CONFIG['domain']=","").replace("'","")
            location = re.findall(r"CONFIG\[\'location\'\]=\'.{0,30}\'", htmlBody)[0].replace("CONFIG['location']=","").replace("'","")
            mid = re.findall(r"mid=\d{1,30}", htmlBody)[0].replace("mid=","").replace("'","")
            #print(mid)
			
            reply_url = 'https://www.weibo.com/aj/v6/comment/add?ajwvr=6&__rnd=%d'%int(round(time.time() * 1000))
            #print(reply_url)
            text = random.choice(MESSAGE)

            replyData = {
                'mid': mid,
                'uid': uid,		
                'forward': '0',		
                'content': text,		
                'location': 'page_100808_super_index',
                'module': 'scommlist',
                'pdetail': id,
            }
            respon = self.session.post(reply_url, replyData, headers=headers)	   
			#respon.json()['code'] == '100000' :
            if('100000' in respon.text):
                print("评论成功")
            else:
                print("发帖失败")

            #超话发帖
            post_url = 'https://www.weibo.com/p/aj/proxy?ajwvr=6&__rnd=%d'%int(round(time.time() * 1000))
            #print(post_url)
            text = random.choice(MESSAGE)
            postData = {
                'location': 'page_100808_super_index',
                'text': text,
                'style_type': '1',
                'pdetail': id,
                'isReEdit': 'false',
                'sync_wb': '0',
                'pub_source': 'page_1',
                'api': "http://i.huati.weibo.com/pcpage/operation/publisher/sendcontent?sign=super&page_id=" + id ,
                'object_id': "1022:" + id,
                'module': 'publish_913',
                'page_module_id': '913',
			    'longtest': '1',
                'topic_id': "1022:" + id,
                'pub_type': 'dialog',
                '_t': '0'		
            }
            respon = self.session.post(post_url, postData, headers=headers)	   
            #print(respon.text)
			#respon.json()['code'] == '100000' :
            if('100000' in respon.text):
                print("发帖成功")
            else:
                print("发帖失败")
                
        return chat_result
    
    def get_list_data(self):
        '''
        解析数据
        :return:
        '''
        datas = self.get_chat_list()
        result = list()
        card_group = datas['data']['cards'][0]['card_group'][1:-1]
        for card in card_group:
            chat_dict = {
                'id':re.findall("(?<=containerid\=)(.*)&luicode",card['scheme'])[0],
                'desc1':card['desc1'],
                'title_sub':card['title_sub'],
                'title_flag_pic':card['title_flag_pic'],

            }
            result.append(chat_dict)
        return result

if __name__ == '__main__':
    for USERNAME,PASSWORD in  USERDICT.items():
        print("登录%s" % USERNAME)
        weibo = WeiboSign(USERNAME,PASSWORD)
        weibo.login()
        sign_data = weibo.chat_sign()
#    result = []
#    for data in sign_data:
#        result.append('超级话题：{} 签到状态：{} 等级：{}\n'.format(data['title_sub'], data['msg'], data['desc1']))
#    result = ''.join(result)
#    if Config.send_methods =='email':
#        send_email(result)
# print(weibo.get_list_data())
