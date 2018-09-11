from django.shortcuts import render

import sys 
sys.path.append('..')
from SMTP import conf
from SMTP import smtp_boom

def smtp_in(request):
    return render(request, 'SMTP-in.html')

def smtp_out(request):
    try:
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
        file_object = request.FILES.get('file')
        file_name = file_object.name
        with open('..\\SMTP-fork\\' + conf.file_path, 'wb') as f:
            for chunk in file_object.chunks():
                f.write(chunk)
            f.close()
        response = smtp_boom.SMTP_Boom().boom(mail_from, mail_to, subject, sender, recipient, text, file_name, send_num, round)
    except BaseException as e:
        response = 'Parameter error.%s'%e
    context = {}
    context['response'] = response
    return render(request, 'SMTP-out.html', context)
