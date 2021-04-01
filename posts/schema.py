from game.models import Channel
import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import Post, Comment
from .enums import PostVisibilityEnums
from users.models import Profile, User, UserFollows
from users.enums import ProfileVisibilityEnums
from tags.models import Tag
from django.db.models import Q


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
    posts_by_tag = graphene.List(PostType, tags=graphene.List(graphene.String, required=True) ,description="Gets all posts based on given tags")

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
            criterion1 = Q(author__in=following, visibility=PostVisibilityEnums.ACTIVE)
            criterion2 = Q(author=current_user_profile, visibility=PostVisibilityEnums.ACTIVE)
            return Post.objects.filter(criterion1 | criterion2).order_by('-date_created')
        
    def resolve_posts_by_tag(self, info, tags=[]):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get post by tags!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            following = UserFollows.objects.filter(user_profile=current_user_profile).values('following_user_profile')
            public_users = Profile.objects.filter(visibility=ProfileVisibilityEnums.PUBLIC)
            print(tags)
            tagobjects = Tag.objects.filter(name__in=tags)
            print(tagobjects)
            criterion1 = Q(author__in=public_users, visibility=PostVisibilityEnums.ACTIVE, tags__in=tagobjects)
            criterion2 = Q(author__in=following, visibility=PostVisibilityEnums.ACTIVE, tags__in=tagobjects)
            return Post.objects.filter(criterion1 | criterion2).order_by('-date_created')

class CreatePost(graphene.Mutation):

    class Arguments:
        caption = graphene.String(default_value="", description="An (optional) textual description.")
        gps_longitude = graphene.Decimal(default_value=0.0, description="GPS Coordinates: Longitude")
        gps_latitude = graphene.Decimal(default_value=0.0, description="GPS Coordinates: Latitude")
        tagged_users = graphene.List(graphene.String, description="List of usernames of tagged users in post.")
        tags = graphene.List(graphene.String, description="List of tags asscoiated with the post.")
        image = graphene.String(required=True, description="Image media for post.")
        channel = graphene.String(default_value='', description="Channel name for post.")

    post = graphene.Field(PostType, description="Returns the new post that was created successfully.")
    success = graphene.Boolean(default_value=False, description="Returns whether the post was created successfully.")

    
    def mutate(self, info, image, caption, channel, gps_longitude, gps_latitude, tagged_users=[], tags=[]):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to create post!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            post = Post(author=current_user_profile, image=info.context.FILES[image], caption=caption, gps_longitude=gps_longitude, gps_latitude=gps_latitude)
            post.save()

            for user in tagged_users:
                post.tagged_users.add(Profile.objects.get(user=User.objects.get(username=user)))
                post.save()

            for tag in tags:
                if not Tag.objects.filter(name=tag).exists():
                    t = Tag(name=tag)
                    t.save()

                post.tags.add(Tag.objects.get(name=tag))
                post.save()

            if channel != '':
                if not Channel.objects.filter(name=channel).exists():
                    raise GraphQLError('Channel does not exist. Provide existing Channel')
                post.channel = Channel.objects.get(name=channel)
                post.save()
        
            return CreatePost(
                post,
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
                        post.author.points = post.author.points + 1
                        post.author.save()
                        post.save()
                if modifier == ModifierEnumsType.REMOVE:
                    if post.upvotes.filter(user=current_user_profile).exists():
                        post.upvotes.remove(current_user_profile)
                        post.author.points = post.author.points - 1
                        post.author.save()
                        post.save()
                
                return PostUpvote(
                    post_upvotes = post.upvotes.count(),
                    success=True
                )

class PostComment(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True, description="Unique ID for post to be commented")
        text = graphene.String(required=True, description="Comment text for post")
    
    success = graphene.Boolean(default_value=False, description="Returns whether the post was commented successfully.")

    def mutate(self, info, post_id, text):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to comment on posts!')
        else:
            post = Post.objects.get(post_id=post_id)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if (post.author.visibility == ProfileVisibilityEnums.PRIVATE) and not (UserFollows.objects.filter(user_profile=current_user_profile, following_user_profile=post.author).exists()) and not (current_user_profile==post.author):
                raise GraphQLError('You must be following post author to comment on private post!')
            else:
                comment = Comment(author=current_user_profile, post_id=post, comment_content=text)
                comment.save()
                
                return PostComment(
                    success=True
                )

class PostCommentReply(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True, description="Unique ID for post to be upvoted")
        text = graphene.String(required=True, description="Comment text for post")
        reply_to_id = graphene.ID(required=True, description="Unique ID for comment reply")
    
    success = graphene.Boolean(default_value=False, description="Returns whether the post was upvoted successfully.")

    def mutate(self, info, post_id, text, reply_to_id):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to comment on posts!')
        else:
            post = Post.objects.get(post_id=post_id)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if (post.author.visibility == ProfileVisibilityEnums.PRIVATE) and not (UserFollows.objects.filter(user_profile=current_user_profile, following_user_profile=post.author).exists()) and not (current_user_profile==post.author):
                raise GraphQLError('You must be following post author to comment on private post!')
            else:
                comment = Comment(author=current_user_profile, post_id=post, comment_content=text, reply_to_comment=Comment.objects.get(comment_id=reply_to_id))
                comment.save()
                
                return PostCommentReply(
                    success=True
                )

class PostIncrementViewCounter(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True, description="Unique ID for post to be upvoted")
    
    success = graphene.Boolean(default_value=False, description="Returns whether the post was upvoted successfully.")
    views = graphene.Int(description="Number of views for post")

    def mutate(self, info, post_id):

        post = Post.objects.get(post_id=post_id)
        current_user_profile = Profile.objects.get(user=info.context.user)
            
        if (post.author.visibility == ProfileVisibilityEnums.PRIVATE) and not (UserFollows.objects.filter(user_profile=current_user_profile, following_user_profile=post.author).exists()) and not (current_user_profile==post.author):
            raise GraphQLError('You must be following post author to view private post!')
        else:
            post.views = post.views + 1
            post.save()
                
            return PostIncrementViewCounter(
                success=True
            )

class DeletePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True, description="Unique ID for post to be deleted")
    
    success = graphene.Boolean(default_value=False, description="Returns whether the post was deleted successfully.")

    def mutate(self, info, post_id):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to delete on posts!')
        else:
            post = Post.objects.get(post_id=post_id)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if (post.author != current_user_profile):
                raise GraphQLError('You must be post author to delete on post!')
            else:
                post.delete()
                
                return DeletePost(
                    success=True
                )

