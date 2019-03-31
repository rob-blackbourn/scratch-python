from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    text_response,
    text_reader,
    json_response
)
from bareasgi.cookies import make_cookie
import bareasgi.header as header
from bareasgi.middleware import mw
import bareasgi_jinja2
from datetime import datetime, timedelta
import jwt
import logging
from time import mktime
from typing import Mapping, Any
from urllib.parse import parse_qs, urlparse
from .auth_service import AuthService
from .jwt_authentication import JwtAuthentication
from .__version__ import __version__

logger = logging.getLogger(__name__)


class HTTPUnauthorized(Exception):
    pass


class HTTPForbidden(Exception):
    pass


class AuthController:

    def __init__(
            self,
            path_prefix: str,
            cookie_name: str,
            token_expiry: timedelta,
            login_expiry: timedelta,
            domain: str,
            secret: str,
            auth_service: AuthService,
            authenticator: JwtAuthentication
    ) -> None:
        self.path_prefix = path_prefix
        self.cookie_name = cookie_name
        self.token_expiry = token_expiry
        self.login_expiry = login_expiry
        self.domain = domain
        self.secret = secret
        self.auth_service = auth_service
        self.authenticator = authenticator

    def add_routes(self, app: Application) -> Application:
        app.http_router.add({'GET'}, self.path_prefix + '/login', self.login_view)
        app.http_router.add({'POST'}, self.path_prefix + '/authenticate', self.login_post)
        app.http_router.add({'POST'}, self.path_prefix + '/renew_token', self.renew_token)

        app.http_router.add(
            {'GET'},
            self.path_prefix + '/whoami',
            mw(self.authenticator.jwt_authenticate, handler=self.who_am_i))

        return app

    @bareasgi_jinja2.template('login.html')
    async def login_view(self, scope: Scope, info: Info, matches: RouteMatches, content: Content) -> Mapping[str, Any]:
        action = f'{self.path_prefix}/authenticate?{scope["query_string"].decode()}'
        return {
            'action': action,
            'version': __version__
        }

    async def login_post(self, scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
        try:
            query = parse_qs(scope['query_string'])
            redirect = query.get(b'redirect')
            if not redirect:
                logger.debug('No redirect')
                return text_response(404, [], 'No redirect')
            redirect = redirect[0]

            text = await text_reader(content)
            body = parse_qs(text)
            username = body['username'][0]
            password = body['password'][0]

            if not self.auth_service.is_password_for_user(username, password):
                raise RuntimeError('Invalid username or password')

            now = datetime.utcnow()
            token = self._make_token(body['username'], now, issued_at=int(mktime(now.timetuple())))

            logger.debug(f'Sending token: {token}')
            urlparts = urlparse(redirect)
            if urlparts.scheme is None or len(urlparts.scheme) == 0:
                raise RuntimeError('The redirect URL has no scheme')

            set_cookie = self._make_cookie(token)

            return 302, [(b'set-cookie', set_cookie), (b'location', redirect)], None

        except:
            logger.exception('Failed to log in')
            return 302, [(b'location', header.find(b'referer', scope['headers']))], None

    async def who_am_i(self, scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
        try:
            token = header.cookie((scope['headers'])).get(self.cookie_name)
            if token is None:
                return text_response(401, [], 'Client requires authentication')

            payload = jwt.decode(token, key=self.secret)

            return json_response(200, [], {'username': payload['sub']})
        except (jwt.exceptions.ExpiredSignature, PermissionError) as error:
            logger.debug(f'JWT encoding failed: {error}')
            return 401, None, None
        except:
            logger.exception(f'Failed to re-sign the token')
            return 500, None, None

    async def renew_token(self, scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
        try:
            token = header.cookie(scope['headers']).get(self.cookie_name)
            if not token:
                # Unauthorised
                return text_response(401, [], 'Client requires authentication')

            payload = jwt.decode(token, key=self.secret, options={'verify_exp': False})

            user = payload['sub']
            issued_at = datetime.utcfromtimestamp(payload['iat'])

            logger.debug(f'Token renewal request: user={user}, iat={issued_at}')

            utc_now = datetime.utcnow()

            authentication_expiry = issued_at + self.login_expiry
            if utc_now > authentication_expiry:
                # Unauthenticated
                logger.debug(f'Token expired for user {user} issued at {issued_at} expired at {authentication_expiry}')
                return text_response(401, [], 'Authentication expired')

            if not self.auth_service.is_valid(user):
                return 403, None, None  # Forbidden

            logger.debug(f'Token renewed for {user}')
            token = self._make_token(user, utc_now, issued_at=issued_at)
            logger.debug(f'Sending token {token}')

            set_cookie = self._make_cookie(token)

            return 204, [(b'set-cookie', set_cookie)], None

        except:
            return 500, None, None

    def _make_cookie(self, token: str) -> bytes:
        return make_cookie(
            self.cookie_name,
            token,
            max_age=int(self.login_expiry.total_seconds()),
            domain=self.domain
        )

    def _make_token(self, username: str, now: datetime, issued_at=None):
        return self._sign(username, now, issued_at=issued_at)

    def _sign(self, username, now, **kwargs):
        expiry = now + self.token_expiry
        logger.info(f'Token will expiry at {expiry}')
        payload = {
            'iss': self.domain,
            'sub': username,
            'exp': int(mktime(expiry.timetuple()))
        }
        for key, value in kwargs.items():
            payload[key] = value
        return jwt.encode(payload, key=self.secret).decode()
