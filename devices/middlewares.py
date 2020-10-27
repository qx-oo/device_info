import asyncio
from django.conf import settings
from django.utils.decorators import sync_and_async_middleware
from channels.auth import AuthMiddlewareStack


@sync_and_async_middleware
def token_config(get_response):
    def set_request(request):
        token = request.META.get('HTTP_DEVICETOKEN')
        name = settings.AUTH_DEVICE_LIST.get(token)
        setattr(request, "__devicename", name)
        setattr(request, "__devicetoken", token)
    if asyncio.iscoroutinefunction(get_response):
        async def middleware(request):
            set_request(request)
            response = await get_response(request)
            return response
    else:
        def middleware(request):
            set_request(request)
            response = get_response(request)
            return response
    return middleware


class TokenAuthMiddleware:
    """
    Token Set
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        headers = dict(scope['headers'])
        name = None
        token = None
        if b'devicetoken' in headers:
            try:
                token = headers[b'devicetoken'].decode()
                name = settings.AUTH_DEVICE_LIST.get(token)
            except Exception:
                pass
        scope['__devicename'] = name
        scope['__devicetoken'] = token
        return self.inner(scope)


def TokenAuthMiddlewareStack(inner): return TokenAuthMiddleware(
    AuthMiddlewareStack(inner))
