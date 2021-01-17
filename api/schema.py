import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from posts.models import Post, Comment
from users.models import User

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

class Query(graphene.ObjectType):
    posts = graphene.List(PostType)
    comments = graphene.List(CommentType)
    users = graphene.List(UserType)

    def resolve_posts(root, info):
        return Post.objects.all()
    
    def resolve_comments(root, info):
        return Comment.objects.all()

    def resolve_users(root, info):
        return User.objects.all()

schema = graphene.Schema(query=Query)
