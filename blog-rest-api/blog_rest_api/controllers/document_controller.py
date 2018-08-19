import logging
logger = logging.getLogger(__name__)
import json
from aiohttp import web
from blog_rest_api.utils import UrlDispatcherEx
from blog_rest_api.utils.json import JsonEncoderEx


class DocumentController:

    def __init__(self, model, db, config):
        self.model = model
        self.db = db
        self.config = config

    def create_app(self, authenticator, read_auth, write_auth):

        app = web.Application(router=UrlDispatcherEx(),
                              middlewares=[authenticator])

        app.router.add_get(
            '/',
            read_auth,
            self.read_many)

        app.router.add_post(
            '/',
            read_auth,
            write_auth,
            self.create_one)

        app.router.add_get(
            '/{id}',
            read_auth,
            self.resolve,
            self.read_one)

        app.router.add_patch(
            '/{id}',
            read_auth,
            self.resolve,
            write_auth,
            self.read_one)

        app.router.add_delete(
            '/{id}',
            read_auth,
            self.resolve,
            write_auth,
            self.delete_one)

        return app

    def document_response(self, document, *, status=200):
        text = json.dumps(document.to_data(), cls=JsonEncoderEx)
        return web.Response(text=text, status=status, content_type='application/json')

    def documents_response(self, documents, *, status=200):
        text = json.dumps([document.to_data()
                           for document in documents], cls=JsonEncoderEx)
        return web.Response(
            text=text,
            content_type='application/json',
            status=status)

    async def create_one(self, request):

        try:
            body = await request.json()
            document = await self.model.create(self.db, **body)
            return self.document_response(document, status=201)
        except Exception as error:
            logger.debug(f"Failed to create document - {error}")
            return web.Response(text="failed to create document", status=500)

    # Depends on resolveDocument middleware
    async def read_one(self, request):
        return web.json_response(request.document)

    async def read_many(self, request):

        try:
            cursor = self.model.q(self.db).find(request.query.copy())
            documents = [document async for document in cursor]
            return self.documents_response(documents)
        except Exception as error:
            logger.debug(f"Failed to read many - {error}")
            return web.Response(text="failed to read documents", status=500)

    # Depends on resolveDocument middleware
    async def update_one(self, request):

        try:
            body = await request.json()

            if '_id' in body:
                del body['_id']

            for key, value in body.items():
                setattr(request.document, key, value)

            document = await request.document.save(self.db)

            return self.document_response(document)
        except Exception as error:
            logger.debug(f"Failed to update document - {error}")
            return web.Response(text="failed to update document", status=500)

    async def delete_one(self, request):

        try:
            await request.document.delete(self.db)
            return web.Response(status=204, text='removed')
        except Exception as error:
            logger.debug(f"Failed to delete document - {error}")
            return web.Response(text="failed to delete document", status=500)

    @web.middleware
    async def resolve(self, request, handler):

        try:
            request.document = await self.model.q(self.db).get(request.match_info['id'])
            if not request.document:
                return web.Response(status=404, text='document not found')

            return await handler(request)

        except Exception as error:
            logger.debug(f"Failed to resolve document - {error}")
            return web.Response(text="failed to resolve document", status=500)
