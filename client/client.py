import logging
from sys import platform as _platform
import argparse
import asyncio
from .utils import ws_cmd, heartbeat_info

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)


def get_args():
    args = argparse.ArgumentParser(description='Device Client')
    args.add_argument("server", type=str, help="Server Name")
    args.add_argument("token", type=str, help="Server Token")
    args.add_argument("--heartbeat", type=int,
                      help="Heartbeat Retval",
                      default=30, required=False)
    args.add_argument("--retval", type=int,
                      help="Reconnect Server retval",
                      default=30, required=False)
    args.add_argument("--port", type=int, required=False,
                      default=16604, help="Server Port")
    args = args.parse_args()
    return args


async def main(loop):
    if _platform.startswith("win"):
        raise SystemError("{} not supported".format(_platform))
    args = get_args()
    logging.info("Client run...")
    loop.create_task(ws_cmd(args))
    await heartbeat_info(args)


loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
