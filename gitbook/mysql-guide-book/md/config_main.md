```
[client]
port=5021
socket=/tol/tmp/db_phoenix.sock
default-character-set = utf8mb4

[mysqld] 
server-id=1107
port=5027
user                                    = mysql
basedir                                 = /tol/server/mysql
datadir                                 = /tol/data/db_phoenix
tmpdir                                  = /tol/tmp
socket                                  = /tol/tmp/db_phoenix.sock
pid-file                                = /tol/tmp/db_phoenix.pid
explicit_defaults_for_timestamp=off
skip-external-locking
skip-name-resolve
lower_case_table_names                  = 1
log_bin_trust_function_creators         = 1
default-storage-engine                  = INNODB
wait_timeout                            = 120
connect_timeout                         = 20
interactive_timeout                     = 500
net_read_timeout                        = 100
back_log                                = 512
log_timestamps                          = SYSTEM 
general_log                             = 0
general_log_file                        = general.log
log-bin                                 = mysql-bin
binlog_format                           = ROW
max_binlog_size                         = 1G
binlog_cache_size                       = 2M
expire-logs-days                        = 10
sync_binlog                             = 0
binlog_rows_query_log_events            = 1
relay-log                               = relay-bin
relay_log_purge                         = 1 
relay_log_recovery                      = 1
slave-net-timeout                       = 10
slave_compressed_protocol               = 1
master_info_repository                  = TABLE
relay_log_info_repository               = TABLE
slave_parallel_type                     = LOGICAL_CLOCK
slave_parallel_workers                  = 0
slave_preserve_commit_order             = 1
slow_query_log                          = 1
slow-query_log_file                     = /tol/logs/slowsql.db_phoenix.log
long_query_time                         = 1
log_error                               = error.log
max_connections                         = 1000
max_user_connections                    = 900
max_connect_errors                      = 10000
query_cache_type                        = 1
query_cache_size                        = 16M
table_open_cache                        = 1024
table_definition_cache                  = 4096
sort_buffer_size = 256K
read_buffer_size = 256K
read_rnd_buffer_size = 512K
join_buffer_size = 256K
max_heap_table_size                     = 64M
max_allowed_packet                      = 100M
tmp_table_size                          = 64M
thread_cache_size                       = 300
low_priority_updates                    = 1
delay_key_write                         = ON
concurrent_insert                       = 1
key_buffer_size                         = 16M
myisam_sort_buffer_size                 = 64M
myisam_max_sort_file_size               = 64M
myisam_repair_threads                   = 1
myisam-recover-options                  = backup,force
innodb_fast_shutdown                    = 1
innodb_data_home_dir                    = /tol/data/db_phoenix
innodb_log_group_home_dir               = /tol/data/db_phoenix
innodb_data_file_path                   = ibdata1:512M:autoextend
innodb_buffer_pool_size                 = 4G
innodb_buffer_pool_instances            = 8
innodb_log_file_size                    = 256M 
innodb_log_buffer_size                  = 64M
innodb_log_files_in_group               = 3
innodb_flush_log_at_trx_commit          = 1
innodb_max_dirty_pages_pct              = 90
innodb_support_xa                       = 1
innodb_thread_concurrency               = 0
innodb_thread_sleep_delay               = 500
innodb_concurrency_tickets              = 1000
innodb_flush_method                     = O_DIRECT
innodb_file_per_table                   = 1
innodb-read-io-threads                  = 16
innodb-write-io-threads                 = 8
innodb_io_capacity                      = 1000
innodb_file_format                      = Barracuda
innodb_file_format_max                  = Barracuda
innodb_purge_threads                    = 1
innodb_purge_batch_size                 = 32
innodb_old_blocks_pct                   = 37
innodb_open_files                       = 40960
#thread_handling                         = pool-of-threads
#thread_pool_max_threads                 = 300
#thread_pool_size                        = 64
innodb_strict_mode                      = 1
innodb_stats_on_metadata                = O
innodb_buffer_pool_dump_at_shutdown     = 1
innodb_buffer_pool_load_at_startup      = 1
innodb_buffer_pool_dump_now             = 1
innodb_buffer_pool_load_now             = 1
#skip-innodb-adaptive-hash-index
innodb_kill_idle_transaction            = 30
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
init_connect='SET NAMES utf8mb4'
sql_mode =''
read_only=1
gtid-mode                              = ON
enforce_gtid_consistency               = 1
log_slave_updates=1
secure_file_priv=''
skip-slave-start

[mysqldump]  
quick 
max_allowed_packet                      = 128M
myisam_max_sort_file_size               = 10G 

[mysql]  
auto-rehash
prompt                                  = (\\u@\\h) [\\d]>\\_
secure-auth                             = off
default-character-set = utf8mb4

[myisamchk]  
key_buffer_size                         = 64M  
sort_buffer_size                        = 64M
read_buffer                             = 256M  
write_buffer                            = 256M 

[mysqlhotcopy]  
interactive-timeout 

[mysqld_safe]
open-files-limit                        = 40960
malloc-lib                              = /usr/lib64/libjemalloc.so.1
```