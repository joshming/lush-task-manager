import strawberry

from app.graphql.mutations.project_mutation import ProjectMutation
from app.graphql.mutations.task_mutation import TaskMutation
from app.graphql.queries.project_query import ProjectQuery
from app.graphql.queries.task_query import TaskQuery


@strawberry.type
class Query(TaskQuery, ProjectQuery):
    pass


@strawberry.type
class Mutation(TaskMutation, ProjectMutation):
    pass