#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Date    : 2023/3/4 0004 23:31
@Author  : ViCrack

补天
1、已通过的漏洞，定价后将无法查看漏洞详情。
2、未通过审核的，七天后将无法查看漏洞详情。

自己提交的不能看详情，搞不懂这种骚操作，所以写个定时保存文章的功能
"""
import re
import time
from pathlib import Path

import browser_cookie3
import requests
from pyquery import PyQuery
from requests.adapters import HTTPAdapter

user_agent = ''
save_path = r''


headers = {
    'User-Agent': user_agent,
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.butian.net/'
}
req = requests.Session()
req.headers = headers
req.cookies = browser_cookie3.firefox(domain_name='.butian.net')
req.mount('http://', HTTPAdapter(max_retries=1))
req.mount('https://', HTTPAdapter(max_retries=1))


def main():
    center_html = req.get('https://www.butian.net/WhiteHat/Center').text
    m_token = re.search(r'token: "(.*?)"', center_html)
    if not m_token:
        print('可能是没有登录')
        return
    token = m_token.group(1)
    total_page = 1
    current_page = 1

    while current_page <= total_page:
        # 不明白他们这里为啥取名为loo
        resp = req.post('https://www.butian.net/WhiteHat/Center/loo',
                        data={
                            'title': '',
                            'level': '',
                            'status': '0',
                            'p': current_page,
                            'token': token
                        },
                        headers={
                            'Accept': 'application/json, text/javascript, */*; q=0.01',
                            'X-Requested-With': 'XMLHttpRequest'
                        })
        # print(resp.text)
        loo_list = resp.json()
        if loo_list['status'] != 1:
            print(f'出错啦，{current_page} {loo_list}')
            break

        current_page += 1
        total_page = int((loo_list['data']['count'] - 1) / 10 + 1)
        finished = False
        for loo in loo_list['data']['list']:
            create_date = loo['create_time'][:10]
            title = loo['title']
            number = loo['number']
            company_name = loo['company_name']
            file_path = Path(f'{save_path}/{create_date}/{number} {title}.html')
            if file_path.exists():
                html_content = file_path.read_text(encoding='utf-8')
                if '<p>补天审核中</p>' not in html_content and '</html>' in html_content:
                    # 已经处理保存过了，不需要重复运行
                    break
            loo_url = f'https://www.butian.net/Loo/detail/{number}.html'
            html_content = req.get(loo_url).text
            if '详情隐藏' in html_content:
                print(f'{create_date} {title} 已经被隐藏了')
                # 直接结束就行，因为按时间来算，后面的都是隐藏
                finished = True
                break
            time.sleep(0.5)
            if loo['status'] == '审核不通过':
                # 把不通过的原因写上，免得到时候去翻
                html_content = html_content.replace('<p>审核不通过</p>', f'<p>审核不通过({loo["assessor"]})</p>{loo["reason"]}')

            print(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 精简内容，节省磁盘空间，大概能看就能行，又不是不能看
            doc = PyQuery(html_content)
            pageDetail = doc('#pageDetail')
            pageDetail.find('.loopDetTitle').find('span').attr('onclick', f'window.open("{loo_url}")')
            pageDetail.find('.loopEdit').remove()
            pageDetail.find('.prompt').remove()
            liuyan = pageDetail.find('.liuyanShuru')
            liuyan.parent().prev().remove()
            liuyan.parent().remove()
            # 漏洞详情解析
            # detail_content = pageDetail.find('#detail').html()
            detail_content = re.search(r'<div id="detail">(.*?)</div>', html_content, re.DOTALL).group(1)
            detail_content = html.unescape(detail_content)

            pageDetail.find('#detail').html(detail_content)
            pageDetail_content = re.sub(r'<em class="(.*?)"/>', r'<em class="\1"></em>', str(pageDetail)).replace('&#13;', '')
            # 也许应该把图片下载下来，谁知道会不会把这也屏蔽了
            with file_path.open(mode='w', encoding='utf-8') as f:
                f.write('''
<!DOCTYPE html>
<html>
<head><style type="text/css">
    .shield{width:295px;height:42px;background-color:#000;position:absolute;z-index:99;opacity:0.0;filter:alpha(opacity=0);display:block;}.confirmTime{position:absolute;left:0;top:0;display:inline-block;width:136px;height:42px;line-height:42px;text-align:center;color:#fff;font-size:14px;border-radius:5px;margin-right:20px;background:#211212;opacity:0.8;}.prompt{padding:10px 20px;background:#efefef;}.prompt h2{line-height:30px;}.prompt p{line-height:24px;}.loopDetTitle h2{padding-right:110px;}.el-message-box .el-message-box__status{top:22px;}
</style>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=0.1, maximum-scale=1.0, user-scalable=yes" />
    <meta name="renderer" content="webkit|ie-comp|ie-stand">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,Chrome=1" />
    <title>%s %s</title>
    <link rel="stylesheet" type="text/css" href="https://www.butian.net/Public/css/base.css">
    <link rel="stylesheet" type="text/css" href="https://www.butian.net/Public/css/loopSetting.css">
    <link rel="stylesheet" type="text/css" href="https://www.butian.net/Public/css/ele.css">
    <link rel="stylesheet" type="text/css" href="https://www.butian.net/Public/css/ele-common.css">
    <style>
        .loginSeting p {
            clear: both;
        }

        .active-li {
            position: relative;
        }

        .active-li>img {
            position: absolute;
            right: -17px;
            top: 22px;
        }
    </style>
    <link rel="stylesheet" type="text/css" href="https://www.butian.net/Public/css/loop.css">
    <link rel="stylesheet" type="text/css" href="https://www.butian.net/Public/css/plugins.css">
</head>
<body class="lotteryWrap">
                ''' % (number, title))

                f.write(pageDetail_content)
                f.write('''
</body>
</html>
                ''')
        if finished:
            break
    print('运行结束')


if __name__ == '__main__':
    main()
