from databases import Database

from app.usecases.interfaces.repos.example import IExampleRepo

class ExampleRepo(IExampleRepo):
    def __init__(self, db: Database):
        self.db = db


