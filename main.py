from apscheduler.schedulers.asyncio import AsyncIOScheduler

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageChain, filter
from astrbot.api.star import Context, Star
from astrbot.core.config.astrbot_config import AstrBotConfig

from .crawlers import updateInfo


class MCMODUpdaterPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.scheduler = AsyncIOScheduler()

    async def initialize(self):
        self.scheduler.add_job(
            self._check_all,
            trigger="interval",
            seconds=3600,
            id="update_check",
            replace_existing=True,
        )
        if not self.scheduler.running:
            self.scheduler.start()
        logger.info("MC模组更新通知插件已初始化")

    async def terminate(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
        logger.info("MC模组更新通知插件已停用")

    def _format_result(self, result: dict[str, str]) -> str:
        return ("[查询结果]\n"
                f"链接：{result['URL']}\n"
                f"模组名称：{result['name']}\n"
                f"最新版本：{result['version']}\n"
                f"更新日期：{result['date']}\n"
                f"更新日志：\n{result['log']}")

    def _update_mod_data(self, result: dict[str, str]):
        lastVersion = "无"
        for data in self.config["modData"]:
            if data["URL"] == result["URL"]:
                lastVersion = data["version"]
                if data["version"] != result["version"]:
                    data["version"] = result["version"]
                    data["date"] = result["date"]
                    data["log"] = result["log"]
                    self.config.save_config()
                break
        else:
            self.config["modData"].append({
                "__template_key": "mod",
                **result,
            })
            self.config.save_config()
        return lastVersion

    @filter.command("mc强制更新")
    async def _check_all(self, event: AstrMessageEvent=None):
        """手动调用更新所有订阅内容的函数，和自动更新是相同的，DEBUG用"""
        count = 0
        for subscriber in self.config["subscribe_relation"]:
            for url in subscriber["URL"]:
                try:
                    result = await updateInfo(url)
                    lastVersion = self._update_mod_data(result)
                except Exception as e:
                    logger.error(f"获取 {url} 的信息时出错：{str(e)}")
                if lastVersion != result["version"]:
                    count += 1
                    await self.context.send_message(subscriber["ID"], MessageChain().message(f"[更新通知] {lastVersion} -> {result['version']}\n").message(self._format_result(result)))
        if event is not None:
            yield event.plain_result(f"手动更新完成，共更新 {count} 个模组")

    @filter.command("mc查询")
    async def mc_query(self, event: AstrMessageEvent):
        """查询指定模组的最新版本信息，不更新订阅数据和版本记录"""
        args = event.message_str.strip().split(" ")[1:]
        if len(args) < 1:
            yield event.plain_result("用法：/mc查询 <URL>")
            return
        url = args[0]

        try:
            result = await updateInfo(url)
            yield event.plain_result(self._format_result(result))
        except ValueError as e:
            yield event.plain_result(str(e))
        except Exception as e:
            yield event.plain_result(f"获取 {url} 的信息时出错：{str(e)}")

    @filter.command("mc订阅")
    async def mc_subscribe(self, event: AstrMessageEvent):
        """在当前会话订阅指定模组的更新通知"""
        session_id = event.unified_msg_origin
        args = event.message_str.strip().split(" ")[1:]
        if len(args) < 1:
            yield event.plain_result("用法：/mc订阅 <URL>")
            return
        url = args[0]

        try:
            result = await updateInfo(url)
            yield event.plain_result(self._format_result(result))
        except ValueError as e:
            yield event.plain_result(str(e))
            return
        except Exception as e:
            yield event.plain_result(f"获取 {url} 的信息时出错：{str(e)}")
            return
        for subscriber in self.config["subscribe_relation"]:
            if subscriber["ID"] == session_id:
                if url in subscriber["URL"]:
                    yield event.plain_result(f"您已订阅：{url}")
                    return
                subscriber["URL"].append(url)
                self.config.save_config()
                break
        else:
            self.config["subscribe_relation"].append({"__template_key": "subscriber", "ID": session_id, "URL": [url]})
            self.config.save_config()

        yield event.plain_result(
            "订阅成功！\n"
            "系统将每小时检查一次更新，发现新版本会主动通知您。"
        )

    @filter.command("mc取消订阅")
    async def mc_unsubscribe(self, event: AstrMessageEvent):
        """取消当前会话订阅指定模组的更新通知"""
        session_id = event.unified_msg_origin
        args = event.message_str.strip().split(" ")[1:]
        if len(args) < 1:
            yield event.plain_result("用法：/mc取消订阅 <URL>")
            return
        url = args[0]

        for subscriber in self.config["subscribe_relation"]:
            if subscriber["ID"] == session_id:
                if url in subscriber["URL"]:
                    subscriber["URL"].remove(url)
                    self.config.save_config()
                    yield event.plain_result(f"已取消订阅：{url}")
                else:
                    yield event.plain_result(f"您未订阅：{url}")
                return
        else:
            yield event.plain_result(f"您未订阅：{url}")

    @filter.command("mc订阅列表")
    async def mc_list(self, event: AstrMessageEvent):
        """显示当前会话订阅的模组订阅列表"""
        session_id = event.unified_msg_origin

        for subscriber in self.config["subscribe_relation"]:
            if subscriber["ID"] == session_id:
                URLs = subscriber["URL"]
                break
        else:
            yield event.plain_result(
                "您还没有订阅任何模组/整合包。使用 /mc订阅 <URL> 来添加订阅。"
            )
            return

        table = {}
        for mod in self.config["modData"]:
            if mod["URL"] in URLs:
                table[mod["URL"]] = mod["name"]
        lines = ["[您的订阅列表]\n"]
        for i, url in enumerate(URLs):
            lines.append(f"[{i + 1}]. [{table.get(url, url)}]({url})\n")
        yield event.plain_result("\n".join(lines).strip())
