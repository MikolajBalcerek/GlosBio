from functools import wraps
from threading import Thread

from bson.objectid import ObjectId
from pymongo import MongoClient, errors


class DatabaseException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        # self.__str__ = mongo_error.__str__


def database_secure(f):
    """
    Raises DatabaseException when database is unavailable.
    """
    @wraps(f)
    def inner(*args, **kwargs):
        try:
            res = f(*args, **kwargs)
        except errors.ServerSelectionTimeoutError:
            raise DatabaseException(
                f"Could not connect to MongoDB."
            )
        return res
    return inner


def background_task(f):
    @wraps(f)
    def inner(*args, **kwargs):
        Thread(target=f, args=args, kwargs=kwargs).start()
    return inner


def job_status_provider_factory(db_url, db_name):
    def inner(*args, **kwargs):
        return JobStatusProvider(db_url, db_name)
    return inner


class JobStatusProvider:
    """
    """

    def __init__(self, db_url: str, db_name: str, show_logs: bool = True):
        """
        :param db_url: str - url to MongoDB database, it can contain port eg: 'localhost:27017'
        :param db_name: str - database name
        :param show_logs: bool - used to suppress log messages
        """
        self._db_url = db_url
        self._db_client = MongoClient(db_url, serverSelectionTimeoutMS=5000)
        self._database = self._db_client[db_name]
        self._jobs = self._database.jobs
        try:
            if show_logs:
                print(f" * #INFO: testing db connection: '{db_url}'...")
            self._db_client.server_info()
        except errors.ServerSelectionTimeoutError:
            raise DatabaseException(
                f"Could not connect to MongoDB at '{db_url}'"
            )
        self.show_logs = show_logs

    def _job_status_schema(
        self, progress: float, finished: bool = False, error: str = None
    ) -> dict:
        return {
            'finished': finished,
            'progress': progress,
            'error': error
        }

    @database_secure
    def create_job_status(self) -> str:
        new_status = self._jobs.insert_one(
            self._job_status_schema(progress=0)
        )
        return str(new_status.inserted_id)

    @database_secure
    def read_job_status(self, jid: str) -> dict:
        job_page = self._jobs.find_one({'_id': ObjectId(jid)})
        job_page.pop('_id', None)
        return job_page

    @database_secure
    def update_job_status(
        self, jid: str, progress: float, finished: bool = False, error: str = None
    ):
        self._jobs.replace_one(
            {'_id': ObjectId(jid)},
            self._job_status_schema(progress, finished, error)
        )

    @database_secure
    def delete_job_status(self, jid: str):
        self._jobs.remove({'_id': jid})
