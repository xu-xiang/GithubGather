# GitHubGather：你的最佳GitHub数据采集工具

## 🚀 简介

一个基于Github API官方API代理来实现的易用采集器，面向开发者、安全工程师、数据分析人员等。

完全兼容Github官方API接口的同时**支持多Token的自动切换**，可以通过参数配置，简单实现数据的批量爬取等复杂功能。

无论你是项批量爬取识别企业代码信息泄露，还是通过Github采集CVE漏洞情报数据，又或是批量分析挖掘追踪你需要的项目信息等等，都能帮你轻松搞定！

配合[airflows](https://github.com/xu-xiang/aiflows)
可以成为N8N等编排任务数据源，通过LLM自动对Github内的数据进行智能分析。典型的，例如每个CVE漏洞自动调用GithubGather获取包含该漏洞的最新代码全部内容，然后大模型分析挖掘漏洞POC等。

## 🌟 功能亮点

* API：完全兼容Github官方API调用方式，不用担心存在接口不支持，可参考官方API调用示例。
* Token轮换：Github存在严格流控，自动多Token轮换，再也不怕被限速。
* 深度爬取：代码搜索等，一次最多返回100条数据，项目支持自动翻页功能，一次性拿下所有分页数据。
* 字段过滤：可以选择只返回你需要的字段，让数据更清晰，提升性能。
* 联动请求：一次请求，多个API联动，数据收集更高效(例如爬用户下的所有项目的Readme信息)。
* Docker部署：一键启动。

## ⚡ 快速上手

### Docker 一键启动

```shell
docker run --name githubgather -d  -e GITHUB_TOKENS='token1,token2,token3,token4,token5,token6,token7' -p 9000:9000 registry.cn-hangzhou.aliyuncs.com/aiflows/githubgather:latest
```

### Docker 本地构建

```shell
docker build -t githubgather .
docker run --name githubgather -d -e GITHUB_TOKENS='token1,token2,token3,token4,token5,token6,token7' -p 9000:9000 githubgather
```

### 本地快速启动

```shell
git clone https://github.com/xu-xiang/GithubGather.git
cd GithubGather
pip install -r requirements.txt
export GITHUB_TOKENS='token1,token2,token3,token4,token5,token6,token7'
uvicorn app.main:app --host 0.0.0.0 --port 9000
```

### 试试看

GithubGather 不仅功能强大，而且超级易用。只需几个简单的 HTTP 请求，你就能轻松获取大量 GitHub 数据。下面是一些常用的例子，快试试看吧！

#### 获取特定用户的基本信息

```http request
GET http://localhost:9000/users/{{username}}
Content-Type: application/json
```

#### 获取特定仓库信息

```http request
GET http://localhost:9000/repos/{{username}}/{{repo}}
Content-Type: application/json
```

## 📘 高级特性

### 深度爬取（Deep Fetch）

- **描述**：自动翻页获取目标接口的所有数据，无需手动处理多页数据。
- **用法**：在请求中添加 `?deep_fetch=true` 参数。
- **适用场景**：当您需要从具有多页数据的 GitHub API 接口中获取全部数据时，如获取某个用户的所有仓库、所有 star 项目等。

#### 深度爬取特定用户的所有仓库

```http request
GET http://localhost:9000/users/{{username}}/repos?deep_fetch=true&per_page=100
Accept: application/json
```

#### 深度爬取用户所有 Starred 项目

```http request
GET http://localhost:9000/users/{{username}}/starred?deep_fetch=true&per_page=100
Content-Type: application/json
```

### 分页控制（Per Page）

- **描述**：控制每次请求返回的数据量。
- **用法**：在请求中添加 `&per_page=<number>` 参数，其中 `<number>` 是您希望每页返回的项目数量。
- **默认值**：GitHub API 默认每页返回 30 项数据，为了提升爬取效率，本项目默认使用最大值100，可通过该参数调小。
- **适用场景**：在使用深度爬取功能时，通过调整每页数据量，可以加快数据爬取速度或更精细地控制返回的数据量。

### 最大爬取页数（Max Pages）

- **描述**：限制深度爬取时的最大翻页数量。
- **用法**：在请求中添加 `&max_pages=<number>` 参数，其中 `<number>` 是最大的翻页次数。
- **适用场景**：在深度爬取大量数据时，限制数据量，避免过多的请求。

#### 限制爬取数量，例如每页1条，一共只翻2页

```http request
GET http://localhost:9000/users/{{username}}/repos?deep_fetch=true&per_page=1&max_pages=2
Accept: application/json
```

### 搜索结果中匹配(代码高亮)内容返回（Highlight Code）

- **描述**：在搜索代码时，返回带有高亮的代码片段，典型的代码数据泄露检测等场景。
- **用法**：在请求中添加 `&highlight_code=true` 参数，以启用代码高亮功能，默认为false。
- **适用场景**：当您需要在搜索结果中快速定位和理解代码时，这个功能尤其有用。

#### 示例：搜索带有高亮的 Python 异步代码片段

```http request
GET http://localhost:9000/search/code?q=python+async&highlight_code=true
Content-Type: application/json
```

### 联动请求（Linked Requests）

- **描述**：在一次请求中执行多个 API 调用，将多个请求的数据聚合在一起返回。
- **用法**：在请求中添加 `&linked_<resource>=<endpoint>` 参数，例如 `&linked_readme=/repos/{full_name}/readme`。
- **动态值**：可以使用 `{}` 中的动态值从第一次请求的结果中提取数据。
- **适用场景**：获取关联数据，如获取用户的所有仓库及其 README 文件。

#### 获取仓库及其 Readme 文件并限定只返回指定字段数据

```http request
GET http://localhost:9000/users/{{username}}/repos?linked_readme=/repos/{full_name}/readme
```

### 字段过滤（Field Filtering）

- **描述**：仅获取特定的数据字段。
- **用法**：在请求中添加 `&fields=<field1>,<field2>` 参数，其中 `<field1>`, `<field2>` 等是您希望获取的字段名称。
- **适用场景**：减少返回的数据量，专注于您关心的信息，如只获取用户的登录名和贡献数。

#### 搜索machine+learning相关的项目并遍历翻页获取所有结果

```http request
### 搜索machine+learning相关的项目并遍历翻页获取所有结果
GET http://localhost:9000/search/repositories?q=machine+learning&deep_fetch=true&fields=items.name,items.description
Accept: application/json
```

返回数据示例

```text
{
  "items": [
    {
      "description": "A curated list of awesome Machine Learning frameworks, libraries and software."
    },
    {
      "description": "Basic Machine Learning and Deep Learning"
    }
    ...
  ]
}  
```

更多示例可参考: [test_cases.http](tests/test_cases.http)

API调用可参考Github官方文档(
均可进行高性能采集代理): [GithubAPI](https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#search-code)

## 🔧 配置自如

`GITHUB_TOKENS`: 在环境变量中配置多个Token，自动切换，提升效率。

`DEEP_FETCH_MAX_PAGES`: 设定深度爬取的最大页数限制，默认15。

`TOTAL_COUNT_LIMIT`： GitHub API 搜索结果上限（确保Github官方API的确允许更高才能调整，截止20240105官方最高只能翻页获取1000条记录）默认1000

`MAX_RETRIES`: 最大重试次数，默认2

配置文件可参考：[config.py](githubgather/config.py)

## 🤝 加入我们

发现了 Bug？有新鲜想法？加入我们一起改进 GithubGather 吧！

Fork 我们的仓库。
切换到一个新分支 (git checkout -b cool-new-feature)。
提交你的修改 (git commit -am 'Add some cool feature')。
推送到分支 (git push origin cool-new-feature)。
提交一个 Pull Request。

## 📜 开源协议

采用 MIT 许可证，详情见 LICENSE 文件。

## 💬 需要帮助？

遇到问题？不清楚怎么使用？随时欢迎你提出 issues 或者直接联系我们！