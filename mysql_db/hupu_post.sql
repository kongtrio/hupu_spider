drop table if exists hupu_post;
CREATE TABLE hupu_post (
  id bigint unsigned NOT NULL auto_increment comment '帖子id',
  hupu_post_id bigint unsigned not null unique comment '该帖子在虎扑中的id',
  title varchar(128) not null comment '帖子标题',
  author varchar(128) not null comment '帖子作者',
  url varchar(512) not null comment '帖子地址',
  post_time bigint not null comment '发帖时间',
  view_count int not null comment '帖子观看数量',
  reply_count int not null comment '回复数量',
  gmt_created bigint not null comment '记录创建时间',
  gmt_modified timestamp not null default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP comment '记录更新时间',
  is_deleted bit not null default 0 comment '该帖子是否被删除',
  PRIMARY KEY (id)
) ENGINE = InnoDB CHARSET = utf8mb4;