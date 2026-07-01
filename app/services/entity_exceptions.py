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