import graphene
import base64
from PIL import Image
from io import BytesIO
from graphene_django import DjangoObjectType

from .models import Post, Comment
from users.models import Profile, User
from users.schema import UserType
from .enums import VisibilityEnums

class VisibilityType(graphene.Enum):
    ACTIVE = VisibilityEnums.ACTIVE
    HIDDEN = VisibilityEnums.HIDDEN

class PostType(DjangoObjectType):

    def resolve_image(self, info):
        """Resolve product image absolute path"""
        if self.image:
            self.image = info.context.build_absolute_uri(self.image.url)
        return self.image

    visibility = graphene.NonNull(VisibilityType)
    image_300x300 = graphene.String()
    image_250x250 = graphene.String()
    image_200x200 = graphene.String()
    image_150x150 = graphene.String()
    image_100x100 = graphene.String()
    image_75x75 = graphene.String()

    def resolve_image_300x300(self, info):
        return info.context.build_absolute_uri(Post.objects.get(post_id=self.post_id).image_300x300.url)
    
    def resolve_image_250x250(self, info):
        return info.context.build_absolute_uri(Post.objects.get(post_id=self.post_id).image_250x250.url)
    
    def resolve_image_200x200(self, info):
        return info.context.build_absolute_uri(Post.objects.get(post_id=self.post_id).image_200x200.url)
    
    def resolve_image_150x150(self, info):
        return info.context.build_absolute_uri(Post.objects.get(post_id=self.post_id).image_150x150.url)

    def resolve_image_100x100(self, info):
        return info.context.build_absolute_uri(Post.objects.get(post_id=self.post_id).image_100x100.url)

    def resolve_image_75x75(self, info):
        return info.context.build_absolute_uri(Post.objects.get(post_id=self.post_id).image_75x75.url)

    class Meta:
        model = Post
        fields = "__all__"

class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = "__all__"


class PostsQuery(graphene.AbstractType):

    post = graphene.Field(PostType, id=graphene.ID(required=True), description="Get one post based on given id")
    posts = graphene.List(PostType, description="Get all posts in the database that are PUBLIC")
    feed_posts = graphene.List(PostType, description="Gets all posts based on users followed by current user")

    def resolve_post(self, info, id):
        if not info.context.user.is_authenticated:
            raise Exception('User has to be LoggedIn to get specific posts!')
        else:
            return Post.objects.get(post_id=id)

    def resolve_posts(self, info):
        return Post.objects.filter(visibility=VisibilityEnums.ACTIVE)

    def resolve_feed_posts(self, info):
        if not info.context.user.is_authenticated:
            raise Exception('User has to be LoggedIn to get feed posts!')
        else:
            followers = Profile.objects.get(user=info.context.user).followers.all()
            return Post.objects.filter(author__in=followers.values_list('id', flat=True), visibility=VisibilityEnums.ACTIVE).order_by('-date_created')

class CreatePost(graphene.Mutation):

    class Arguments:
        caption = graphene.String(default_value="", description="An (optional) textual description.")
        gps_tag = graphene.String(default_value="", description="GPS Coordinates: Lat, Long")
        tagged_users = graphene.List(graphene.String, description="List of usernames of tagged users in post.")
        image = graphene.String(required=True, description="Image media for post.")

    post_id = graphene.ID(description="Unique ID for post")
    success = graphene.Boolean(default_value=False, description="Returns whether the post was created successfully.")

    
    def mutate(self, info, image, caption, gps_tag, tagged_users=[]):
        if not info.context.user.is_authenticated:
            raise Exception('User has to be LoggedIn to create posts!')
        else:
            post = Post(author=info.context.user, image=info.context.FILES[image], caption=caption, gps_tag=gps_tag)
            post.save()

            for user in tagged_users:
                post.tagged_users.add(User.objects.get(username=user))

            if Post.objects.get(post_id=post.post_id):
                success = True
        
            return CreatePost(
                post_id = post.post_id,
                success=True
            )


class PostsMutation(graphene.ObjectType):
    create_post = CreatePost.Field()