class EditPostCaption(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True, description="Unique ID for post to be upvoted")
        text = graphene.String(required=True, description="New Caption")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was upvoted successfully.")

    
    def mutate(self, info, post_id, text):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to edit posts!')
        else:
            post = Post.objects.get(post_id=post_id)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if (post.author != current_user_profile):
                raise GraphQLError('You must be post author to edit post!')
            else:
                post.caption = text
                post.save()
                
                return EditPostCaption(
                    success=True
                )

class EditPostTaggedUsers(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True, description="Unique ID for post to be modified")
        tagged_users = graphene.List(graphene.String, required=True, description="List of usernames of to be/removed tagged users in post.")
        modifier = ModifierEnumsType(required=True, description="Add or remove")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was edited successfully.")

    
    def mutate(self, info, post_id, modifier, tagged_users):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to edit posts!')
        else:
            post = Post.objects.get(post_id=post_id)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if (post.author != current_user_profile):
                raise GraphQLError('You must be post author to edit post!')
            else:
                if modifier == ModifierEnumsType.ADD:
                    for user in tagged_users:
                        post.tagged_users.add(Profile.objects.get(user=User.objects.get(username=user)))
                        post.save()
                if modifier == ModifierEnumsType.REMOVE:
                    for user in tagged_users:
                        post.tagged_users.remove(Profile.objects.get(user=User.objects.get(username=user)))
                        post.save()
                return EditPostTaggedUsers(
                    success=True
                )

class EditPostVisibility(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True, description="Unique ID for post to be modified")
        modifier = PostVisibilityType(required=True, description="Hidden or Visibile")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was edited successfully.")

    
    def mutate(self, info, post_id, modifier):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to edit posts!')
        else:
            post = Post.objects.get(post_id=post_id)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if (post.author != current_user_profile):
                raise GraphQLError('You must be post author to edit post!')
            else:
                if modifier == PostVisibilityType.ACTIVE:
                    post.visibility = PostVisibilityEnums.ACTIVE
                    post.save()
                if modifier == PostVisibilityType.HIDDEN:
                    post.visibility = PostVisibilityEnums.HIDDEN
                    post.save()
                return EditPostVisibility(
                    success=True
                )

class EditPostTags(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True, description="Unique ID for post to be modified")
        tags = graphene.List(graphene.String, required=True, description="List of tags of to be/removed in post.")
        modifier = ModifierEnumsType(required=True, description="Add or remove")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was edited successfully.")

    def mutate(self, info, post_id, modifier, tags):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to edit posts!')
        else:
            post = Post.objects.get(post_id=post_id)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if (post.author != current_user_profile):
                raise GraphQLError('You must be post author to edit tags!')
            else:
                if modifier == ModifierEnumsType.ADD:
                    for tag in tags:
                        if not Tag.objects.filter(name=tag).exists():
                            t = Tag(name=tag)
                            t.save()
                        post.tags.add(Tag.objects.get(name=tag))
                        post.save()
                if modifier == ModifierEnumsType.REMOVE:
                    for tag in tags:
                        if Tag.objects.filter(name=tag).exists():
                            post.tags.remove(Tag.objects.get(name=tag))
                            post.save()
                return EditPostTags(
                    success=True
                )

class EditPostChannel(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True, description="Unique ID for post to be upvoted")
        channel = graphene.String(required=True, description="Channel name")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was edited successfully.")

    
    def mutate(self, info, post_id, channel):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to edit posts!')
        else:
            post = Post.objects.get(post_id=post_id)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if (post.author != current_user_profile):
                raise GraphQLError('You must be post author to edit post!')
            else:
                if not Channel.objects.filter(name=channel).exists():
                    raise GraphQLError('Channel does not exist. Provide existing Channel')
                post.channel = Channel.objects.get(name=channel)
                post.save()
                
                return EditPostChannel(
                    success=True
                )

class PostsMutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    post_upvote = PostUpvote.Field()
    post_comment = PostComment.Field()
    post_comment_reply = PostCommentReply.Field()
    post_increment_view_counter = PostIncrementViewCounter.Field()
    delete_post = DeletePost.Field()
    edit_post_caption = EditPostCaption.Field()
    edit_post_tagged_users = EditPostTaggedUsers.Field()
    edit_post_visibility = EditPostVisibility.Field()
    edit_post_tags = EditPostTags.Field()
    edit_post_channel = EditPostChannel.Field()