from typing import Any
from fastapi import Request
from githubgather.client.github_client import AsyncGitHubClient
from githubgather.client.exceptions import APIError
from githubgather.proxy.data_processing import deep_fetch_data, process_linked_requests
from starlette.responses import JSONResponse
import logging
import re

# 创建日志记录器
logger = logging.getLogger("github_proxy")


async def proxy_to_github(request: Request, rest_of_path: str, client: AsyncGitHubClient) -> Any:
    try:
        params = dict(request.query_params)
        perform_deep_fetch = params.pop('deep_fetch', None) == 'true'
        per_page = int(params.get('per_page', 100))
        fields = params.get('fields', '')  # 不立即弹出，以便后续操作
        highlight_code = params.pop('highlight_code', None) == 'true'
        max_pages = int(params.get('max_pages', None)) if 'max_pages' in params else None

        headers = {}
        if highlight_code:
            headers["Accept"] = "application/vnd.github.v3.text-match+json"

        # 处理联动请求
        linked_params = {k: v for k, v in params.items() if k.startswith('linked_')}
        for key, endpoint_template in linked_params.items():
            params.pop(key)  # 从参数中移除
            if fields:
                # 把linked_里面的{}模版字段添加到过滤字段，即使用户没有主动配置（即关联字段默认属于过滤要展示的字段）
                fields += f',{extract_field_name(endpoint_template)}'

        # 根据情况调用不同函数
        response = await deep_fetch_data(client, f"/{rest_of_path}", params, per_page, fields=fields,
                                         max_pages=max_pages,
                                         headers=headers) \
            if perform_deep_fetch else \
            await client.fetch_github_api(f"/{rest_of_path}", params, fields=fields, headers=headers)

        if linked_params:
            # 将联动请求相关的字段过滤字符串传递给处理函数
            response = await process_linked_requests(client, response, linked_params, fields=fields)

        return response
    except APIError as e:
        # 返回具体的错误信息和状态码
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})


def extract_field_name(template: str) -> str:
    """
    从联动请求模板中提取所需的字段名称。
    """
    match = re.search(r"{([\w.]+)}", template)
    if match:
        return match.group(1).split('.')[0]  # 获取字段名的第一部分
    return ''
