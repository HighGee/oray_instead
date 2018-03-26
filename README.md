# oray_instead V 1.0.0
出于下述原因,开发了简单的,类似ORAY的DDNS功能:<br/>
1.ORAY对普通用户不友好,免费版经常崩;<br/>
2.DDNS需求;<br/><br/>
实现功能:<br/>
对于有独立公网IP的用户,可以放在本地的服务器上运行,更新出口公网IP与腾讯云解析记录的对应关系.<br/>
比如，我的需求是www.example.com和download.example.com均解析至出口IP;<br/>
则建立transpon.example.com子域名，并将www和download 通过CNAME 解析其上;<br/>
再在本地通过此程序进行监控及更新即可;<br/>
每次更新后，暂停(1,500)范围内随机秒;<br/>
<br/>
使用方法：<br/>
git clone https://github.com/HighGee/oray_instead.git <br/>
编辑腾讯云ID和KEY<br/>
/bin/python -u /the/path/to/oray_instead/tencent_dns_api.py >> /the/log/path/dns.log &
