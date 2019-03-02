# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2019-02-28 22:24
import re
import smtplib
import requests
from email.mime.text import MIMEText
from email.header import Header
from cause.log_handler import own_log
from cause.config import own_cfg

email_logger = own_log('EMAIL', own_cfg.log_file)


class IsMail():
    """
    判断是否为邮箱地址
    """

    def __init__(self):
        self.p = re.compile(r"[^\._][\w\._-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+$")

    def ismail(self, str):
        res = self.p.match(str)
        if res:
            return True
        else:
            return False


def send_errmsg(receiver, title=None, content=None):
    """
    邮件通知模块
    """

    ipipNetUrl = "http://myip.ipip.net"
    is_email = IsMail()
    if is_email.ismail(receiver[0]):
        if title is None:
            title = u"[故障]出口IP获取异常"
        if content is None:
            try:
                content = requests.get(ipipNetUrl).content
            except:
                content = u"外网断开，无法获取出口IP"
        msg = MIMEText(content, "html", _charset="utf-8")
        me = "OrayInstead@haiji.io"
        msg["Subject"] = Header(title, charset="utf-8")
        msg["From"] = me
        msg["To"] = ";".join(receiver)

        try:
            s = smtplib.SMTP("localhost")
            s.sendmail(me, receiver, msg.as_string())
            s.quit()
        except Exception, e:
            email_logger.error(u"邮件通知失败，目标邮箱：%s %s" % (";".join(receiver), e))
    else:
        email_logger.error(u"邮件通知失败，目标邮箱：%s" % ";".join(receiver))


def mail_mass(receivers, title=None, content=None):
    """
    收信人处理
    """
    if receivers is not None:
        if ";" in receivers:
            for email in receivers.split(";"):
                send_errmsg([email], title=title, content=content)
        else:
            send_errmsg([receivers], title=title, content=content)
