# oray_instead V 1.0.2 描述
出于下述原因，开发了简单的，类似ORAY的DDNS功能:<br/>
1.ORAY对普通用户不友好,免费版经常崩;<br/>
2.DDNS需求;<br/><br/>
# 环境
    centos7  python v2.7 
# 工具
    dnspod@腾讯云
# 实现功能
对于有独立公网IP的用户,可以放在本地的服务器上运行,更新出口公网IP与腾讯云解析（DNSPOD）记录的对应关系.<br/>
比如，我的需求是www.example.com和download.example.com均解析至出口IP;<br/>
则建立transpon.example.com子域名，并将www和download 通过CNAME 解析其上;<br/>
再在本地通过此程序进行监控及更新即可;<br/>
每次更新后，暂停(1,500)范围内随机秒;<br/>
<br/>
# 使用方法：SHELL后台运行
git clone https://github.com/HighGee/oray_instead.git <br/>
/bin/python -u /the/path/to/oray_instead/tencent_dns_api.py --root_domain example.com --host transpond --secret_id 腾讯云API_ID --secret_key 腾讯云API_KEY <br/><br/>
# 使用方法：进程托管
git clone https://github.com/HighGee/oray_instead.git <br/>
yum install supervisor -y<br/>
#以具体个人需求编辑supervisord_extra.ini，并放至/etc/supervisord.d；<br/>
systemctl start supervisord <br/>
systemctl enable supervisord <br/>
#查看运行状态<br/>
supervisorctl status<br/>

# HELP
[root@captain smalls]# python tencent_dns_api.py -h<br/>
usage: tencent_dns_api.py [-h] [--secret_id SECRET_ID]<br/>
                          [--secret_key SECRET_KEY]<br/>
                          [--root_domain ROOT_DOMAIN] [--host HOST]<br/>
                          [--logfile LOGFILE]<br/>
<br/>
optional arguments:<br/>
  -h, --help            show this help message and exit<br/>
  --secret_id   SECRET_ID   腾讯云API SECRET ID<br/>
  --secret_key  SECRET_KEY  腾讯云API SECRET KEY<br/>
  --root_domain ROOT_DOMAIN 指定根域名<br/>
  --host        HOST        指定解析转发的子域名<br/>
  --logfile LOGFILE     日志文件的绝对路径，默认脚本所在路径下dns.log
