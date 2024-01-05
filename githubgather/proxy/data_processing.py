import asyncio
import re
from typing import Any, Dict, List, Optional
from githubgather.client.github_client import AsyncGitHubClient
from githubgather.config import Config


async def deep_fetch_data(client: AsyncGitHubClient, endpoint: str, initial_params: Dict[str, Any],
                          per_page: int, fields: Optional[str] = None, max_pages: Optional[int] = None,
                          headers: Optional[Dict[str, str]] = None) -> Any:
    """
    从GitHub API深度获取数据，支持分页。
    """
    first_page_response = await client.fetch_github_api(endpoint, initial_params, fields=fields, headers=headers)
    max_pages = max_pages if max_pages is not None else Config.DEEP_FETCH_MAX_PAGES

    if isinstance(first_page_response, list):
        all_items = first_page_response
        page = 2
        while len(first_page_response) == per_page and page <= max_pages:
            initial_params["page"] = page
            page_response = await client.fetch_github_api(endpoint, initial_params, fields=fields, headers=headers)
            if not page_response:
                break
            all_items.extend(page_response)
            first_page_response = page_response
            page += 1
        return all_items

    elif isinstance(first_page_response, dict) and 'total_count' in first_page_response:
        total_count = first_page_response.get('total_count', 0)
        total_pages = min(-(-total_count // per_page), -(-int(initial_params.get('max_results', 1000)) // per_page))
        if total_pages <= 1:
            return first_page_response.get('items', [])
        tasks = [asyncio.create_task(client.fetch_github_api(endpoint, {**initial_params, "page": page}, fields=fields))
                 for page in range(2, total_pages + 1)]
        responses = await asyncio.gather(*tasks)
        all_items = first_page_response.get('items', [])
        for response in responses:
            all_items.extend(response.get('items', []))
        return all_items

    return first_page_response


async def process_linked_requests(client: AsyncGitHubClient, primary_response: Dict[str, Any],
                                  linked_params: Dict[str, str], fields: Optional[str] = None) -> Dict[str, Any]:
    """
    处理联动请求。
    """
    if isinstance(primary_response, list):
        for item in primary_response:
            await process_item_linked_requests(item, linked_params, client, fields)
    elif isinstance(primary_response, dict):
        await process_item_linked_requests(primary_response, linked_params, client, fields)
    return primary_response


async def process_item_linked_requests(item: Dict[str, Any], linked_params: Dict[str, str],
                                       client: AsyncGitHubClient, fields: Optional[str]) -> None:
    """
    处理单个项的联动请求。
    """
    for key, endpoint_template in linked_params.items():
        if endpoint_template.startswith("/"):
            endpoint = format_dynamic_path(endpoint_template, item)
            linked_fields = generate_linked_fields(fields, key)
            linked_response = await client.fetch_github_api(endpoint, fields=linked_fields)
            item[key] = linked_response


def generate_linked_fields(fields: str, key: str) -> str:
    """
    生成联动请求特定的字段过滤字符串。
    """
    if fields:
        linked_field_prefix = f"{key}."
        linked_fields = [f[len(linked_field_prefix):] for f in fields.split(',') if f.startswith(linked_field_prefix)]
        return ','.join(linked_fields)
    return ''


def format_dynamic_path(template: str, data: dict) -> str:
    """
    格式化动态路径。
    """
    while '{' in template:
        matches = re.findall(r"{([\w.]+)}", template)
        for match in matches:
            value = extract_nested_value(data, match.split('.'))
            template = template.replace('{' + match + '}', str(value))
    return template


def extract_nested_value(data: dict, path: List[str]):
    """
    从嵌套字典中提取特定路径的值。
    """
    for key in path:
        if key in data:
            data = data[key]
        else:
            raise KeyError(key)
    return data
