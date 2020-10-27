import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer


logger = logging.getLogger(__name__)


class DeviceConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.__token = self.scope['__devicetoken']
        self.__name = self.scope['__devicename']
        logger.info("connect: {}, {}".format(
            self.__token, self.channel_name))
        if not self.scope['__devicename']:
            await self.close()
        else:
            await self.channel_layer.group_add(
                self.__token, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        logger.info("disconnect: {}, {}".format(
            self.__token, self.channel_name))
        if self.__name:
            await self.channel_layer.group_discard(
                self.__token, self.channel_name)

    async def send_cmd(self, event):
        cmd = event['cmd']
        logger.info("send cmd: {}, {}".format(self.__name, cmd))
        await self.send_json({
            'type': "cmd",
            'cmd': cmd,
        })

    async def query_info(self, data):
        """
        query device info
        """
        logger.debug('send msg: {}'.format(data))
        data['recv'] = True
        await self.send_json(data)
