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
  content text comment '帖子内容',
  content_is_set bit not null default 0 comment '内容是否已经设置',
  PRIMARY KEY (id)
) ENGINE = InnoDB CHARSET = utf8mb4;

drop table if exists hupu_post_reply;
create table hupu_post_reply(
  id bigint unsigned NOT NULL auto_increment comment '回复id',
  hupu_reply_id bigint unique not null comment '虎扑回复的id',
  author varchar(128) not null comment '回复的用户',
  hupu_post_id bigint unsigned not null comment '回复的帖子id',
  reply_time bigint not null comment '回复时间',
  like_count int not null default 0 comment '亮了的次数',
  content text comment '回复内容',
  floor_num int not null comment '回复所属楼层',
  gmt_created bigint not null comment '记录创建时间',
  gmt_modified timestamp not null default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP comment '记录更新时间',
  PRIMARY KEY (id)
) ENGINE = InnoDB CHARSET = utf8mb4;