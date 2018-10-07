import logging

logger = logging.getLogger(__name__)


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


def authorize(*, any_role=[], all_roles=[], is_owner=False, owner_roles=None):
    def authenticate_roles(user, permission, owner=None):
        if not has_any_role(any_role, permission.roles):
            logger.debug(f"The user did not have any required role: user='{user}', any_role={any_role}")
            return False

        if not has_all_roles(all_roles, permission.roles):
            logger.debug("All required roles not found")

        if is_owner and not (
                user == owner or has_any_role(owner_roles, permission.roles)):
            logger.debug("user not owner or an owner role")

        return True

    return authenticate_roles
