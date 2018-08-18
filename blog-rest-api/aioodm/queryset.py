"""QuerySet classes."""
import functools
import sys
import textwrap

import pymongo.errors

from aioodm.errors import DocumentNotFoundError, DuplicateKeyError


PY_36 = sys.version_info >= (3, 6)


class MotorQuerySet(object):
    """QuerySet based on Motor query syntax."""

    def __init__(self, doc_class, db):
        self.doc_class = doc_class
        self.db = db
        self.default_query = doc_class.meta.default_query
        self.default_sort = doc_class.meta.default_sort
        self.collection = self.doc_class.meta.collection(self.db)

    def _update_query(self, query):
        """Update query with default_query if any."""
        return (query
                if not self.default_query
                else {'$and': [self.default_query, query]})

    def clone(self):
        """Return a copy of queryset."""
        qs = type(self)(self.doc_class, self.db)
        qs.default_query = self.default_query
        qs.collection = self.collection
        return qs

    async def create(self, **kwargs):
        """Create document."""
        return await self.doc_class.create(self.db, **kwargs)

    async def create_indexes(self):
        """Create document's indexes defined in Meta class."""
        if self.doc_class.meta.indexes:
            await self.collection.create_indexes(self.doc_class.meta.indexes)

    async def delete_one(self, query, **kwargs):
        """Delete one document."""
        res = await self.collection.delete_one(
            self._update_query(query), **kwargs)
        return res.deleted_count if res.acknowledged else None

    async def delete_many(self, query, **kwargs):
        """Delete many documents."""
        res = await self.collection.delete_many(
            self._update_query(query), **kwargs)
        return res.deleted_count if res.acknowledged else None

    async def replace_one(self, query, *args, **kwargs):
        """Replace one document.

        Returns:
            int: Number of modified documents.

        Raises:
            aioodm.errors.DuplicateKeyError: On duplicate key error.
        """
        try:
            res = await self.collection.replace_one(
                self._update_query(query), *args, **kwargs)
        except pymongo.errors.DuplicateKeyError as e:
            raise DuplicateKeyError(str(e)) from e
        return res.modified_count if res.acknowledged else None

    async def update_one(self, query, *args, **kwargs):
        """Update one document.

        Returns:
            int: Number of modified documents.

        Raises:
            aioodm.errors.DuplicateKeyError: On duplicate key error.
        """
        try:
            res = await self.collection.update_one(
                self._update_query(query), *args, **kwargs)
        except pymongo.errors.DuplicateKeyError as e:
            raise DuplicateKeyError(str(e)) from e
        return res.modified_count if res.acknowledged else None

    async def update_many(self, query, *args, **kwargs):
        """Update many documents.

        Returns:
            int: Number of modified documents.

        Raises:
            aioodm.errors.DuplicateKeyError: On duplicate key error.
        """
        try:
            res = await self.collection.update_many(
                self._update_query(query), *args, **kwargs)
        except pymongo.errors.DuplicateKeyError as e:
            raise DuplicateKeyError(str(e)) from e
        return res.modified_count if res.acknowledged else None

    async def insert_one(self, *args, **kwargs):
        """Insert one document.

        Returns:
            Inserted ``_id`` value.

        Raises:
            aioodm.errors.DuplicateKeyError: On duplicate key error.
        """
        try:
            res = await self.collection.insert_one(*args, **kwargs)
        except pymongo.errors.DuplicateKeyError as e:
            raise DuplicateKeyError(str(e)) from e
        return res.inserted_id if res.acknowledged else None

    async def insert_many(self, *args, **kwargs):
        """Insert many documents.

        Returns:
            list: List of inserted ``_id`` values.
        """
        res = await self.collection.insert_many(*args, **kwargs)
        return res.inserted_ids if res.acknowledged else None

    async def find_one(self, query={}, *args, **kwargs):
        """Find one document.

        Arguments are the same as for ``motor.Collection.find_one``.
        This method does not returns ``None`` if there is no documents for
        given query but raises ``aioodm.errors.DocumentNotFoundError``.

        Returns:
            Document model instance.

        Raises:
            aioodm.errors.DocumentNotFoundError: If there is no documents
                for given query.
        """
        data = await self.collection.find_one(
            self._update_query(query), *args, **kwargs)
        if data is None:
            raise DocumentNotFoundError()

        return self.doc_class.from_mongo(data)

    async def get(self, _id, *args, **kwargs):
        """Get document by its _id."""
        return await self.find_one(
            {'_id': self.doc_class._id.to_mongo(_id)}, *args, **kwargs)

    def find(self, query={}, *args, sort=None, **kwargs):
        """Find documents by query.

        Returns:
            MotorQuerySetCursor: Cursor to get actual data.
        """
        if not sort and self.default_sort:
            sort = self.default_sort
        return MotorQuerySetCursor(
            self.doc_class,
            self.collection.find(self._update_query(query),
                                 *args, sort=sort, **kwargs))

    async def count(self, query={}, **kwargs):
        """Count documents in collection."""
        return await self.collection.count(
            self._update_query(query), **kwargs)

    def aggregate(self, pipeline, **kwargs):
        """Return Aggregation cursor."""
        if not self.default_query:
            return self.collection.aggregate(pipeline, **kwargs)

        try:
            match = pipeline[0]['$match']
        except KeyError:
            return self.collection.aggregate(
                [{'$match': self.default_query}] + pipeline, **kwargs)
        else:
            pipeline[0]['$match'] = self._update_query(match)
            return self.collection.aggregate(pipeline, **kwargs)

    def with_options(self, **kwargs):
        """Change collection options."""
        clone = self.clone()
        clone.collection = self.collection.with_options(**kwargs)
        return clone


class MotorQuerySetCursor(object):
    """Cursor based on motor cursor."""

    DIRECT_TO_MOTOR = {'distinct', 'explain', 'count'}

    def __init__(self, doc_class, cursor):
        self.doc_class = doc_class
        self.cursor = cursor

    def _proxy_to_motor_cursor(self, method, *args, **kwargs):
        getattr(self.cursor, method)(*args, *kwargs)
        return self

    async def to_list(self, length):
        """Return list of documents.

        Args:
            length: Number of items to return.

        Returns:
            list: List of document model isinstances.
        """
        data = await self.cursor.to_list(length)
        return [self.doc_class.from_mongo(item) for item in data]

    def clone(self):
        """Get copy of this cursor."""
        return self.__class__(self.doc_class, self.cursor.clone())

    if PY_36:
        # for python >= 3.6 implement __aiter__ as async generator
        exec(textwrap.dedent("""
        async def __aiter__(self):
            return (self.doc_class.from_mongo(item)
                    async for item in self.cursor)
        """), globals(), locals())
    else:
        # for python < 3.6 implement __aiter__ as async iterator
        exec(textwrap.dedent("""
        def __aiter__(self):
            return self

        async def __anext__(self):
            return self.doc_class.from_mongo(await self.cursor.__anext__())
        """), globals(), locals())

    def __getattr__(self, name):
        if name in self.DIRECT_TO_MOTOR:
            return getattr(self.cursor, name)

        return functools.partial(self._proxy_to_motor_cursor, name)
