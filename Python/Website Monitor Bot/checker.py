import aiohttp
import asyncio
from datetime import datetime

async def check_site(url: str, keyword: str = None, timeout: int = 10) -> dict:
    result = {
        "status": "down",          # Assume down until proven otherwise
        "status_code": None,       # HTTP status code (200, 404, 500...)
        "response_ms": None,       # Response time in milliseconds
        "error": None,             # Error message if something fails
        "keyword_found": None,     # True/False if keyword was searched
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/122.0 Safari/537.36"
        )
    }

    try:
        start = asyncio.get_event_loop().time()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout),
                allow_redirects=True,
                ssl=False
            ) as response:
                elasped_ms = int((asyncio.get_event_loop().time() - start) * 1000)
                result["status_code"] = response.status
                result["response_ms"] = elasped_ms
                if response.status == 200:
                    if keyword:
                        body = await response.text()
                        if keyword.lower() in body.lower():
                            result["status"] = "up"
                            result["keyword_found"] = True
                        else:
                            result["status"] = "keyword_missing"
                            result["keyword_found"] = False
                    else:
                        result["status"] = "up"
                else:
                    result["status"] = "down"
                    result["error"] = f"HTTP {response.status}"
    except aiohttp.ClientConnectorError:
        result["error"] = "Connection refused / DNS failure"
    except asyncio.TimeoutError:
        result["error"] = f"Timeout after {timeout}s"
    except Exception as e:
        result["error"] = str(e)

    return result


