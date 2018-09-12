# SMTP-Fork
基于SMTP协议的邮件伪造和邮件炸弹

## 介绍
邮件自动发送程序，使其可以用伪造的电子邮件地址向某一邮箱发送成千上万次的邮件，实现最基本的邮件炸弹攻击方式。  

## 环境
* Python 3.7.0  
* Linux（根据系统可能需要修改`SMTP-fork/SMTP/conf.py`和 `SMTP-fork/server/view.py`里的路径）

### 第三方库
* Pygame
* Django
* dnspython

## 使用
### 将文件夹命名为SMTP-fork

### 进入文件目录，运行manage.py  
```shell
cd SMTP-fork

python manage.py runserver 0.0.0.0:8080
```

### 用浏览器访问即可，本地访问为 http://127.0.0.1:8080/
