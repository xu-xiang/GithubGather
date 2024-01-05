import os
import logging

logging.basicConfig(level=logging.INFO)


class Config:
    # 并发Token池，防止限速
    GITHUB_TOKENS = os.getenv("GITHUB_TOKENS").split(",")
    # GitHub API 搜索结果上限（确保Github官方API的确允许更高才能调整，截止20240105官方最高只能翻页获取1000条记录）
    TOTAL_COUNT_LIMIT = 1000
    # 最大重试次数
    MAX_RETRIES = 2
    # 深度爬取模式程序默认限制深度(例如Github commit接口没有1000条的限制，避免程序遇到超大项目爬取层数过深)
    DEEP_FETCH_MAX_PAGES = 15

    # 待扩展开发其他配置项，如请求速率限制等
