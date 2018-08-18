import logging
logger = logging.getLogger(__name__)

import jwt
from datetime import datetime, timedelta
from aiohttp import web
from blog_rest_api.models.users import User
from blog_rest_api.models.permissions import Permission


def verify_token(authorization, secret):
    if not authorization:
        raise Exception('no authorization header')

    scheme, token = authorization.split(' ')
    if scheme.lower() != 'bearer':
        raise Exception(f'invalid scheme {scheme} - expected "Bearer"')

    payload = jwt.decode(token, secret)
    if not payload['sub']:
        raise Exception('token contains no "sub"')

    return payload


def has_any_role(required_roles, user_roles):
    if not required_roles or len(required_roles) == 0:
        return True

    for required_role in required_roles:
        if required_role in user_roles:
            return True

    return False


class AuthController:

    def bind_routes(self, app):
        app.add_routes([
            web.post('/login', self.login),
            web.post('/register', self.register)
        ])
        return app

    async def login(self, request):

        db = request.app['db']
        auth_config = request.app['config'].authentication

        try:
            body = await request.json()

            user = await User.q(db).find_one({
                User.primary_email.s: body['email']
            })

            if not user.is_valid_password(body['password']):
                raise Exception('invalid password')

            token = self.sign(user._id, auth_config.issuer, auth_config.secret)

            return web.json_response({'token': token})

        except Exception as error:
            logger.debug(f'failed to login - {error}')
            return web.Response(status=401, text='unauthenticated')

    async def register(self, request):

        db = request.app['db']
        auth_config = request.app['config'].authentication

        try:
            body = await request.json()

            if not body['primary_email'] or not body['password']:
                raise Exception('no primary email or password')

            user = await User.create(
                db,
                primary_email=body['primary_email'],
                password=body['password'],
                secondary_emails=body['secondary_emails'],
                family_name=body['family_name'],
                given_names=body['given_names'],
                nickname=body['nickname']
            )

            await Permission.create(
                db,
                user=user,
                roles=['public:read'])

            token = self.sign(
                user._id, auth_config.issuer, auth_config.secret)

            return web.json_response({'token': token})

        except Exception as error:
            logger.debug(f'failed to login - {error}')
            return web.Response(text='unauthenticated', status=401)

    def sign(self, id, issuer, secret):
        payload = {
            'iss': issuer,
            'sub': str(id),
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, key=secret).decode()

    async def authenticate(self, request):

        db = request.app['db']
        auth_config = request.app['config'].authentication

        try:
            scheme, token = request.headers['authorization'].split(' ')
            if scheme.lower() != 'bearer':
                raise Exception('invalid token')
            payload = jwt.decode(token, key=auth_config.secret)

            if not payload['sub']:
                raise Exception('token contains no "sub"')
            request.user = await User.q(db).find_one({
                User._id.s: payload['sub']
            })
            if not request.user:
                raise Exception(f'unknown user id {payload.sub}')

            return None
        except:
            return web.Response(body='unauthorized', status=401)

    def authorise(self, application_roles, is_owner=False, owner_roles=None):

        async def authenticate_roles(request):
            try:
                if not has_any_role(application_roles, request.user.roles):
                    raise Exception('Required roles not found')

                if is_owner and not (request.user._id == request.document.user_id or has_any_role(owner_roles, request.user.roles)):
                    raise Exception('user not owner or an owner role')

                return None
            except:
                return web.Response(body='unauthorized', status=401)

        return authenticate_roles
