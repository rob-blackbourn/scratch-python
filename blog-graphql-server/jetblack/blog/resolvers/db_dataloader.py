from aiodataloader import DataLoader


class DbDataLoader(DataLoader):

    def __init__(self, db, loader):
        super().__init__()
        self.db = db
        self.loader = loader

    async def batch_load_fn(self, keys):
        return await self.loader(self.db, keys)
