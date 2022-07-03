from typing import List
import httpx
import traceback
import jinja2
import re
from pathlib import Path

from os.path import dirname, join, exists
import hoshino
from hoshino import R, Service, priv
from hoshino.typing import CQEvent, MessageSegment

from bs4 import BeautifulSoup
from .html_render import html_to_pic
from .browser import get_new_page

sv_help = '''发送开启 everyday_bangumi，自动将在每日零点推送当日番剧'''
sv = Service('everyday-bangumi', manage_priv=priv.SUPERUSER, enable_on_default=True,help_ = sv_help)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
}
@sv.on_prefix("测试番剧推送")
async def get_today_bangumi(bot, ev: CQEvent):
    try:
        url = 'https://bgmlist.com/'
        async with get_new_page() as page:
            await page.goto(url)
            await page.click("text=今天")
            soup = BeautifulSoup(await page.content(), 'html.parser')
            bangumi_list = soup.select('article')
            for each_bangumi in bangumi_list:
                play_list = []
                infoList = each_bangumi.select('div')
                cnName = infoList[0].select_one('h3').string
                jpTime = infoList[1].select_one('dd').string
                cnTime = infoList[2].select_one('dd').string
                startTime = infoList[3].select_one('dd').string
                infoUrl = infoList[4].select('dd ul li a')
                bangumiId = None
                for each in infoUrl:
                    match = re.search(r"subject\/(.*?)$",each.attrs['href'])
                    if match:
                        bangumiId = match.group(1)
                        break
                play = infoList[5].select('dd ul li a')
                for each in play:
                    play_list.append(each.string)
                print(cnName,jpTime,cnTime,startTime,bangumiId,play_list)

    except Exception:
        traceback.print_exc()
        return None