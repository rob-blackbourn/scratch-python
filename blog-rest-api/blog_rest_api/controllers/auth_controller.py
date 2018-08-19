import logging
logger = logging.getLogger(__name__)

import jwt
from datetime import datetime, timedelta
from bson import ObjectId
from aiohttp import web
from blog_rest_api.models.users import User
from blog_rest_api.models.permissions import Permission


def has_any_role(required_roles, user_roles):
    if not required_roles or len(required_roles) == 0:
        return True

    for required_role in required_roles:
        if required_role in user_roles:
            return True

    return False


def has_all_roles(required_roles, user_roles):
    if not required_roles or len(required_roles) == 0:
        return True

    for required_role in required_roles:
        if required_role not in user_roles:
            return False

    return True


class AuthController:

    def __init__(self, db, config):
        self.db = db
        self.config = config

    def create_app(self):
        admin = web.Application()

        admin.add_routes([
            web.post('/login', self.login),
            web.post('/register', self.register)
        ])

        return admin

    async def login(self, request):

        try:
            body = await request.json()

            user = await User.q(self.db).find_one({
                User.primary_email.s: body['email']
            })

            if not user.is_valid_password(body['password']):
                raise Exception('invalid password')

            token = self.sign(user._id)

            return web.json_response({'token': token})

        except Exception as error:
            logger.debug(f'failed to login - {error}')
            return web.Response(status=401, text='unauthenticated')

    async def register(self, request):

        try:
            body = await request.json()

            if not body['primary_email'] or not body['password']:
                raise Exception('no primary email or password')

            user = await User.create(
                self.db,
                primary_email=body['primary_email'],
                password=body['password'],
                secondary_emails=body['secondary_emails'],
                family_name=body['family_name'],
                given_names=body['given_names'],
                nickname=body['nickname']
            )

            await Permission.create(
                self.db,
                user=user,
                roles=self.config.authorization.default_roles)

            token = self.sign(user._id)

            return web.json_response({'token': token})

        except Exception as error:
            logger.debug(f'failed to login - {error}')
            return web.Response(text='unauthenticated', status=401)

    def sign(self, id):
        payload = {
            'iss': self.config.authentication.issuer,
            'sub': str(id),
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, key=self.config.authentication.secret).decode()

    @web.middleware
    async def authenticate(self, request, handler):

        try:
            scheme, token = request.headers['authorization'].split(' ')
            if scheme.lower() != 'bearer':
                raise Exception('invalid token')
            payload = jwt.decode(token, key=self.config.authentication.secret)

            if not payload['sub']:
                raise Exception('token contains no "sub"')
            user_id = ObjectId(payload['sub'])
            request.user = await User.q(self.db).get(user_id)
            request.permission = await Permission.q(self.db).find_one({
                Permission.user.s: user_id
            })

            response = await handler(request)

            return response
        except Exception as error:
            logger.debug(f"Failed to authenticate - {error}")
            return web.Response(body='unauthorized', status=401)

    def authorise(self, *, any_role=[], all_roles=[], is_owner=False, owner_roles=None):

        @web.middleware
        async def authenticate_roles(request, handler):
            try:
                if not has_any_role(any_role, request.permission.roles):
                    raise Exception('Required roles not found')

                if not has_all_roles(all_roles, request.permission.roles):
                    raise Exception('Required roles not found')

                if is_owner and not (request.user == request.document.user or has_any_role(owner_roles, request.user.roles)):
                    raise Exception('user not owner or an owner role')

                return await handler(request)
            except Exception as error:
                logger.debug(f"Failed to authorize - {error}")
                return web.Response(body='unauthorized', status=401)

        return authenticate_roles
