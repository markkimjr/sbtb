import traceback
from typing import Union, Optional, Dict, Any

import requests
import aiohttp

from sbtb.core.logging import logger


def get_request(url, params=None, headers=None, proxies=None, cookies=None, timeout=5, verify=True, max_retries=1,
                return_json=False, return_res_text=False, allow_redirects=True) -> Union[requests.Response, str, None]:
    res = None
    try:
        session = requests.Session()
        session.headers.update(headers or {})
        for i in range(max_retries):
            res = session.request(method="GET", url=url, params=params, proxies=proxies, cookies=cookies,
                                  timeout=timeout, verify=verify, allow_redirects=allow_redirects)
            if res.status_code == 200:
                if return_json:
                    return res.json()
                if return_res_text:
                    return res.text
                return res

        if res and isinstance(res, requests.Response):
            logger.info(f"REQUEST INFO: {res.status_code}/{res.text}")
        return res
    except Exception as e:
        traceback.print_exc()
        logger.error(f"ERROR GETTING REQUEST: {e}")
        return res


def post_request(url, data=None, json=None, headers=None, proxies=None, cookies=None, timeout=5, max_retries=1,
                 return_json=False, return_res_text=False, allow_redirects=True) -> Union[requests.Response, str, None]:
    res = None
    try:
        session = requests.Session()
        session.headers.update(headers or {})
        for i in range(max_retries):
            res = session.request(method="POST", url=url, data=data, json=json, headers=headers, proxies=proxies,
                                  cookies=cookies, timeout=timeout, allow_redirects=allow_redirects)
            if res.status_code == 200 or res.status_code == 201:
                if return_res_text:
                    return res.text
                if return_json:
                    return res.json()
                return res

        if res and isinstance(res, requests.Response):
            logger.info(f"REQUEST INFO: {res.status_code}/{res.text}")
        return res
    except Exception as e:
        traceback.print_exc()
        logger.error(f"ERROR POSTING REQUEST: {e}")
        return res


async def async_get_request(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    timeout: int = 5,
    max_retries: int = 1,
    return_json: bool = False,
    return_res_text: bool = False,
    allow_redirects: bool = True,
    ssl: bool = True,
) -> Union[Dict[str, Any], str, aiohttp.ClientResponse, None]:
    for i in range(max_retries):
        try:
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(headers=headers, cookies=cookies, timeout=timeout_obj) as session:
                async with session.get(url, params=params, allow_redirects=allow_redirects, ssl=ssl) as res:
                    if res.status == 200:
                        if return_json:
                            return await res.json()
                        if return_res_text:
                            return await res.text()
                        return res
                    logger.info(f"GET attempt {i+1}: {res.status} - {await res.text()}")
        except Exception as e:
            logger.error(f"GET attempt {i+1} failed: {e}")
            traceback.print_exc()
    return None


async def async_post_request(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    timeout: int = 5,
    max_retries: int = 1,
    return_json: bool = False,
    return_res_text: bool = False,
    allow_redirects: bool = True,
    ssl: bool = True,
) -> Union[Dict[str, Any], str, aiohttp.ClientResponse, None]:
    for i in range(max_retries):
        try:
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(headers=headers, cookies=cookies, timeout=timeout_obj) as session:
                async with session.post(url, data=data, json=json, allow_redirects=allow_redirects, ssl=ssl) as res:
                    if res.status in [200, 201]:
                        if return_json:
                            return await res.json()
                        if return_res_text:
                            return await res.text()
                        return res
                    logger.info(f"POST attempt {i+1}: {res.status} - {await res.text()}")
        except Exception as e:
            logger.error(f"POST attempt {i+1} failed: {e}")
            traceback.print_exc()
    return None
