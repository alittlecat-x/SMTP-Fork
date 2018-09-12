#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
ALi
20180911
Python 3.7.0
"""

import traceback
from django.shortcuts import render


import sys
sys.path.append('..')
from SMTP import conf
from SMTP import smtp_boom

def smtp_in(request):
    return render(request, 'SMTP-in.html')

def smtp_out(request):
    try:
        print(request.POST)
        mail_from = request.POST['mail_from']
        mail_to = request.POST['mail_to']
        subject = request.POST['subject']
        sender = request.POST['sender']
        recipient = request.POST['recipient']
        text = request.POST['text']
        send_num = int(request.POST['send_num'])
        round = request.POST['round']
        if round == 'True':
            round = True
        else:
            round = False
        if 'file' not in request.POST:
            file_object = request.FILES.get('file')
            file_name = file_object.name
            with open('../SMTP-fork/' + conf.file_path, 'wb') as f:
                for chunk in file_object.chunks():
                    f.write(chunk)
                f.close()
        else:
        	file_name = ''
        
        response = smtp_boom.SMTP_Boom().boom(mail_from, mail_to, subject, sender, recipient, text, file_name, send_num, round)
    except BaseException:
        response = 'Parameter error.'
        traceback.print_exc()
    context = {}
    context['response'] = response
    return render(request, 'SMTP-out.html', context)
