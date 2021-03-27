# 一、描述
出于下述，开发了简单的，类似ORAY的DDNS功能:<br/>
* ORAY对普通用户不友好,免费版经常崩
* DDNS需求
# 二、环境
* python 3.6.8
* dnspod@腾讯云
# 三、功能
* 对于有独立公网IP的用户, 可以由此工具更新本地出口公网IP与腾讯云解析（DNSPOD）NS 记录
    * 比如，需求是www.example.com和download.example.com均解析至出口IP
    * 则建立transpond.example.com子域名，并将www和download 通过CNAME 解析其上
    * 再在服务端通过此程序进行监控出口IP的变化及更新transpond子域名的解析记录
# 四、使用方法
## 4.1. 使用前准备
    touch cause/config.yaml # 并按环境情况进行逐项核实
    vim cause/config.yaml

    or

    cp cause/config.yaml.example cuase/config.yaml
    vim cause/config.yaml
## 4.2. docker
    docker-compose up -d
## 4.3. SHELL后台运行
    git clone https://github.com/HighGee/oray_instead.git
    /bin/python -u /the/path/to/oray_instead/ddns_sync.py &
## 4.4. 进程托管
    git clone https://github.com/HighGee/oray_instead.git
    yum install supervisor -y
    #以具体个人需求编辑supervisord_extra.ini，并放至/etc/supervisord.d/
    systemctl start supervisord
    systemctl enable supervisord
    # 查看运行状态
    supervisorctl status