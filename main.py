import asyncio
import os
import aiofiles
import aiohttp
import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage, Message
from zhipuai import ZhipuAI  # 导入新的AI模型模块

# 读取配置文件
test_config = read(os.path.join(os.path.dirname(__file__), "bot_config.yaml"))

# 获取日志记录器
_log = logging.get_logger()

# 创建ZhipuAI客户端实例
client = ZhipuAI(api_key="2b5a8c3fd438df8af00a006b8a20ba7f.ALfTiirSr4GG8fT2")  # 请替换为您的API密钥

# 创建一个名为 'completions' 的属性，指向 ZhipuAI 模块中的聊天功能
client.completions = client.chat.completions

# 定义MyClient类，继承自botpy.Client
class MyClient(botpy.Client):
    # 创建一个名为 'completions' 的属性，指向 ZhipuAI 模块中的聊天功能
    completions = client.completions
    # 定义on_ready方法
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    # 定义on_group_at_message_create方法
    async def on_group_at_message_create(self, message: GroupMessage):
        try:
            # 打开聊天历史文件
            async with aiofiles.open(f"./ai_chat/{message.author.member_openid}.txt", 'r', encoding='utf-8') as f:
                history_chat = eval(await f.read())
        except Exception as e:
            _log.error(f"Error reading chat history: {e}")
            history_chat = []

        # 将用户的消息添加到历史聊天记录中
        history_chat.append({"role": "user", "content": message.content})

        # 调用ZhipuAI的chat.completions.create方法获取回复
        response = client.completions.create(
            model="charglm-3",
            messages=history_chat,
            meta={
                "user_info": "误入幻想乡的人类",
                "bot_info": "蕾米莉亚是500岁的吸血鬼领主，夜之王。她是红魔馆的主人，芙兰朵露的姐姐。萝莉体型，身穿粉红色的洋装。作为红魔馆的主人，和一般的贵族一样注重威严和体面。但性格却跟外表一样，非常任性和孩子气。她拥有“操纵命运程度的能力”，似乎会使被影响者有很高概率遇上珍奇的事。",
                "bot_name": "蕾米莉亚·斯卡雷特",
                "user_name": "人类"
            },
        )

        # 获取回复内容
        reply_content = response.choices[0].message.content

        _log.info(f"Received reply: {reply_content}")

        # 将回复内容添加到历史聊天记录中
        history_chat.append({"role": "assistant", "content": reply_content})

        # 回复用户
        await message.reply(content=f"\n{reply_content}")

        # 将更新后的历史聊天记录写入到文件中
        async with aiofiles.open(f"./ai_chat/{message.author.member_openid}.txt", 'w', encoding='utf-8') as f:
            await f.write(str(history_chat))

            print(response.choices[0].message)

# 主程序入口

if __name__ == "__main__":
    intents = botpy.Intents(public_messages=True, public_guild_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], secret=test_config["secret"])
