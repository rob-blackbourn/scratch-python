from bareasgi import (
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    HttpRequestCallback,
    Header
)
from bareasgi.cookies import make_cookie
import bareasgi.header as header
from bareclient import HttpClient
from calendar import timegm
from datetime import datetime
import http.cookies
import jwt
import logging
import ssl
from typing import Mapping, Any, Optional, List

logger = logging.getLogger(__name__)


class HTTPUnauthorised(Exception):
    pass


class JwtAuthentication:

    def __init__(
            self,
            cookie_name: str,
            secret: str,
            auth_host: str,
            auth_port: int,
            token_renewal_path: str
    ) -> None:
        self.cookie_name = cookie_name
        self.secret = secret
        self.auth_host = auth_host
        self.auth_port = auth_port
        self.token_renewal_path = token_renewal_path

    async def _renew_cookie(self, scope: Scope) -> http.cookies.Morsel:

        scheme = scope["scheme"]
        server_host, server_port = scope['server']

        headers = [(k, v) for k, v in scope['headers'] if k == b'cookie']

        renewal_url = f'{scheme}://{self.auth_host}:{self.auth_port}{self.token_renewal_path}'
        url = f'{scheme}://{server_host}:{server_port}{scope["path"]}'
        referer = header.find(b'referer', scope['headers'], url.encode('ascii'))

        headers.extend(
            [
                (b'host', self.auth_host.encode('ascii')),
                (b'referer', referer),
                (b'content-length', b'0'),
                (b'connection', b'close')
            ]
        )

        ssl_context = ssl.SSLContext() if scheme == 'https' else None

        async with HttpClient(renewal_url, method='POST', headers=headers, ssl=ssl_context) as (response, body):

            logger.debug(f'Renew cookie: {renewal_url}')

            if response.status_code == 200:
                logger.debug('Cookie renewed')
                return self._extract_cookie(response.headers)
            elif response.status_code == 401:
                logger.debug('Cookie not renewed - client requires authentication')
                raise HTTPUnauthorised('Client requires authentication')
            else:
                logger.debug('Cookie not renewed - client authentication failed')
                raise Exception('Client authentication failed')

    def _extract_cookie(self, headers: List[Header]) -> http.cookies.Morsel:
        set_cookies = header.find_all(b'set-cookie', headers)
        set_cookies_by_name = [(v.split(b'=', maxsplit=1)[0], v) for k, v in set_cookies]
        response_cookies = {
            k.decode(): v.decode()
            for k, v in set_cookies_by_name
        }
        simple_cookie = http.cookies.SimpleCookie[response_cookies[self.cookie_name]]
        return simple_cookie[self.cookie_name]

    def _decode_jwt(self, token: bytes) -> Optional[Mapping[str, Any]]:
        if not token:
            logger.debug(f'No token named "{self.cookie_name}"')
            return None
        return jwt.decode(token.decode('ascii'), key=self.secret, options={'verify_exp': False})

    @classmethod
    def _should_renew_token(cls, payload: Mapping[str, Any]) -> bool:
        now = timegm(datetime.utcnow().utctimetuple())
        return now > payload['exp']

    async def jwt_authenticate(
            self,
            scope: Scope,
            info: Info,
            matches: RouteMatches,
            content: Content,
            handler: HttpRequestCallback
    ) -> HttpResponse:
        logger.debug(f'JWT Authentication Reqeust: {scope["path"]}')

        # noinspection PyBroadException
        try:
            token = header.cookie(scope['headers']).get(self.cookie_name.encode('ascii'))
            payload = self._decode_jwt(token)
            if payload is None or self._should_renew_token(payload):
                logger.debug('Renewing cookie')
                cookie = await self._renew_cookie(scope)
                payload = self._decode_jwt(cookie.value)
            else:
                logger.debug('Cookie still valid')
                cookie = None

            if info is None:
                info = dict()
            info['jwt'] = payload

            response_status, response_headers, response_content = await handler(scope, info, matches, content)

            if cookie:
                set_cookie = make_cookie(
                    self.cookie_name,
                    cookie.value,
                    max_age=int(cookie['max-age']),
                    domain=cookie['domain'],
                    httponly=True
                )
                if response_headers is None:
                    response_headers = list()
                response_headers.append((b'set-cookie', set_cookie))

            return response_status, response_headers, response_content

        except HTTPUnauthorised:
            logger.debug('Unauthorised')
            return 401, None, None
        except Exception:
            logger.exception('JWT authentication failed')
            return 500, None, None
