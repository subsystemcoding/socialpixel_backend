import graphene

from posts.schema import PostsQuery, PostsMutation
from users.schema import UsersQuery, AuthMutation
from chat.schema import ChatQuery, ChatMutation
from game.schema import ChannelMutation, ChannelQuery, GameMutation, GameQuery

from graphql_auth.schema import MeQuery


class Query(PostsQuery, UsersQuery, MeQuery, ChatQuery, ChannelQuery, GameQuery, graphene.ObjectType):
    # This class extends all abstract apps level Queries and graphene.ObjectType
    pass

class Mutation(AuthMutation, PostsMutation, ChatMutation, ChannelMutation, GameMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)