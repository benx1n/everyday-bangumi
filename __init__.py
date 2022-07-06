from typing import List
import httpx
import traceback
import jinja2
import re
from pathlib import Path

from hoshino import R, Service, priv
from hoshino.typing import CQEvent, MessageSegment

from bs4 import BeautifulSoup
from .html_render import html_to_pic
from .browser import get_new_page
from .utils import bytes2b64

sv_help = '''发送开启 everyday_bangumi，自动将在每日晚八点推送当日番剧'''
sv = Service('everyday-bangumi', manage_priv=priv.SUPERUSER, enable_on_default=True,help_ = sv_help)

dir_path = Path(__file__).parent
template_path = dir_path / "templates"
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path), enable_async=True
)

headers = {
    "user-agent": "benx1n/everyday-bangumi",
}


@sv.on_prefix("查询番剧")
async def send_today_bangumi(bot, ev: CQEvent):
    text = str(ev.message).strip()
    img = await get_today_bangumi(text)
    await bot.send(ev,str(MessageSegment.image(bytes2b64(img))))

@sv.scheduled_job('cron',hour='20')
async def auto_send_daily_bangumi():
#@sv.on_prefix("推送今日番剧")
#async def auto_send_daily_bangumi(bot, ev: CQEvent):
    img = await get_today_bangumi()
    await sv.broadcast(str(MessageSegment.image(bytes2b64(img))), 'auto_send_daily_bangumi', 2)

async def get_today_bangumi(text = '今天'):
    try:
        if not text:
            text = '今天'
        url = 'https://bgmlist.com/'
        data1,data2 = [],[]
        async with get_new_page() as page:
            await page.goto(url)
            await page.click(f"text={text}")
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
                info['imgUrl'] = None
                if info['bangumiId']:
                    async with httpx.AsyncClient(headers=headers) as client:
                        url = f"https://api.bgm.tv/v0/subjects/{info['bangumiId']}"
                        resp = await client.get(url, timeout=None)
                        if resp.status_code == 200:
                            result = resp.json()
                            info['imgUrl'] = result['images']['large']
                        if info['imgUrl']:
                            data1.append(info.copy())
                        else:
                            data2.append(info.copy())
                else:
                    data2.append(info.copy())
            data = {
                "data1":data1,
                "data2":data2,
                "template_path" : template_path
            }
            template = env.get_template("main.html")
            content = await template.render_async(data)
            img =  await html_to_pic(content, wait=0, viewport={"width": 1200 ,"height": 100})
            return img
    except Exception:
        traceback.print_exc()
        return None