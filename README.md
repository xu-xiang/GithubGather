# GitHubGather: Your Ultimate GitHub Data Gathering Tool

## 🚀 Introduction

An easy-to-use harvester based on the official GitHub API proxy, designed for developers, security engineers, data analysts, and more.

Fully compatible with the official GitHub API, **GitHubGather supports automatic switching between multiple tokens**. Simple parameter configuration allows for complex functionalities like batch data scraping.

Whether you're looking to bulk scrape for corporate code leakage, collect CVE vulnerability intelligence from GitHub, or analyze and track project information, GitHubGather simplifies the process!

Combine it with [airflows](https://github.com/xu-xiang/aiflows) to create a data source for task orchestration tools like N8N. Use LLM to intelligently analyze data on GitHub. For instance, automatically gather the latest code containing a CVE vulnerability using GitHubGather, then use large models to explore PoC.

[中文版本(Chinese version)](doc/README.zh-cn.md)


## 🌟 Highlight Features

* API: Fully compatible with the official GitHub API, no worries about unsupported interfaces. Refer to the official API examples.
* Token Rotation: Handles strict GitHub rate limits with automatic token rotation.
* Deep Fetch: Automatically paginate to capture all data in searches, like code, which usually returns a maximum of 100 items at once.
* Field Filtering: Choose to return only the fields you need, for clearer data and improved performance.
* Linked Requests: Efficient data collection with one request triggering multiple API calls (e.g., crawling all READMEs of a user's repositories).
* Docker Deployment: Easy one-click start.

## ⚡ Quick Start

### Docker One-Click Start

```shell
docker run --name githubgather -d -e GITHUB_TOKENS='token1,token2,token3,token4,token5,token6,token7' -p 9000:9000 registry.cn-hangzhou.aliyuncs.com/aiflows/githubgather:latest
```

### Docker Local Build

```shell
docker build -t githubgather .
docker run --name githubgather -d -e GITHUB_TOKENS='token1,token2,token3,token4,token5,token6,token7' -p 9000:9000 githubgather
```

### Local Quick Start

```shell
git clone https://github.com/xu-xiang/GitHubGather.git
cd GitHubGather
pip install -r requirements.txt
export GITHUB_TOKENS='token1,token2,token3,token4,token5,token6,token7'
uvicorn app.main:app --host 0.0.0.0 --port 9000
```

### Give it a Try

GitHubGather is not only powerful but also super easy to use. With just a few simple HTTP requests, you can easily obtain a large amount of GitHub data. Here are some common examples to try out!

#### Get basic information of a specific user

```http request
GET http://localhost:9000/users/{{username}}
Content-Type: application/json
```

#### Get information of a specific repository

```http request
GET http://localhost:9000/repos/{{username}}/{{repo}}
Content-Type: application/json
```

## 📘 Advanced Features

### Deep Fetch

- **Description**: Automatically paginate to retrieve all data from the target interface, no manual handling of multiple pages required.
- **Usage**: Add `?deep_fetch=true` to the request.
- **Applicable Scenarios**: When you need to retrieve all data from a GitHub API interface with multiple pages of data, such as obtaining all repositories or all starred projects of a user.

#### Deep fetch all repositories of a specific user

```http request
GET http://localhost:9000/users/{{username}}/repos?deep_fetch=true&per_page=100
Accept: application/json
```

#### Deep fetch all Starred projects of a user

```http request
GET http://localhost:9000/users/{{username}}/starred?deep_fetch=true&per_page=100
Content-Type: application/json
```

### Pagination Control (Per Page)

- **Description**: Control the amount of data returned in each request.
- **Usage**: Add `&per_page=<number>` to the request, where `<number>` is the number of items you want per page.
- **Default Value**: GitHub API defaults to 30 items per page, but for efficiency, this project uses the maximum value of 100, which can be reduced via this parameter.
- **Applicable Scenarios**: When using deep fetch, adjusting the number of items per page can speed up data scraping or more finely control the amount of data returned.

### Maximum Fetch Pages (Max Pages)

- **Description**: Limit the number of pages fetched in deep fetch mode.
- **Usage**: Add `&max_pages=<number>` to the request, where `<number>` is the maximum number of pages to fetch.
- **Applicable Scenarios**: To limit the amount of data and avoid too many requests when deeply fetching a large amount of data.

#### Limit fetch to a specific number of pages, e.g., 1 item per page, only 2 pages in total

```http request
GET http://localhost:9000/users/{{username}}/repos?deep_fetch=true&per_page=1&max_pages=2
Accept: application/json
```

### Highlighted Code in Search Results

- **Description**: When searching for code, returns snippets with highlighted code, useful in scenarios like code leakage detection.
- **Usage**: Add `&highlight_code=true` to the request to enable code highlighting, default is false.
- **Applicable Scenarios**: When you need to quickly locate and understand code in search results, this feature is particularly useful.

#### Example: Search for highlighted asynchronous Python code snippets

```http request
GET http://localhost:9000/search/code?q=python+async&highlight_code=true
Content-Type: application/json
```

### Linked Requests

- **Description**: Perform multiple API calls in one request, aggregating data from multiple requests.
- **Usage**: Add `&linked_<resource>=<endpoint>` to the request, e.g., `&linked_readme=/repos/{full_name}/readme`.
- **Dynamic Values**: Use `{}` to extract data dynamically from the results of the first request.
- **Applicable Scenarios**: To retrieve related data, like getting all repositories of a user along with their README files.

#### Retrieve repositories and their Readme files, limiting to specific fields

```http request
GET http://localhost:9000/users/{{username}}/repos?linked_readme=/repos/{full_name}/readme
```

### Field Filtering

- **Description**: Retrieve specific data fields only.
- **Usage**: Add `&fields=<field1>,<field2>` to the request, where `<field1>`, `<field2>` are the names of the fields you want to retrieve.
- **Applicable Scenarios**: To reduce the amount of data returned, focusing on the information you care about, like only retrieving a user's login name and contributions.

#### Search for machine+learning related projects and paginate to retrieve all results

```http request
GET http://localhost:9000/search/repositories?q=machine+learning&deep_fetch=true&fields=items.name,items.description
Accept: application/json
```

Example of returned data

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

For more examples, refer to: [test_cases.http](tests/test_cases.http)

API calls can refer to the official GitHub documentation (all can be efficiently proxied): [GitHubAPI](https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#search-code)

## 🔧 Configurable

`GITHUB_TOKENS`: Configure multiple tokens in the environment variable for automatic switching to enhance efficiency.

`DEEP_FETCH_MAX_PAGES`: Set the maximum number of pages for deep fetching, default is 15.

`TOTAL_COUNT_LIMIT`: The upper limit of GitHub API search results (adjust only if the official GitHub API allows more, as of 2024-01-05, the official limit is up to 1000 records), default is 1000

`MAX_RETRIES`: Maximum number of retries, default is 2

For configuration file, refer to: [config.py](githubgather/config.py)

## 🤝 Join Us

Found a bug? Have a fresh idea? Join us to improve GitHubGather!

Fork our repository.
Switch to a new branch (git checkout -b cool-new-feature).
Commit your changes (git commit -am 'Add some cool feature').
Push to the branch (git push origin cool-new-feature).
Submit a Pull Request.

## 📜 License

Licensed under the MIT License, see the LICENSE file for details.

## 💬 Need Help?

Having issues? Not sure how to use? Feel free to raise issues or contact us directly!
