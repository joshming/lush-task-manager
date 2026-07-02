class NotFoundException(Exception):
    pass


class TaskNotFound(NotFoundException):
    pass


class ProjectNotFound(NotFoundException):
    pass


class UserNotFound(NotFoundException):
    pass


class UnauthorizedException(Exception):
    pass


class UnauthorizedTaskException(UnauthorizedException):
    pass


class UnauthorizedProjectException(UnauthorizedException):
    pass


class DuplicateException(Exception):
    pass


class DuplicateProjectException(DuplicateException):
    pass


class DuplicateTaskException(DuplicateException):
    pass


class RefreshException(Exception):
    pass
