import httpx
import itertools
import time
import asyncio
from typing import Any, Dict, Optional, List
from githubgather.client.exceptions import APIError
from githubgather.config import Config
import logging
from fastapi import Response


class AsyncGitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.client = httpx.AsyncClient()
        self.token_iterator = itertools.cycle(Config.GITHUB_TOKENS)
        self.logger = logging.getLogger("AsyncGitHubClient")

    async def fetch_github_api(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
                               headers: Optional[Dict[str, str]] = None, fields: Optional[str] = None,
                               retries: int = 0) -> Any:
        last_response = None
        while retries <= Config.MAX_RETRIES:
            token = next(self.token_iterator)
            auth_headers = {"Authorization": f"token {token}"}
            if headers:
                auth_headers.update(headers)

            try:
                self.logger.info(f"Sending request to GitHub API: {endpoint} with params: {params}")
                self.logger.debug(f"with token: {token}")
                response = await self.client.get(f"{self.BASE_URL}{endpoint}", params=params, headers=auth_headers)
                response.raise_for_status()
                try:
                    response_data = response.json()
                    return self._filter_response_data(response_data, fields)
                except ValueError:
                    # 非Json结果例如https://api.github.com/favicon.ico 直接返回
                    return Response(content=response.content, media_type=response.headers["content-type"])
            except httpx.HTTPStatusError as e:
                self.logger.error(f"HTTP error occurred: {e.response.text}")
                if 'Only the first 1000 search results are available' in e.response.text:
                    self.logger.warning("Reached the limit of 1000 search results.")
                last_response = e.response
                if e.response.status_code == 403 and 'rate limit exceeded' in e.response.text:
                    rate_limit_data = await self._get_rate_limit_data()
                    limit_category = self._determine_limit_category(rate_limit_data)
                    await self._handle_rate_limit(limit_category)
                    retries += 1
                    continue
                raise APIError(e.response.status_code, e.response.json().get('message'))
            except Exception as e:
                self.logger.error(f"An error occurred: {e}")
                raise

        if last_response:
            raise httpx.HTTPStatusError("Rate limit exceeded after maximum retries", request=last_response.request,
                                        response=last_response)
        else:
            raise Exception("Error in API request after maximum retries reached")

    async def _get_rate_limit_data(self) -> Dict[str, Any]:
        response = await self.client.get(f"{self.BASE_URL}/rate_limit")
        return response.json().get("resources", {})

    @staticmethod
    def _determine_limit_category(rate_limit_data: Dict[str, Any]) -> str:
        for category, data in rate_limit_data.items():
            if data.get("remaining", 0) == 0:
                return category
        return "core"

    async def _handle_rate_limit(self, limit_category: str):
        rate_limit_reset = await self._get_rate_limit_reset_time(limit_category)
        wait_seconds = int(max(0, int(rate_limit_reset - time.time())))
        self.logger.info(f"Waiting for {wait_seconds} seconds due to rate limit...")
        await asyncio.sleep(wait_seconds)

    async def _get_rate_limit_reset_time(self, limit_category: str) -> int:
        rate_limit_data = await self._get_rate_limit_data()
        reset_time = rate_limit_data.get(limit_category, {}).get("reset", int(time.time()))
        return reset_time

    def _filter_response_data(self, data: Any, fields: Optional[str]) -> Any:
        if not fields:
            return data
        field_paths = fields.split(',')
        if isinstance(data, list):
            return [self._filter_response_data(item, fields) for item in data]
        if isinstance(data, dict):
            result = {}
            for field_path in field_paths:
                field_levels = field_path.split('.')
                self._extract_nested_field(data, field_levels, result)
            return result
        return data

    def _extract_nested_field(self, data: dict, field_levels: List[str], result: dict, current_path: str = ''):
        if len(field_levels) == 1:
            key = current_path + field_levels[0] if current_path else field_levels[0]
            if field_levels[0] in data:
                result[key] = data[field_levels[0]]
            return
        if field_levels[0] in data:
            new_path = current_path + field_levels[0] + '.' if current_path else field_levels[0] + '.'
            if isinstance(data[field_levels[0]], dict):
                self._extract_nested_field(data[field_levels[0]], field_levels[1:], result, new_path)
            elif isinstance(data[field_levels[0]], list):
                result[new_path[:-1]] = [self._filter_response_data(item, '.'.join(field_levels[1:])) for item in
                                         data[field_levels[0]]]
