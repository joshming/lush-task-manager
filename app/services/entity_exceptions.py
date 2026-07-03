class WrappedException(Exception):
    code: str

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code

    pass

class TaskNotFound(WrappedException):
    def __init__(self, message: str):
        super().__init__("TASK_NOT_FOUND", message)


class ProjectNotFound(WrappedException):
    def __init__(self, message: str):
        super().__init__("PROJECT_NOT_FOUND", message)


class UserNotFound(WrappedException):
    def __init__(self, message: str):
        super().__init__("USER_NOT_FOUND", message)


class UnauthorizedTaskException(WrappedException):
    def __init__(self, message: str):
        super().__init__("UNAUTHORIZED_TASK_OPERATION", message)


class UnauthorizedProjectException(WrappedException):
    def __init__(self, message: str):
        super().__init__("UNAUTHORIZED_PROJECT_OPERATION", message)


class DuplicateProjectException(WrappedException):
    def __init__(self, message: str):
        super().__init__("DUPLICATE_PROJECT", message)


class DuplicateTaskException(WrappedException):
    def __init__(self, message: str):
        super().__init__("DUPLICATE_TASK", message)


class RefreshException(WrappedException):
    def __init__(self, message: str):
        super().__init__("STALE_DATA", message)
