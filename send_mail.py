#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
ALi
20180909
Python 3.7.0
"""

import socket

import get_mx


"""
Send_Mail([timeout=10, [try_num=100]]) 发送邮件
    timeout 单次连接超时
    try_num 发送失败最大尝试次数
send(mail_from, mail_to, message)
    In:
        mail_from 发件人
        mail_to 收件人
        message 邮件内容
    Out:
        response [SUCCESS] 发件成功并返回发件过程
                 [ERROR] Send mail false. 达到失败最大尝试次数
                         Socket error. 连接错误
                         Searching DNS error. 解析DNS错误
SMTP非登录发件流程
    HELO 发件人域名
    MAIL FROM:<发件人邮箱>
    RCPT TO:<收件人邮箱>
    DATA
    邮件内容
    . DATA结束符
    QUIT
"""


class Send_Mail(object):
    def __init__(self, timeout=10, try_num=10):
        self.timeout = timeout
        self.try_num = try_num

    def send(self, mail_from, mail_to, message):
        response = ''
        mail_servers = get_mx.Get_MX().get(mail_to.split('@')[1])
        if mail_servers != False:
            mail_servers.sort()
            command_helo = 'HELO ' + mail_from.split('@')[1] + '\r\n'
            command_mail_from = 'MAIL FROM:<' + mail_from + '>\r\n'
            command_rcpt_to = 'RCPT TO:<' + mail_to + '>\r\n'
            command_data = 'DATA\r\n'
            message_end = '\r\n.\r\n'
            command_quit = 'QUIT\r\n'
            send_success = False
            error_info = ''
            for num in range(self.try_num):
                for mail_server in mail_servers:
                    try:
                        smtp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
                        smtp_socket.settimeout(self.timeout)
                        smtp_socket.connect((mail_server[1], 25))
                        recv_connect = smtp_socket.recv(1024).decode()
                        smtp_socket.send(command_helo.encode())
                        recv_helo = smtp_socket.recv(1024).decode()
                        smtp_socket.send(command_mail_from.encode())
                        recv_mail_from = smtp_socket.recv(1024).decode()
                        smtp_socket.send(command_rcpt_to.encode())
                        recv_rcpt_to = smtp_socket.recv(1024).decode()
                        smtp_socket.send(command_data.encode())
                        recv_data = smtp_socket.recv(1024).decode()
                        smtp_socket.send(message.encode())
                        smtp_socket.send(message_end.encode())
                        recv_message = smtp_socket.recv(1024).decode()
                        smtp_socket.send(command_quit.encode())
                        recv_quit = smtp_socket.recv(1024).decode()
                        smtp_socket.close()
                        if (recv_connect[:3] == '220' and recv_helo[:3] == '250' and
                            recv_mail_from[:3] == '250' and recv_rcpt_to[:3] == '250' and
                            recv_data[:3] == '354' and recv_message[:3] == '250'):
                            response = ('[SUCCESS]' +
                                        'SMTP SERVER: ' +
                                        mail_server[1] +
                                        '    PORT: 25\r\n' +
                                        'MAIL FROM: ' +
                                        mail_from +
                                        '\r\nMAIL TO: ' +
                                        mail_to +
                                        '\r\n\r\n' +
                                        recv_connect +
                                        command_helo +
                                        recv_helo +
                                        command_mail_from +
                                        recv_mail_from +
                                        command_rcpt_to +
                                        recv_rcpt_to +
                                        command_data +
                                        recv_data +
                                        message[:100] +
                                        '...' +
                                        message_end +
                                        recv_message +
                                        command_quit +
                                        recv_quit)
                            send_success = True
                            break
                        else:
                            error_info = ('[ERROR]Send mail false.\r\n\r\n' +
                                          'SMTP SERVER: ' +
                                          mail_server[1] +
                                          '    PORT: 25\r\n' +
                                          'MAIL FROM: ' +
                                          mail_from +
                                          '\r\nMAIL TO: ' +
                                          mail_to +
                                          '\r\n\r\n' +
                                          recv_connect +
                                          command_helo +
                                          recv_helo +
                                          command_mail_from +
                                          recv_mail_from +
                                          command_rcpt_to +
                                          recv_rcpt_to +
                                          command_data +
                                          recv_data +
                                          message[:100] +
                                          '...' +
                                          message_end +
                                          recv_message +
                                          command_quit +
                                          recv_quit)
                    except BaseException:
                        error_info = '[ERROR]Socket error.'
                if send_success:
                    break
            if not send_success:
                response = error_info
        else:
            response = '[ERROR]Searching DNS error.'
        return response
