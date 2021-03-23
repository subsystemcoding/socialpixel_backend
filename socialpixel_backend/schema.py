import graphene

from posts.schema import PostsQuery, PostsMutation
from users.schema import UsersQuery, AuthMutation
from chat.schema import ChatQuery, ChatMutation

from graphql_auth.schema import MeQuery


class Query(PostsQuery, UsersQuery, MeQuery, ChatQuery, graphene.ObjectType):
    # This class extends all abstract apps level Queries and graphene.ObjectType
    pass

class Mutation(AuthMutation, PostsMutation, ChatMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)