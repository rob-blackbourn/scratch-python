from bareasgi import Application
import bareasgi_jinja2
from easydict import EasyDict as edict
import jinja2
import pkg_resources
import yaml
from .yaml import initialize_types
from .auth_controller import AuthController
from .auth_service import AuthService
from .jwt_authentication import JwtAuthentication


def make_app(port: int) -> Application:
    initialize_types()

    with open(pkg_resources.resource_filename('jetblack_auth', 'config.yml'), 'rt') as fp:
        config = edict(yaml.load(fp))

    templates_folder = pkg_resources.resource_filename('jetblack_auth', 'templates')

    app = Application()

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates_folder),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
        enable_async=True
    )

    bareasgi_jinja2.add_jinja2(app, env)

    # cookie_name = 'jetblack-auth'
    # secret = 'trustno1'
    # token_expiry = timedelta(hours=1)
    # login_expiry = timedelta(days=1)
    # domain = 'jetblack.net'
    # auth_host = '127.0.0.1'
    # path_prefix = '/auth'
    token_renewal_path = config.path_prefix + config.token_renewal_path

    auth_service = AuthService()
    authenticator = JwtAuthentication(config.cookie_name, config.secret, config.auth_host, port, token_renewal_path)

    auth_controller = AuthController(
        config.path_prefix,
        config.cookie_name,
        config.token_expiry,
        config.login_expiry,
        config.domain,
        config.secret,
        config.auth_service,
        authenticator)

    auth_controller.add_routes(app)

    return app
