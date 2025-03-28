import asyncio

from app.agent.cogniself import CogniSelf
from app.logger import logger

async def main():
    agent = CogniSelf()
    try:
        prompt = input("请输入要处理的请求：")
        if not prompt.strip():
            logger.warning("请求不能为空")
            return
        logger.warning("正在处理请求...")
        await agent.run(prompt)
        logger.info("请求处理完成")
    except KeyboardInterrupt:
        logger.info("请求处理已完成")
if __name__ == '__main__':
    asyncio.run(main())