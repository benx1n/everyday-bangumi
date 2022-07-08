from typing import List
import httpx
import traceback
import jinja2
import re
from pathlib import Path
from datetime import datetime
from hoshino import R, Service, priv
from hoshino.typing import CQEvent, MessageSegment

from bs4 import BeautifulSoup
from .html_render import html_to_pic
from .browser import get_new_page
from .utils import bytes2b64,match_keywords
from .data_source import weekday,weekday_cn

sv_help = '''发送开启 everyday_bangumi，每日晚自动推送当日番剧'''
sv = Service('everyday-bangumi', enable_on_default=True,help_ = sv_help)

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
    text = str(ev.message).split()
    if not text:
        weekday_int = datetime.now().weekday() + 1
    else:
        weekday_int,text = await match_keywords(text,weekday)
        if not weekday_int:
            await bot.send(ev,"格式不正确哦，请跟随周一至周日或今天")
            return
    print(weekday_int)
    img = await get_today_bangumi(weekday_int)
    await bot.send(ev,str(MessageSegment.image(bytes2b64(img))))

@sv.scheduled_job('cron', hour='0', minute='01')
async def auto_send_daily_bangumi():
#@sv.on_prefix("推送今日番剧")
#async def auto_send_daily_bangumi(bot, ev: CQEvent):
    img = await get_today_bangumi()
    await sv.broadcast(str(MessageSegment.image(bytes2b64(img))), 'auto_send_daily_bangumi', 2)

async def get_today_bangumi(weekday = datetime.now().weekday() + 1):
    try:
        data1,data2 = [],[]             #有图片/没图片
        async with httpx.AsyncClient(headers=headers) as client:
            url = f"https://api.bgm.tv/calendar"
            resp = await client.get(url, timeout=None)
            if resp.status_code == 200:
                result = resp.json()
                for each in result:
                    info = {}
                    if each['weekday']['id'] == weekday:
                        for each_bangumi in each['items']:
                            if each_bangumi['name_cn']:
                                info['cnName'] = each_bangumi['name_cn']
                            else:
                                info['cnName'] = each_bangumi['name']
                            info['startTime'] = each_bangumi['air_date']
                            info['bangumiId'] = each_bangumi['id']
                            info['playWeb'] = ''
                            info['jpTime'] = '暂无'
                            info['cnTime'] = '暂无'
                            if each_bangumi['images']:
                                info['imgUrl'] = each_bangumi['images']['large']
                                data1.append(info.copy())
                            else:
                                info['imgUrl'] = None
                                data2.append(info.copy())
                            
        url = 'https://bgmlist.com/'
        async with get_new_page() as page:
            await page.goto(url)
            print(weekday_cn[weekday])
            await page.click(f"text=全部")
            soup = BeautifulSoup(await page.content(), 'html.parser')
            bangumi_list = soup.select('article')
            for each_bangumi in bangumi_list:
                playWeb_list = []
                infoList = each_bangumi.select('div')
                infoUrl = infoList[4].select('dd ul li a')
                playWeb = infoList[5].select('dd ul li a')
                for each in infoUrl:
                    match = re.search(r"subject\/(.*?)$",each.attrs['href'])
                    if match:
                        for each_data1 in data1:
                            if each_data1['bangumiId'] == int(match.group(1)):
                                print(f'发现匹配的番剧{match.group(1)}')
                                each_data1['jpTime'] = infoList[1].select_one('dd').string
                                each_data1['cnTime'] = infoList[2].select_one('dd').string
                                count = 0
                                for each in playWeb:
                                    playWeb_list.append(each.string)
                                    count += 1
                                    if count == 6:
                                        break
                                each_data1['playWeb'] = playWeb_list
                        break
            data = {
                "data1":data1,
                "data2":data2,
                "template_path" : template_path,
                "title": weekday_cn[weekday]
            }
            print(data)
            template = env.get_template("main.html")
            content = await template.render_async(data)
            img =  await html_to_pic(content, wait=0, viewport={"width": 1200 ,"height": 100})
            return img
    except Exception:
        traceback.print_exc()
        return None