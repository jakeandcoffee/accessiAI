import strawberry
from strawberry.fastapi import GraphQLRouter

from app.graphql.queries import Query

schema = strawberry.Schema(query=Query)


def get_graphql_router() -> GraphQLRouter:
    return GraphQLRouter(schema)
