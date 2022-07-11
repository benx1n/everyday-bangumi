# everyday-bangumi
每日番剧推送

## 部署流程
1. 在HoshinoBot的插件目录modules下clone本项目 `git clone https://github.com/benx1n/everyday-bangumi.git`
2. 在项目文件夹下执行`pip install -r requirements.txt`安装依赖
4. 在 `config/__bot__.py`的模块列表里加入 `everyday-bangumi`
5. 重启hoshinoBot
6. 本插件默认开启，如不需要请在lssv中禁用本模块即可`禁用 everyday-bangumi`

## 指令
- 每日番剧+星期，默认今日，例：
  - 每日番剧
  - 每日番剧 今天
  - 每日番剧 周六
- 凌晨自动推送当日番剧
## 预览
<div align="left">
  <img src="https://benx1n.oss-cn-beijing.aliyuncs.com/img/everyday-bangumi_small.png" width="300" />
</div>

## 感谢
[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)  
[nonebot-plugin-htmlrender](https://github.com/kexue-z/nonebot-plugin-htmlrender)