import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import Post, Comment
from .enums import PostVisibilityEnums
from users.models import Profile, User, UserFollows
from users.enums import ProfileVisibilityEnums
class PostVisibilityType(graphene.Enum):
    ACTIVE = PostVisibilityEnums.ACTIVE
    HIDDEN = PostVisibilityEnums.HIDDEN

class ModifierEnumsType(graphene.Enum):
    ADD = 1
    REMOVE = 0

class PostType(DjangoObjectType):

    def resolve_image(self, info):
        """Resolve product image absolute path"""
        if self.image:
            self.image = info.context.build_absolute_uri(self.image.url)
        return self.image

    visibility = graphene.NonNull(PostVisibilityType)
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
            raise GraphQLError('You must be logged to get post by post_id!')
        else:
            post = Post.objects.get(post_id=id)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if (post.author.visibility == ProfileVisibilityEnums.PRIVATE) and not (UserFollows.objects.filter(user_profile=current_user_profile, following_user_profile=post.author).exists()) and not (current_user_profile==post.author):
                raise GraphQLError('You must be following post author to get private post!')
            else:
                return Post.objects.get(post_id=id)

    def resolve_posts(self, info):
        public_users = Profile.objects.filter(visibility=ProfileVisibilityEnums.PUBLIC)
        return Post.objects.filter(author__in=public_users, visibility=PostVisibilityEnums.ACTIVE).order_by('-date_created')

    def resolve_feed_posts(self, info):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get post feed!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            following = UserFollows.objects.filter(user_profile=current_user_profile).values('following_user_profile')
            return Post.objects.filter(author__in=following, visibility=PostVisibilityEnums.ACTIVE).order_by('-date_created')

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
            raise GraphQLError('You must be logged to create post!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            post = Post(author=current_user_profile, image=info.context.FILES[image], caption=caption, gps_tag=gps_tag)
            post.save()

            for user in tagged_users:
                post.tagged_users.add(Profile.objects.get(user=User.objects.get(username=user)))
        
            return CreatePost(
                post_id = post.post_id,
                success=True
            )

class PostUpvote(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True, description="Unique ID for post to be upvoted")
        modifier = ModifierEnumsType(required=True, description="Add or remove")

    post_upvotes = graphene.Int(description="Number of upvotes for post")
    success = graphene.Boolean(default_value=False, description="Returns whether the post was upvoted successfully.")

    
    def mutate(self, info, post_id, modifier):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to upvote posts!')
        else:
            post = Post.objects.get(post_id=post_id)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if (post.author.visibility == ProfileVisibilityEnums.PRIVATE) and not (UserFollows.objects.filter(user_profile=current_user_profile, following_user_profile=post.author).exists()) and not (current_user_profile==post.author):
                raise GraphQLError('You must be following post author to upvote private post!')
            else:
                if modifier == ModifierEnumsType.ADD:
                    if not post.upvotes.filter(user=current_user_profile).exists():
                        post.upvotes.add(current_user_profile)
                        post.save()
                if modifier == ModifierEnumsType.REMOVE:
                    if post.upvotes.filter(user=current_user_profile).exists():
                        post.upvotes.remove(current_user_profile)
                        post.save()
                
                return PostUpvote(
                    post_upvotes = post.upvotes.count(),
                    success=True
                )
class PostsMutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    post_upvote = PostUpvote.Field()