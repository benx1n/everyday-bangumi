from dataclasses import dataclass
from typing import Tuple
from datetime import datetime, date

@dataclass
class matching:
    keywords: Tuple[str, ...]
    match_keywords : int
    
weekday = [        #同指令中越长的匹配词越靠前
    matching(("星期一","周一","周1","星期1"), 1),
    matching(("星期二","周二","周2","星期2"), 2),
    matching(("星期三","周三","周3","星期3"), 3),
    matching(("星期四","周四","周4","星期4"), 4),
    matching(("星期五","周五","周5","星期5"), 5),
    matching(("星期六","周六","周6","星期6"), 6),
    matching(("星期日","周日","星期天","周日","星期日","星期天"), 7),
    matching(("今天","今日"), datetime.now().weekday() + 1),
]

weekday_cn = ["留空","周一","周二","周三","周四","周五","周六","周日"]