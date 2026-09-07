import re
from urllib.request import Request, urlopen


def getAuthorization(url):
    """Fetch the anonymous access token exposed by a SeaTable external app page."""
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=20) as response:
        raw_html_data = response.read().decode("utf-8", errors="replace")

    match = re.search(r"accessToken:\s*'([^']+)'", raw_html_data)
    if not match:
        raise RuntimeError('无法读取课程页面，请确认分享链接仍然有效且允许公开访问。')
    return match.group(1)
