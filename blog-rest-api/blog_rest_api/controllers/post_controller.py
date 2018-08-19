from blog_rest_api.controllers.document_controller import DocumentController
from blog_rest_api.models import Post


class PostController(DocumentController):

    def __init__(self, db, config):
        super().__init__(Post, db, config)
