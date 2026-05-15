

## 域名配置

```
server {
    listen 443 ssl;
    server_name ${域名};

    ssl_certificate /${path to nginx}/ssl/${pem文件正式};
    ssl_certificate_key /${path to nginx}/ssl/${key文件正式};
    ssl_session_timeout 5m;
    ssl_protocols TLSv1.2 TLSv1.1 TLSv1;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    gzip on;
    gzip_min_length 1k;
    gzip_buffers     4 16k;
    gzip_http_version 1.0;
    gzip_comp_level 2;
    gzip_types       text/plain application/x-javascript text/css application/xml application/json;
    gzip_vary on;
    root  /${path to html};
    rewrite ^/$ /index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
    location /uri  {
        proxy_pass      http://127.0.0.1:80;
        proxy_redirect             off;
        proxy_set_header           Host $host;
        access_log /${path to nginx}/logs/$host.json log_json;
    }
    access_log access;
}

```


## 安装

*参考：*

```shell

cd /tol/soft ; tar zxf  nginx-1.2.4.tar.gz ; cd /tol/soft/nginx-1.2.4 ; ./configure --user=nginx --group=nginx --with-http_stub_status_module --prefix=/tol/app/nginx-1.2.4 ; make && make install ; cd /tol/app; ln -s nginx-1.2.4 nginx

echo "the system initaliztion is ok"
```