### 主配置

```
user nginx nginx;
worker_processes 4;
worker_cpu_affinity  auto;
error_log /${path to nginx}/logs/nginx_error.log crit;
pid /${path to nginx}/nginx.pid;
worker_rlimit_nofile 51200;
events
{
    use epoll;
    worker_connections 51200;
}


http {
    include       mime.types;
    default_type   application/octet-stream;
    proxy_headers_hash_max_size 51200;
    proxy_headers_hash_bucket_size 6400;
    server_names_hash_max_size 10240;
    server_names_hash_bucket_size 256;
    client_header_buffer_size 128k;
    large_client_header_buffers 4 128k;
    client_max_body_size 500M; 
    sendfile on;
    tcp_nopush     on;
    server_tokens off;
    server_info off;
    keepalive_timeout 200;
    tcp_nodelay on;
    fastcgi_intercept_errors on;
    gzip on;
    gzip_min_length 1k;
    gzip_buffers     4 16k;
    gzip_http_version 1.0;
    gzip_comp_level 2;
    gzip_types       text/plain application/x-javascript text/css application/xml application/json;
    gzip_vary on;

    server {
        client_max_body_size 500M;

    }
    add_header Cache-Control no-cache;
    log_format main '$remote_addr	[$time_local]	$request	$status	$http_referer	$body_bytes_sent	$content_length	$request_time	$http_user_agent	$server_name	$upstream_status	$upstream_addr	$upstream_response_time	$scheme	$request_body';
    log_format log_json escape=json '$request_body';

    include /${path to nginx}/conf/vhost/*.conf;
    
    access_log /${path to nginx}/logs/$host.log main;
}

```
