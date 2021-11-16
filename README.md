# ForceSSR
使用selenium渲染webpack网页，返回给搜索引擎蜘蛛，达到服务端渲染效果。 

## 效果
正常访问
[![QQ20211116163126.png](https://image.futechlab.com/images/2021/11/16/QQ20211116163126.png)](https://image.futechlab.com/image/AuJ)
搜索引擎蜘蛛访问
[![QQ20211116163052.png](https://image.futechlab.com/images/2021/11/16/QQ20211116163052.png)](https://image.futechlab.com/image/vfN)

## 使用方法
### 安装docker-ce
https://docs.docker.com/engine/install/ubuntu/

### 编译docker镜像
```
git clone https://github.com/kamino-space/ForceSSR.git
cd ForceSSR
docker build -t forcessr:latest .
```
### 运行docker容器
```
docker run -d -e DOMAINS=testdomain1.com,testdomain2.com --restart always --name forcessr forcessr:latest
```
### 查看容器ip地址
```
docker inspect forcessr
```
### 配置nginx反向代理
将原有网站新建一个server
```
server {
    listen 127.0.0.1:9001;
    root /var/www/wwwroot;
    access_log off;
    error_log off;

    location / {
        index index.html;
        try_files $uri $uri/ /index.html;
    }
}
```
nginx按user-agent判断是否为搜索引擎
```
server {
    listen 443 ssl;
    server_name domain;
    ssl_certificate cert.cer;
    ssl_certificate_key cert.key;

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        set $is_bot 0;
        if ($http_user_agent ~* (Baiduspider|Googlebot|360Spider|SogouSpider|YisouSpider|bingbot|YoudaoBot|msnbot|YandexBot|MJ12bot|SemrushBot|Bytespider|AspiegelBot)) {
            proxy_pass http://container_ip:5000; #容器ip地址
            set $is_bot 1;
        }
        if ($is_bot = 0) {
            proxy_pass http://127.0.0.1:9001;
        }
    }
}
```
