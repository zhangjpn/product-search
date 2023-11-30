# product search api specification
product search api for new aim interview

## 功能说明

### 产品功能点

- 提供产品搜索接口
- 支持给定时间段内对接口进行限流

### 测试

- 单元测试
- 接口测试
- ci/cd


## 系统架构
```mermaid

```

### 考虑点

- 扩展性：支持横向扩展，涉及反向代理nginx
- 性能：搜索引擎 elasticsearch、缓存
- 

## 详细设计
### api

#### 用户授权接口

path: /user/auth
method: POST
payload:
```json
    {
        "account": "example@gmail.com",
        "password": "123456"
    }
```
response:
```json
{
  "status": 0,
  "msg": "Success",
  "data": {
    "access_token": "tk1234",
    "expire_in": 7200
  }
}
```
error code


#### 产品搜索接口

path: /products?keywords=some_name&id=1234&_t=12345
method: GET
headers:
    Authorization: token
response:
```json
{
  "status": 0,
  "msg": "Success",
  "data": {
    "products": [
      {"sku": "", "title": "", "description": ""},
      {"sku": "", "title": "", "description": ""},
    ],
    "has_next": 1
  }
}
```

todo: 搜索数据的分页问题，下一页

#### 流量限制

方案：nginx的流量限制配置
方案：应用层计数，使用redis的key失效时间特性
方案：


#### 流程

用户登陆
用户搜索
商家CRUD商品信息


### database


## 部署

### elasticsearch初始化

### docker-compose

### data import

### 

