from blog_rest_api.controllers import AuthController, UserController, PostController, CommentController


def configure_auth_controller(app, db, config):
    auth_controller = AuthController(db, config)
    auth_app = auth_controller.create_app()
    app.add_subapp('/admin', auth_app)
    return auth_controller


def configure_document_controller(app, db, authenticate, authorise, controller, name, other_read_roles=[], other_write_roles=[], read_is_owner=False, write_is_owner=False):

    read_authorise = authorise(
        all_roles=[name + ':read'] + other_read_roles,
        is_owner=read_is_owner)

    write_authorise = authorise(
        all_roles=[name + ':write'] + other_write_roles,
        is_owner=write_is_owner)

    document_app = controller.create_app(
        authenticate,
        read_authorise,
        write_authorise)

    app.add_subapp('/' + name, document_app)

    return controller


def configure_user_controller(app, db, config, authenticate, authorise):
    controller = UserController(db, config)
    return configure_document_controller(app, db, authenticate, authorise, controller, "user")


def configure_post_controller(app, db, config, authenticate, authorise):
    controller = PostController(db, config)
    return configure_document_controller(app, db, authenticate, authorise, controller, "post", write_is_owner=True)


def configure_comment_controller(app, db, config, authenticate, authorise):
    controller = CommentController(db, config)
    return configure_document_controller(app, db, authenticate, authorise, controller, "comment", other_read_roles=['post:read'], write_is_owner=True)


def configure_controllers(app, db, config):
    auth = configure_auth_controller(app, db, config)
    configure_user_controller(
        app, db, config, auth.authenticate, auth.authorise)
    configure_post_controller(
        app, db, config, auth.authenticate, auth.authorise)
    configure_comment_controller(
        app, db, config, auth.authenticate, auth.authorise)
