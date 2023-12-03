# product search api specification
product search api for new aim interview


## Architecture

![architecture](./docs/assets/architecture.png)

assumption:
- 本系统实现了上述架构图中红框的部分，在真实生产环境中，该系统不是独立存在的，数据将通过消息队列、rest api等方式从其它系统获取。该数据处理部分在本次功能中未实现，而是使用脚本从本地csv文件中获取、处理并写入。
- 在真实环境中，往往存在多个用户访问，为简单起见，本系统仅通过环境变量配置的方式提供一个`api key`作为用户身份。
- 在真实环境中，出于规模、性能、可靠性方面的原因，系统各个组建往往采用集群的方式提供服务，往往需要服务注册和服务发现完整的系统，为简单起见，本系统仅通过环境变量配置的方式获取所依赖服务的访问地址。
- 本系统实现的匹配是基于英文语境下的文本搜索，对其它语言的支持不是特别完善。
- 在业务逻辑层面，本系统采取将关键词与商品标题进行匹配的方式，而未对商品描述做过多处理
- 在数据返回环节，真实系统可能会返回更多商品各个维度的信息，这将涉及数据缓存的环节，本系统未实现

feature：
- 基于elasticsearch构建，对title字段进行分词和倒排索引，以匹配用户输入的关键词
- 对于标题中没有相应关键词的情况，系统将使用语义搜索的方式寻找数据库中与关键词语义接近的title
- 接口限流，在首次访问算起，给定时间区间内只能访问限定次数，区间时长和允许访问次数可通过环境变量配置

实现
- 上述app使用flask+gunicorn提供web服务
- embedding service基于tensorflow-serving和谷歌开源的universal-sentence-encoder模型提供文本向量化功能，为语义搜索提供支撑
- 限流功能通过redis提供的键过期功能实现


## 详细设计

### api

#### 产品搜索接口

path: /products?keywords=some_name&id=1234&_t=12345 
method: GET 
headers: 
    Authorization: token

response:

```json
{
  "err_code": 0,
  "msg": "Success",
  "data": {
    "items": [
      {"id": "", "sku": "", "title": "", "description": ""},
      {"id": "", "sku": "", "title": "", "description": ""},
    ],
    "has_next": 1
  }
}
```
字段说明

| 字段                       | 数据类型    | 是否必传 | 描述                   |
|--------------------------|---------|------|----------------------|
| err_code                 | integer | 是    | 错误码，0-无错误，其它见通用错误码取值 |
| msg                      | string  | 是    | 错误描述                 |
| data                     | object  | 是    | 具体返回数据               |
| data.has_next            | integer | 是    | 是否有下一页：1-有；0-没有      |
| data.items               | array   | 是    | 商品列                  |
| data.items[]             | object  | 是    | 商品项                  |
| data.items[].id          | string  | 是    | 商品id                 |
| data.items[].sku         | string  | 是    | 商品sku                |
| data.items[].title       | string  | 是    | 商品title              |
| data.items[].description | string  | 是    | 商品描述                 |




## 部署

1. download embedding model

```shell
# download 
wget https://storage.googleapis.com/kaggle-models-data/1265/1497/bundle/archive.tar.gz?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20231202%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20231202T110124Z&X-Goog-Expires=259200&X-Goog-SignedHeaders=host&X-Goog-Signature=9f431df72fa76e3f2e8215a7c135a476af010e7ae0506d6736a40a57f95dfda04996deb3ddaa36fb34d8c83c705b2cb06fb101934c659143c16d6cca96c4e7ad1f7961c4eb003fec56e90e43749dce555b7097ce049acdbf2775df8185066c03b5fb88152b5cfa4d75d6c38a49b1847c429b12813980b1e5c47256b27501af94a47b24eca7b993587e6dbbd4732cbf1f27534ea2ee0d93acc7efb92741889aef2b35e6431ae4552a5f15907bec5d7144201263df205dca30ff252eb00e8cfdc48852050988930d4854aa1711889bb1623bde2406249571d1168c4b1b00e1bc4379520dd34f72fb10f505f2f73d5696dc02ea6760c596ded35ecdc85f72cedca1
mkdir -p app/models/embedding/1
tar -xvf archive.tar.gz -C app/models/embedding/1
```

2. build application docker image

```shell
docker build . -t product_app:1.0
```
3. 
3. 
### elasticsearch初始化

### docker-compose

### data import

### 

