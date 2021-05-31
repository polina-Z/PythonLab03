from enum import Enum
from uuid import uuid4
import datetime


class Task:
    def __init__(self, id=None, title=None, finish=None, priority=None, status=None, information=None, user_creator=None):
        self.id = id if id is not None else str(uuid4().hex)[-5:]
        self.title = title if title is not None else " "
        self.pub_date = datetime.datetime.now()
        self.finish = finish
        self.priority = priority if priority is not None else Priority.NORMAL
        self.status = status if status is not None else Status.ACTIVE
        self.information = information if information is not None else " "
        self.user_creator = user_creator if user_creator is not None else "admin"


class Status(Enum):
    ACTIVE = 2
    FINISHED = 1
    FAILED = 0

    def __str__(self):
        return str(self.name).lower()


class Priority(Enum):
    HIGH = 2
    NORMAL = 1
    LOW = 0

    def __str__(self):
        return str(self.name).lower()


class OperationType(Enum):
    READ = 0
    FINISH = 1
    EDIT = 2
    REMOVE = 3

    def __str__(self):
        return str(self.name).lower()
