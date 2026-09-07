import json
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

from . import getAuthorization


def _safe_text(value):
    if value is None:
        return "None"
    text = str(value).replace("\r", " ").replace("\n", " ")
    return text.replace(",", "\u3001")


def _parse_external_app_url(url):
    parsed = urlparse(url.strip())
    if parsed.scheme != "https" or parsed.hostname != "cloud.seatable.cn" or parsed.username or parsed.password:
        raise ValueError('请使用 https://cloud.seatable.cn 的课程分享链接。')
    parts = [part for part in parsed.path.split("/") if part]
    try:
        idx = parts.index("external-apps")
        app_uuid = parts[idx + 1]
    except (ValueError, IndexError):
        raise ValueError('链接中缺少 external-apps/课程标识，请复制完整分享链接。')

    page_id = parse_qs(parsed.query).get("page_id", [None])[0]
    if not page_id:
        raise ValueError('链接中缺少 page_id，请打开具体课程页面后复制完整链接。')
    return app_uuid, page_id


def _query_rows(url, university, grade):
    app_uuid, page_id = _parse_external_app_url(url)
    authorization = getAuthorization.getAuthorization(url)

    api_url = "https://cloud.seatable.cn/api/v2.1/universal-apps/{}/query/".format(app_uuid)
    payload = {
        "filters": [
            {
                "column_name": "\u5b66\u6821",
                "is_required": False,
                "enable_fuzzy_query": True,
                "case_sensitive": False,
                "column_key": "0000",
                "filter_predicate": "contains",
                "filter_term": university,
                "id": "HX94",
            },
            {
                "column_name": "\u73ed\u7ea7",
                "is_required": False,
                "enable_fuzzy_query": True,
                "case_sensitive": False,
                "column_key": "2nCB",
                "filter_predicate": "contains",
                "filter_term": grade,
                "id": "DW7a",
            },
        ],
        "sort_by": "",
        "sort_type": "",
        "start": 0,
        "limit": 500,
        "page_id": page_id,
    }

    headers = {
        "Origin": "https://cloud.seatable.cn",
        "Referer": url,
        "Content-Type": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Authorization": "Token " + authorization,
    }

    request = Request(
        api_url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
    )
    with urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))

    if not result.get("success", False):
        raise RuntimeError(result.get("error_message") or "SeaTable query failed")

    rows = result.get("results") or []
    metadata = result.get("metadata") or []
    key_to_name = {
        item.get("key"): item.get("name")
        for item in metadata
        if item.get("key")
    }
    return rows, key_to_name


def _to_legacy_rows(rows, key_to_name):
    output = []
    required_names = ("\u65e5\u671f", "\u661f\u671f", "\u8282\u6b21")

    for row in rows:
        named = {key_to_name.get(key, key): value for key, value in row.items()}
        if any(not named.get(name) for name in required_names):
            raise ValueError('课程数据缺少日期、星期或节次，请检查来源表格。')

        legacy = [
            named.get("\u5b66\u6821"),
            named.get("\u73ed\u7ea7"),
            named.get("\u79d1\u76ee"),
            named.get("\u65e5\u671f"),
            named.get("\u661f\u671f"),
            named.get("\u8282\u6b21"),
            named.get("\u65f6\u95f4"),
            named.get("\u5185\u5bb9"),
            named.get("\u6559\u5e08"),
            named.get("\u7535\u8bdd"),
            named.get("\u5730\u70b9"),
            None,
            None,
            None,
            None,
            None,
        ]
        output.append([_safe_text(value) for value in legacy])

    output.sort(key=lambda values: (values[3], values[4], values[5], values[2], values[8]))
    return output


def validate_inputs(url, university, grade):
    values = dict(url=url.strip(), university=university.strip(), grade=grade.strip())
    if not values['url']:
        raise ValueError('请填写课程分享链接。')
    _parse_external_app_url(values['url'])
    if not values['university']:
        raise ValueError('请填写大学名称。')
    if not values['grade']:
        raise ValueError('请填写年级与班级。')
    return values


def fetch_courses(url, university, grade):
    values = validate_inputs(url, university, grade)
    rows, key_to_name = _query_rows(**values)
    if not rows:
        raise ValueError('没有找到匹配的课程，请检查学校和班级名称。')
    if len(rows) >= 500:
        raise ValueError('匹配结果达到查询上限，请填写更准确的学校和班级，避免导入不完整课表。')
    return _to_legacy_rows(rows, key_to_name)


def describe_error(error):
    if isinstance(error, HTTPError):
        if error.code in (401, 403):
            return '课程页面暂时无法访问，请检查分享链接及访问权限。'
        return '课程网站返回错误（{}），请稍后重试。'.format(error.code)
    if isinstance(error, (URLError, TimeoutError, ConnectionError)):
        return '网络连接失败或超时，请检查网络后重试。'
    if isinstance(error, (ValueError, RuntimeError)):
        return str(error)
    if isinstance(error, OSError):
        return '无法保存课表，请检查存储空间及目录写入权限。'
    return '导入未完成，请稍后重试或检查课程数据。'


def SeatableGet(url, university, grade):
    """Compatibility entry point using the same transactional import as the UI."""
    from .schedule_store import import_schedule
    try:
        import_schedule(url, university, grade)
        return 200
    except Exception as error:
        return describe_error(error)
