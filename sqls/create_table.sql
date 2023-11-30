create table `products` (
    `id` bigint auto_increment,
    `sku` varchar(100) not null default '' comment 'product sku id',
    `title` varchar(200) not null default '' comment 'procduct title',
    `description` varchar(1000) not null default '' comment 'product description',
    primary key (`id`),
    index `idx_sku`(`sku`)
) engine=InnoDB charset=utf8mb4 comment 'product information';

create table `user_infos` (
    `id` bigint auto_increment,
    `username` varchar(30) not null default '' comment 'username',
    `email` varchar(100) not null default '' comment 'email',
    primary key (`id`),
    index `idx_username`(`username`)
) engine=InnoDB charset=utf8mb4 comment 'user profile';

create table `user_auths` (
    `id` bigint auto_increment,
    `uid` varchar(64) not null default '' comment 'encrypted user password',
    `created_at` bigint not null default 0 comment 'data create time',
    `modified_at` bigint not null default 0 comment 'data last modified time',
    `deleted_at` bigint not null default 0 comment 'data delete time',
    primary key (`id`),
    index `idx_uid`(`uid`)
) engine=InnoDB charset=utf8mb4 comment 'user profile';