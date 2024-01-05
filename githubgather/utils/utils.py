import re


def extract_field_name(template: str) -> str:
    """
    从联动请求模板中提取所需的字段名称。
    """
    match = re.search(r"{([\w.]+)}", template)
    if match:
        return match.group(1).split('.')[0]  # 获取字段名的第一部分
    return ''


def some_other_utility_function():
    """
    其他工具函数，可以根据需要添加更多实用工具。
    """
    pass
