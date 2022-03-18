FROM python:3.8.12
ADD sources.list /etc/apt/
RUN apt-get update && apt-get install dnsutils -y
RUN mkdir /code
WORKDIR /code
ADD pip.requirements /code/
RUN pip3 install -r pip.requirements -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
