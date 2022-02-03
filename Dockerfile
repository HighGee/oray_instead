FROM python:3.9
RUN sed -i 's/httpredir.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list
RUN mkdir /code
WORKDIR /code
ADD pip.requirements /code/
RUN pip3 install -r pip.requirements -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
