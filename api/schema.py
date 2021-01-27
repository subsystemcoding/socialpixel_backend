import graphene
from graphene_django import DjangoObjectType

from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations as gqlAuthMutations

from graphql_jwt.decorators import login_required



from posts.models import Post, Comment
from users.models import User

class AuthMutation(graphene.ObjectType):
    register = gqlAuthMutations.Register.Field()
    verify_account = gqlAuthMutations.VerifyAccount.Field()
    resend_activation_email = gqlAuthMutations.ResendActivationEmail.Field()
    send_password_reset_email = gqlAuthMutations.SendPasswordResetEmail.Field()
    password_reset = gqlAuthMutations.PasswordReset.Field()
    password_set = gqlAuthMutations.PasswordSet.Field() # For passwordless registration
    password_change = gqlAuthMutations.PasswordChange.Field()
    update_account = gqlAuthMutations.UpdateAccount.Field()
    archive_account = gqlAuthMutations.ArchiveAccount.Field()
    delete_account = gqlAuthMutations.DeleteAccount.Field()
    send_secondary_email_activation =  gqlAuthMutations.SendSecondaryEmailActivation.Field()
    verify_secondary_email = gqlAuthMutations.VerifySecondaryEmail.Field()
    swap_emails = gqlAuthMutations.SwapEmails.Field()
    remove_secondary_email = gqlAuthMutations.RemoveSecondaryEmail.Field()

    # django-graphql-jwt inheritances
    token_auth = gqlAuthMutations.ObtainJSONWebToken.Field()
    verify_token = gqlAuthMutations.VerifyToken.Field()
    refresh_token = gqlAuthMutations.RefreshToken.Field()
    revoke_token = gqlAuthMutations.RevokeToken.Field()


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        # fields = (
        #     "post_id", "author", "date_created", 
        #     "caption", "gps_tag", "tagged_users",
        #     "upvotes", "views", "visibility", "media_id"
        # )
        fields = "__all__"

class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        # fields = (
        #     "comment_id", "post_id", "author",
        #     "comment_content", "reply_to_comment", "date_created"
        # )
        fields = "__all__"

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = (
            "username", "email",
            "first_name", "last_name",
            "date_joined"
        )

class Query(UserQuery, MeQuery, graphene.ObjectType):
    posts = graphene.List(PostType)
    comments = graphene.List(CommentType)
    users = graphene.List(UserType)

    def resolve_posts(root, info):
        return Post.objects.all()
    
    def resolve_comments(root, info):
        return Comment.objects.all()

    @login_required
    def resolve_users(root, info):
        return User.objects.all()

class Mutation(AuthMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
