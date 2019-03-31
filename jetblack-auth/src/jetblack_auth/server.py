from bareasgi import Application
import bareasgi_jinja2
from datetime import timedelta
import jinja2
import pkg_resources
from .auth_controller import AuthController
from .auth_service import AuthService
from .jwt_authentication import JwtAuthentication


def make_app(port: int) -> Application:
    templates_folder = pkg_resources.resource_filename('jetblack_auth', 'templates')

    app = Application()

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates_folder),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
        enable_async=True
    )

    bareasgi_jinja2.add_jinja2(app, env)

    cookie_name = 'jetblack-auth'
    secret = 'trustno1'
    token_expiry = timedelta(hours=1)
    login_expiry = timedelta(days=1)
    domain = 'jetblack.net'
    auth_host = '127.0.0.1'
    path_prefix = '/auth'
    token_renewal_path = path_prefix + '/renew_token'

    auth_service = AuthService()
    authenticator = JwtAuthentication(cookie_name, secret, auth_host, port, token_renewal_path)

    auth_controller = AuthController(
        path_prefix,
        cookie_name,
        token_expiry,
        login_expiry,
        domain,
        secret,
        auth_service,
        authenticator)

    auth_controller.add_routes(app)

    return app
