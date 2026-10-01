#!/usr/bin/env python3
"""
    NepSecretary - Yuuki
    ~~~~~~~~~

    Version: v8.0

    Copyright(c) 2021 Star Inc.
    Copyright(c) 2026 Neptune Studio. All Rights Reserved.
    The software licensed under Mozilla Public License Version 2.0
"""

import asyncio
import logging
import sys

from src.bot import Yuuki
from src.config import Config
from src.kernel.polling import Polling


async def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        config = Config.load()
    except FileNotFoundError as error:
        print(error)
        sys.exit(1)

    bot = Yuuki(config)
    await bot.start()
    revision = await bot.client.get_last_op_revision()
    print(f"{bot.name} {bot.version} - Start Successful!")

    polling = Polling(bot.client, revision=revision, guard=lambda: bot.power)
    try:
        await polling.run(bot.dispatcher)
    finally:
        await bot.shutdown()


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("NepSecretary BOT - Bye!")


if __name__ == "__main__":
    main()
