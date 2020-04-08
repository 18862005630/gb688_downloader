import base64
import re
import time

import requests

from .config import BAN_LIST


def get(url: str) -> str:
    headers = {
        'Accept': 'text/plain, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1',
        'X-Requested-With': 'XMLHttpRequest'
    }
    r = requests.post(url, headers=headers)
    return r.text


def get_bytes(hcno: str) -> bytes:
    """
    这部分代码可以在对 http://openstd.samr.gov.cn/bzgk/gb/index 网站的手机版预览模式下抓包获得
    :param hcno:
    :return:
    """
    text = ""
    for i in range(0, 10):
        if i == 0:
            url = f"http://c.gb688.cn/bzgk/gb/viewGb?type=online&hcno={hcno}"
        else:
            url = f"http://c.gb688.cn/bzgk/gb/viewGb?type=online&hcno={hcno}.00{i}"
        time.sleep(1)

        text += get(url)
        print(f"正在下载中{i * 10}%")
    pdf_bytes = base64.standard_b64decode(text)
    return pdf_bytes


def get_hcno(url: str) -> str:
    """获取hcno

    :param url:
    :return:
    """
    hcno = url.split("?hcno=")[1]
    return hcno


def is_download(url: str) -> bool:
    """判断能否下载pdf

    :param url:
    :return:
    """
    r = requests.get(url)
    if "在线预览" in r.text:
        return True
    else:
        return False


def get_pdf_name(url: str) -> tuple:
    """获取pdf的名称

    :param url: 网页
    :return: 返回pdf的名称
    """
    r = requests.get(url)
    g_name = re.findall(r"标准号：(.*?) </h1></td>", r.text)
    c_name = re.findall(r"中文标准名称：<b>(.*?)</b></td>", r.text)
    if len(g_name) == 0 or len(c_name) == 0:
        input("未找到标准号和标准名称")
        raise Exception("未找到标准号和标准名称")
    return g_name[0], c_name[0]


def download(url: str):
    if not is_download(url):
        raise Exception("这个文件展示不支持下载，原页面没有在线预览，请自行打开网页进行查询")

    hcno = get_hcno(url)
    g_name, c_name = get_pdf_name(url)
    pdf_name = f"{g_name}({c_name})"

    for b in BAN_LIST:
        pdf_name = pdf_name.replace(b, " ")

    pdf_bytes = get_bytes(hcno)

    path = f"{pdf_name}.pdf"
    with open(path, "wb") as f:
        f.write(pdf_bytes)
    print("下载成功")

    return path

