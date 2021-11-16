FROM debian:11

ENV HOME /root
ENV USER root
ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL C.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

WORKDIR /root/app/

EXPOSE 5000

ENV DISPLAY=:99

ADD app /root/app/

RUN mkdir /root/tmp &&\
    cd /root/tmp &&\
    sed -i 's/deb.debian.org/mirrors.cloud.tencent.com/g' /etc/apt/sources.list &&\
    sed -i 's/security.debian.org/mirrors.tencent.com/g' /etc/apt/sources.list &&\
    sed -i 's/https/http/g' /etc/apt/sources.list &&\
    apt update &&\
    apt install -y wget python3-pip xvfb supervisor unzip redis-server &&\
    wget https://mirrors.imea.me/packages.microsoft.com/repos/edge/pool/main/m/microsoft-edge-stable/microsoft-edge-stable_95.0.1020.53-1_amd64.deb &&\
    dpkg -i microsoft-edge-stable_95.0.1020.53-1_amd64.deb || true &&\
    apt install -fy &&\
    wget https://mirrors.imea.me/msedgedriver.azureedge.net/95.0.1020.53/edgedriver_linux64.zip &&\
    unzip edgedriver_linux64.zip &&\
    mv msedgedriver /usr/bin &&\
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple &&\
    pip install -r /root/app/requirements.txt &&\
    rm /root/tmp -rf &&\
    apt autoremove -y


ADD supervisor.conf /etc/supervisor/conf.d/

ENTRYPOINT ["/usr/bin/supervisord","--nodaemon"]