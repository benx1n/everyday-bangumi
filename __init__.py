from typing import List
import httpx
import traceback
import jinja2
import re
from pathlib import Path

from os.path import dirname, join, exists
from hoshino import R, Service, priv
from hoshino.typing import CQEvent, MessageSegment

from bs4 import BeautifulSoup
from .html_render import html_to_pic
from .browser import get_new_page
import json

sv_help = '''发送开启 everyday_bangumi，自动将在每日零点推送当日番剧'''
sv = Service('everyday-bangumi', manage_priv=priv.SUPERUSER, enable_on_default=True,help_ = sv_help)
headers = {
    "user-agent": "benx1n/everyday-bangumi",
    "Authorized": "iv7gzEN38C6tH4HqlJjfPTsOqFtA00y4El6wpxgB"
}
@sv.on_prefix("测试番剧推送")
async def get_today_bangumi(bot, ev: CQEvent):
    try:
        url = 'https://bgmlist.com/'
        data = []
        async with get_new_page() as page:
            await page.goto(url)
            await page.click("text=今天")
            soup = BeautifulSoup(await page.content(), 'html.parser')
            bangumi_list = soup.select('article')
            for each_bangumi in bangumi_list:
                info,playWeb_list = {},[]
                infoList = each_bangumi.select('div')
                info['cnName'] = infoList[0].select_one('h3').string
                info['jpTime'] = infoList[1].select_one('dd').string
                info['cnTime'] = infoList[2].select_one('dd').string
                info['startTime'] = infoList[3].select_one('dd').string
                infoUrl = infoList[4].select('dd ul li a')
                info['bangumiId'] = None
                for each in infoUrl:
                    match = re.search(r"subject\/(.*?)$",each.attrs['href'])
                    if match:
                        info['bangumiId'] = match.group(1)
                        break
                play = infoList[5].select('dd ul li a')
                for each in play:
                    playWeb_list.append(each.string)
                info['playWeb'] = playWeb_list
                if info['bangumiId']:
                    async with httpx.AsyncClient(headers=headers) as client:
                        url = f"https://api.bgm.tv/v0/subjects/{info['bangumiId']}"
                        resp = await client.get(url, timeout=None)
                        if resp.status_code == 200:
                            result = resp.json()
                            info['imgUrl'] = result['images']['large']
                data.append(info.copy())
            print(json.dumps(data,ensure_ascii=False))

    except Exception:
        traceback.print_exc()
        return None