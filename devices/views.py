import json
from django.utils import timezone
from django.http import JsonResponse, Http404
from django.conf import settings
from channels.layers import get_channel_layer
from .utils import RedisClient


def token_check(func):
    async def _func(request):
        if not request.__devicename:
            return JsonResponse({'message': "forbiden"}, status=403)
        return await func(request)
    return _func


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@token_check
async def device_info(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'message': "data type error"}, status=400)
        data['time'] = timezone.localtime(
            timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
        data['name'] = request.__devicename
        data['remote_ip'] = get_client_ip(request)
        heartbeat = int(data.get('heartbeat', 30))
        token = request.__devicetoken
        async with RedisClient() as client:
            await client.set(token, json.dumps(data), expire=heartbeat + 30)
        return JsonResponse({'message': "success"})
    else:
        raise Http404()


async def device_list(request):
    data_list = []
    async with RedisClient() as client:
        for token, name in settings.AUTH_DEVICE_LIST.items():
            if data := await client.get(token, encoding='utf-8'):
                try:
                    data_list.append(json.loads(data))
                except Exception:
                    pass
    return JsonResponse({"data": data_list})


async def device_reboot(request):
    if request.method == "GET":
        if _name := request.GET.get('name'):
            for token, name in settings.AUTH_DEVICE_LIST.items():
                if name == _name:
                    layer = get_channel_layer()
                    await layer.group_send(
                        token,
                        {
                            "type": "send_cmd",
                            "cmd": "ls",
                            "test": 1,
                        }
                    )
                    return JsonResponse({'message': "success"})
    raise Http404()
