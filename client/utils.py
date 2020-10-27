import asyncio
import psutil
import socket
import websockets
import json
import logging
import aiohttp

logger = logging.getLogger(__name__)


def get_info():
    """
    device info
    """
    return {
        "cpu_count": psutil.cpu_count(),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_size": round(
            psutil.virtual_memory().total / 1024 / 1024 / 1024, 2),
        "disk_percent": psutil.disk_usage('/').percent,
        "disk_size": round(
            psutil.disk_usage('/').total / 1024 / 1024 / 1024, 2),
        "ip_list": [
            [eth, addr.address]
            for eth, addrs in psutil.net_if_addrs().items()
            for addr in addrs
        ]
    }


async def get_ip():
    """
    get query ip
    """
    local_ip = None
    while not local_ip:
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
        except Exception:
            await asyncio.sleep(30)
    return local_ip


async def run_cmd(cmd) -> (bool, str):
    """
    exec system cmd
    """
    if cmd in ['reboot', 'ls']:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if stdout:
            return True, stdout.decode()
        elif stderr:
            return False, stderr.decode()
    return False, "cmd error"


async def ws_cmd(args):
    """
    recv ws server cmd
    """
    url = "ws://{}:{}/ws/device/".format(
        args.server, args.port)
    headers = {'devicetoken': args.token}
    while True:
        try:
            async with websockets.connect(
                    url, extra_headers=headers) as websocket:
                logger.info("ws server connected...")
                try:
                    while True:
                        data = await websocket.recv()
                        data = json.loads(data)

                        if data['type'] == 'cmd':
                            status, msg = await run_cmd(data['cmd'])
                            logging.info("result: {}".format(msg))
                            await websocket.send(json.dumps({
                                "type": "cmd",
                                "msg": msg,
                            }))
                except Exception:
                    logger.exception("{} error".format(data))
        except Exception:
            await asyncio.sleep(args.retval)
        logger.info("retry connected...")


async def heartbeat_info(args):
    """
    send info to server
    """
    url = "http://{}:{}/device/info/".format(args.server, args.port)
    local_ip = await get_ip()
    headers = {'devicetoken': args.token}
    try:
        while True:
            data = get_info()
            data['local_ip'] = local_ip
            data['heartbeat'] = args.heartbeat
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                            url, json=data, headers=headers) as resp:
                        ret = await resp.json()
                        logging.info("result: {}".format(ret))
            except Exception:
                logger.exception("request error")
            await asyncio.sleep(args.heartbeat)
    except Exception:
        await asyncio.sleep(args.retval)
