from functools import wraps
from threading import Thread

from bson.objectid import ObjectId
from pymongo import MongoClient, errors


class DatabaseException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


def database_secure(f):
    """
    Raises DatabaseException when database is unavailable.
    """
    @wraps(f)
    def inner(*args, **kwargs):
        try:
            res = f(*args, **kwargs)
        except (errors.ServerSelectionTimeoutError, errors.PyMongoError) as e:
            raise DatabaseException(
                f"Probem with the database: {str(e)}"
            )
        return res
    return inner


def background_task(f):
    @wraps(f)
    def inner(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs)
        # TODO: change threading to something different because of GIL
        t.start()
        return t
    return inner


def get_status_updater_factory(db_url, db_name, show_logs=True):
    def inner(*args, **kwargs):
        jsp = JobStatusProvider(db_url, db_name, show_logs)
        return StatusUpdater(kwargs['job_id'], jsp)
    return inner


class JobStatusProvider:
    """
    This class serves as a frontend for job statuses.
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
            self._db_client.server_info()
            if show_logs:
                print("jsp connected to mongo")
        except (errors.ServerSelectionTimeoutError, errors.PyMongoError):
            raise DatabaseException(
                f"Could not connect to MongoDB at '{db_url}'"
            )
        self._show_logs = show_logs

    def _job_status_schema(
        self, progress: float, finished: bool = False, error: str = None, data: dict = None
    ) -> dict:
        return {
            'finished': finished,
            'progress': progress,
            'error': error,
            'data': data
        }

    @database_secure
    def create_job_status(self, data: dict = None) -> str:
        schema = self._job_status_schema(progress=0, data=data)
        new_status = self._jobs.insert_one(schema)
        return str(new_status.inserted_id)

    @database_secure
    def read_job_status(self, jid: str) -> dict:
        job_page = self._jobs.find_one({'_id': ObjectId(jid)})
        if job_page is not None:
            job_page.pop('_id', None)
        return job_page

    @database_secure
    def update_job_status(
        self, jid: str, progress: float, finished: bool = False, error: str = None
    ):
        old = self.read_job_status(jid)
        if not old:
            return
        self._jobs.update_one(
            {'_id': ObjectId(jid)}, {
                '$set': {
                    'progress': progress,
                    'finished': finished,
                    'error': error,
                    'data': old['data']
                }
            }
        )

    @database_secure
    def delete_job_status(self, jid: str):
        self._jobs.remove({'_id': ObjectId(jid)})

    @database_secure
    def job_with_data_is_running(self, data: dict) -> bool:
        # TODO: should we check with full data or only algorithm?
        docs = self._jobs.find(
            {
                'finished': False,
                'error': None
            }
        )
        if docs is None:
            return False

        for doc in docs:
            if doc and 'data' in doc and doc['data'] and 'algorithm' in doc['data']:
                if doc['data']['algorithm'] == data['algorithm']:
                    return str(doc['_id'])
        return False

    @database_secure
    def get_all_running_jobs(self):
        jobs_cursor = self._jobs.find({'finished': False}, {'data': 1, 'progress': 1, 'error': 1})
        jobs = []
        for job in jobs_cursor:
            jid = job['_id']
            job.pop('_id', None)
            job['job_id'] = str(jid)
            jobs.append(job)
        return jobs


class StatusUpdater:
    """
    This class can only update statuse.
    It is passed to AlgorithmManager, which in turn passes it to
    algorithms to enable them to update status.
    """
    def __init__(self, job_id, job_status_provider):
        self._jid = job_id
        self._jsp = job_status_provider

    def update(self, progress: float = 0, finished: bool = False, error: str = None):
        try:
            self._jsp.update_job_status(
                jid=self._jid, progress=progress, finished=finished, error=error
            )
        except Exception as e:
            print(str(e))
            return str(e)
