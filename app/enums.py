from enum import Enum


class TaskStatus(str, Enum):
    TODO = "To Do"
    PROGRESS = "In Progress"
    COMPLETED = "Completed"


class ProjectStatus(str, Enum):
    OPEN = "Open"
    COMPLETE = "Complete"


class Priority(int, Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3
