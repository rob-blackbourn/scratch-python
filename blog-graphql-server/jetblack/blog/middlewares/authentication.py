import jwt
import logging
from cachetools import TTLCache

logger = logging.getLogger(__name__)

from ..models import (
    User,
    Permission
)


class AuthenticationMiddleware(object):

    def __init__(self, whitelist=[], maxsize=1000, ttl=60 * 60):
        self.whitelist = whitelist
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def is_whitelisted(self, path):
        for unauthenticated_path in self.whitelist:
            if path[:len(unauthenticated_path)] == unauthenticated_path:
                logger.info(f"Path is whitelisted: {path}")
                return True
        return False

    async def _get_user_and_permission(self, db, user_id):
        user, permission = self._cache.get(user_id, (None, None))
        if not (user or permission):
            logger.debug(f"Getting permissions from the database for '{user_id}'")
            user = await User.qs(db).get(user_id)
            permission = await Permission.qs(db).find_one(user={'$eq': user}) if user else None
            self._cache[user_id] = (user, permission)
        return user, permission

    async def _authenticate(self, request, config, db):

        scheme, token = request.headers['authorization'].split(' ')
        if scheme.lower() != 'bearer':
            raise Exception('invalid token')
        payload = jwt.decode(token, key=config.authentication.secret)

        if not payload['sub']:
            raise Exception('token contains no "sub"')

        user_id = payload['sub']

        return await self._get_user_and_permission(db, user_id)

    async def resolve(self, next, root, info, *args, **kwargs):
        try:
            if not ('user' in info.context or self.is_whitelisted(info.path)):
                logger.info(f"Authenticating {info.path}")
                request = info.context['request']
                config = info.context['config']
                db = info.context['mongo_db']
                user, permission = await self._authenticate(request, config, db)
                info.context['user'] = user
                info.context['permission'] = permission
        finally:
            response = await next(root, info, *args, **kwargs)
            return response
