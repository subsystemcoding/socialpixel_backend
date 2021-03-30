import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import Channel, Game, Leaderboard, LeaderboardRow, ValidatePost
from users.models import Profile
from posts.models import Post
from tags.models import Tag
from chat.models import ChatRoom
from django.dispatch import Signal

post_added_to_game = Signal()

from posts.schema import ModifierEnumsType

class ValidatorEnumsType(graphene.Enum):
    ACCEPT = 1
    REJECT = 0

class ChannelType(DjangoObjectType):
    def resolve_cover_image(self, info):
        """Resolve cover image absolute path"""
        if self.cover_image:
            self.cover_image = info.context.build_absolute_uri(self.cover_image.url)
        return self.cover_image

    def resolve_avatar(self, info):
        """Resolve avatar image absolute path"""
        if self.avatar:
            self.avatar = info.context.build_absolute_uri(self.avatar.url)
        return self.avatar
        
    class Meta:
        model = Channel
        fields = "__all__"

class GameType(DjangoObjectType):
    def resolve_image(self, info):
        """Resolve image absolute path"""
        if self.image:
            self.image = info.context.build_absolute_uri(self.image.url)
        return self.image
    
    class Meta:
        model = Game
        fields = "__all__"

class LeaderboardType(DjangoObjectType):
    class Meta:
        model = Leaderboard
        fields = "__all__"

class LeaderboardRowType(DjangoObjectType):    
    class Meta:
        model = LeaderboardRow
        fields = "__all__"

class ValidatePostType(DjangoObjectType):
    class Meta:
        model = ValidatePost
        fields = "__all__"

class ChannelQuery(graphene.AbstractType):

    channel = graphene.Field(ChannelType, id=graphene.ID(required=True), description="Get one channel based on given id")
    channelname = graphene.Field(ChannelType, name=graphene.String(required=True), description="Get one channel based on given name")
    channels = graphene.List(ChannelType, description="Get all channels")
    channels_by_tag = graphene.List(ChannelType, tags=graphene.List(graphene.String, required=True) ,description="Gets all channels based on given tags")

    def resolve_channel(self, info, id):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get channel by channel_id!')
        else:
            return Channel.objects.get(id=id)
    
    def resolve_channelname(self, info, name):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get channel by channel_id!')
        else:
            return Channel.objects.get(name=name)

    def resolve_channels(self, info):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get channels!')
        else:
            return Channel.objects.all()

    def resolve_channels_by_tag(self, info, tags=[]):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get channels!')
        else:
            tagobjects = Tag.objects.filter(name__in=tags)
            return Channel.objects.filter(tags__in=tagobjects)

class GameQuery(graphene.AbstractType):

    game = graphene.Field(GameType, id=graphene.ID(required=True), description="Get one game based on given id")
    gamename = graphene.Field(GameType, name=graphene.String(required=True), description="Get one game based on given name")
    games = graphene.List(GameType, description="Get all games")
    games_by_tag = graphene.List(GameType, tags=graphene.List(graphene.String, required=True) ,description="Gets all games based on given tags")

    def resolve_game(self, info, id):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get game by id!')
        else:
            return Game.objects.get(id=id)
    
    def resolve_gamename(self, info, name):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get game by name!')
        else:
            return Game.objects.get(name=name)

    def resolve_games(self, info):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get games!')
        else:
            return Game.objects.all()
    
    def resolve_games_by_tag(self, info, tags=[]):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get games!')
        else:
            tagobjects = Tag.objects.filter(name__in=tags)
            return Game.objects.filter(tags__in=tagobjects)

class ValidatePostQuery(graphene.AbstractType):

    validate_post = graphene.Field(ValidatePostType, id=graphene.ID(required=True), description="Get one post to be validated based on given id")
    validate_posts = graphene.List(ValidatePostType, description="Get all posts to be validated")
    validate_posts_by_game = graphene.List(ValidatePostType, game=graphene.String(required=True), channel=graphene.String(required=True) ,description="Gets all posts to be validated for given game in channel")
    validate_posts_by_channel = graphene.List(ValidatePostType, channel=graphene.String(required=True) ,description="Gets all posts to be validated for given channel")

    def resolve_validate_post(self, info, id):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get post to be validated by id!')
        else:
            return ValidatePost.objects.get(id=id)
    
    def resolve_validate_posts(self, info):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get all posts to be validated!')
        else:
            return ValidatePost.objects.all()

    def resolve_validate_posts_by_game(self, info, game, channel):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get post to be validated by game!')
        else:
            return ValidatePost.objects.filter(game=Game.objects.get(name=game, channel=channel))
    
    def resolve_validate_posts_by_channel(self, info, channel):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get post to be validated by channel!')
        else:
            return ValidatePost.objects.filter(channel=Channel.objects.get(name=channel))

class CreateChannel(graphene.Mutation):

    class Arguments:
        name = graphene.String(required=True, description="Name of Channel.")
        description = graphene.String(default_value="", description="Description of the Channel.")
        cover_image = graphene.String(default_value="", description="Cover image media for Channel.")
        avatar_image = graphene.String(default_value="", description="Avatar image media for Channel.")
        tags = graphene.List(graphene.String, description="List of tags asscoiated with the Channel.")

    channel = graphene.Field(ChannelType, description="Returns the new channel that was created successfully.")
    success = graphene.Boolean(default_value=False, description="Returns whether the chatroom was created successfully.")

    
    def mutate(self, info, name, description, cover_image, avatar_image, tags=[]):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to create chatroom!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            if Channel.objects.filter(name=name).exists():
                raise GraphQLError('Channel with same name exists. PLease try another name!')
            channel = Channel(name=name, description=description)
            channel.save()
            channel.subscribers.add(current_user_profile)
            channel.save()

            if cover_image != "":
                channel.cover_image = image=info.context.FILES[cover_image]
                channel.save()
            
            if avatar_image != "":
                channel.avatar = image=info.context.FILES[avatar_image]
                channel.save()

            for tag in tags:
                if not Tag.objects.filter(name=tag).exists():
                    t = Tag(name=tag)
                    t.save()

                channel.tags.add(Tag.objects.get(name=tag))
                channel.save()

            chatroomname = '{}-chatroom'.format(name)
            chatroom = ChatRoom(created_by=current_user_profile, name=chatroomname)
            chatroom.save()
            chatroom.members.add(current_user_profile)
            chatroom.save()
            channel.chatroom = chatroom
            channel.save()
        
            return CreateChannel(
                channel,
                success=True
            )

class DeleteChannel(graphene.Mutation):

    class Arguments:
        name = graphene.String(required=True, description="Unique name of channel to be deleted")

    success = graphene.Boolean(default_value=False, description="Returns whether the channel was deleted successfully.")

    
    def mutate(self, info, name):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to delete on posts!')
        else:
            Channel.objects.get(name=name).delete()
                
            return DeleteChannel(
                success=True
            )

class ChannelChangeDescription(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True, description="Unique name for channel to be edited")
        description = graphene.String(required=True, description="New description")

    success = graphene.Boolean(default_value=False, description="Returns whether the description was changed successfully.")

    def mutate(self, info, name, description):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to change channel description!')
        else:

            channel = Channel.objects.get(name=name)
            channel.description = description
            channel.save()

            return ChannelChangeDescription(
                success=True
            )

class ChannelChangeCoverImage(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True, description="Unique name for channel to be edited")
        image = graphene.String(required=True, description="New image")

    success = graphene.Boolean(default_value=False, description="Returns whether the cover image was changed successfully.")

    def mutate(self, info, name, image):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to change channel cover image!')
        else:
            channel = Channel.objects.get(name=name)
            channel.cover_image = info.context.FILES[image]
            channel.save()

            return ChannelChangeCoverImage(
                success=True
            )

class ChannelChangeAvatarImage(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True, description="Unique name for channel to be edited")
        image = graphene.String(required=True, description="New image")

    success = graphene.Boolean(default_value=False, description="Returns whether the avatar image was changed successfully.")

    def mutate(self, info, name, image):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to change channel avatar image!')
        else:
            channel = Channel.objects.get(name=name)
            channel.avatar = info.context.FILES[image]
            channel.save()

            return ChannelChangeCoverImage(
                success=True
            )

class ChannelSubscription(graphene.Mutation):
    class Arguments:
        name = graphene.ID(required=True, description="Unique name of Channel to be change membership")
        modifier = ModifierEnumsType(required=True, description="Add or remove")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was upvoted successfully.")
    
    def mutate(self, info, name, modifier):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to add/remove channel memberships!')
        else:
            channel = Channel.objects.get(name=name)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if modifier == ModifierEnumsType.ADD:
                if not channel.subscribers.filter(user=current_user_profile).exists():
                    channel.subscribers.add(current_user_profile)
                    channel.chatroom.members.add(current_user_profile)
                    channel.chatroom.save()
                    channel.save()
            if modifier == ModifierEnumsType.REMOVE:
                if channel.subscribers.filter(user=current_user_profile).exists():
                    channel.subscribers.remove(current_user_profile)
                    channel.chatroom.members.remove(current_user_profile)
                    channel.chatroom.save()
                    channel.save()
                
            return ChannelSubscription(
                success=True
            )

class CreateGame(graphene.Mutation):

    class Arguments:
        name = graphene.String(required=True, description="Name of Game.")
        channel = graphene.String(required=True, description="Name of Channel.")
        description = graphene.String(default_value="", description="Description of the Game.")
        game_image = graphene.String(default_value="", description="Game image media for Game.")
        tags = graphene.List(graphene.String, description="List of tags asscoiated with the Game.")
        posts = graphene.List(graphene.ID, required=True, description="List of post_id to be added to the Game.")
        
    game = graphene.Field(GameType, description="Returns the new game that was created successfully.")
    success = graphene.Boolean(default_value=False, description="Returns whether the game was created successfully.")

    
    def mutate(self, info, name, description, game_image, channel, tags=[], posts=[]):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to create game!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            channel = Channel.objects.get(name=channel)

            if not channel.subscribers.filter(user=current_user_profile).exists():
                raise GraphQLError('You must be suscribed to channel to add games!')

            if Game.objects.filter(name=name, channel=channel).exists():
                raise GraphQLError('Game with same name exists in Channel. PLease try another name!')
            

            game = Game(name=name, channel=channel, description=description, creator=current_user_profile)
            game.save()

            game.subscribers.add(current_user_profile)
            game.save()

            if game_image != "":
                game.image = image=info.context.FILES[game_image]
                game.save()

            for tag in tags:
                if not Tag.objects.filter(name=tag).exists():
                    t = Tag(name=tag)
                    t.save()

                game.tags.add(Tag.objects.get(name=tag))
                game.save()

            for post_id in posts:
                post = Post.objects.get(post_id=post_id)

                game.posts.add(post)
                game.save()
        
            return CreateGame(
                game,
                success=True
            )

class DeleteGame(graphene.Mutation):

    class Arguments:
        name = graphene.String(required=True, description="Unique name of game to be deleted")

    success = graphene.Boolean(default_value=False, description="Returns whether the game was deleted successfully.")

    
    def mutate(self, info, name):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to delete game!')
        else:
            Game.objects.get(name=name).delete()
                
            return DeleteGame(
                success=True
            )

class GameChangeDescription(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True, description="Unique name for game to be edited")
        description = graphene.String(required=True, description="New description")

    success = graphene.Boolean(default_value=False, description="Returns whether the description was changed successfully.")

    def mutate(self, info, name, description):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to change game description!')
        else:

            game = Game.objects.get(name=name)
            game.description = description
            game.save()

            return GameChangeDescription(
                success=True
            )

class GameChangeImage(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True, description="Unique name for game to be edited")
        image = graphene.String(required=True, description="New image")

    success = graphene.Boolean(default_value=False, description="Returns whether the image was changed successfully.")

    def mutate(self, info, name, image):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to change game image!')
        else:
            game = Channel.objects.get(name=name)
            game.image = info.context.FILES[image]
            game.save()

            return GameChangeImage(
                success=True
            )

class AddGamePosts(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True, description="Unique name of Game to be add post too")
        post_id = graphene.ID(required=True, description="Unique ID for post to be added")
        original_post_id = graphene.ID(required=True, description="Unique ID for the original post")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was added successfully.")
    
    def mutate(self, info, name, post_id, original_post_id):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to add posts to games!')
        else:
            game = Game.objects.get(name=name)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if not game.channel.subscribers.filter(user=current_user_profile).exists():
                raise GraphQLError('You must be suscribed to channel to add post to game!')
            
            if not game.subscribers.filter(user=current_user_profile).exists():
                raise GraphQLError('You must be suscribed to game to add post to game!')

            post = Post.objects.get(post_id=post_id)
            original_post = Post.objects.get(post_id=original_post_id)

            if post.author != current_user_profile:
                raise GraphQLError('You must be post author to add post to game!')

            validate_post = ValidatePost(game=Game.objects.get(name=name), post=post, channel=game.channel, creator_post=original_post)
            validate_post.save()

            game.save()

            return RemoveGamePosts(
                success=True
            )

class RemoveGamePosts(graphene.Mutation):
    class Arguments:
        name = graphene.ID(required=True, description="Unique name of Game to be remove post from")
        post_id = graphene.ID(required=True, description="Unique ID for post to be removed")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was removed successfully.")
    
    def mutate(self, info, name, post_id):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to remove posts to games!')
        else:
            game = Game.objects.get(name=name)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if not game.channel.subscribers.filter(user=current_user_profile).exists():
                raise GraphQLError('You must be suscribed to channel to remove post to game!')
            
            post = Post.objects.get(post_id=post_id)

            if post.author != current_user_profile:
                raise GraphQLError('You must be post author to remove post to game!')
            
            game.posts.remove(post)
            game.save()

            return RemoveGamePosts(
                success=True
            )

class EditChannelTags(graphene.Mutation):
    class Arguments:
        name = graphene.ID(required=True, description="Unique name of Channel to be change tags")
        modifier = ModifierEnumsType(required=True, description="Add or remove")
        tags = graphene.List(graphene.String, required=True, description="List of tags of to be/removed in Channel.")

    success = graphene.Boolean(default_value=False, description="Returns whether the Channel was edited successfully.")

    
    def mutate(self, info, name, modifier, tags):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to edit channels!')
        else:
            channel = Channel.objects.get(name=name)
            
            if modifier == ModifierEnumsType.ADD:
                for tag in tags:
                    if not Tag.objects.filter(name=tag).exists():
                        t = Tag(name=tag)
                        t.save()
                    channel.tags.add(Tag.objects.get(name=tag))
                    channel.save()
            if modifier == ModifierEnumsType.REMOVE:
                for tag in tags:
                    if Tag.objects.filter(name=tag).exists():
                        channel.tags.remove(Tag.objects.get(name=tag))
                        channel.save()
                
            return EditChannelTags(
                success=True
            )

class EditGameTags(graphene.Mutation):
    class Arguments:
        name = graphene.ID(required=True, description="Unique name of game to be change tags")
        modifier = ModifierEnumsType(required=True, description="Add or remove")
        tags = graphene.List(graphene.String, required=True, description="List of tags of to be/removed in game.")

    success = graphene.Boolean(default_value=False, description="Returns whether the game was edited successfully.")

    
    def mutate(self, info, name, modifier, tags):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to edit game!')
        else:
            game = Game.objects.get(name=name)
            
            if modifier == ModifierEnumsType.ADD:
                for tag in tags:
                    if not Tag.objects.filter(name=tag).exists():
                        t = Tag(name=tag)
                        t.save()
                    game.tags.add(Tag.objects.get(name=tag))
                    game.save()
            if modifier == ModifierEnumsType.REMOVE:
                for tag in tags:
                    if Tag.objects.filter(name=tag).exists():
                        game.tags.remove(Tag.objects.get(name=tag))
                        game.save()
                
            return EditGameTags(
                success=True
            )

class ValidatePostMutationMethod(graphene.Mutation):

    class Arguments:
        post_id = graphene.ID(required=True, description="post_id in Game to be validated")
        game = graphene.String(required=True, description="Unique name for game in which post to be validated")
        modifier = ValidatorEnumsType(required=True, description="Accept or Reject")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was validated successfully.")
    
    def mutate(self, info, post_id, game, modifier):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to add posts to games!')
        else:
            game = Game.objects.get(name=game)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if not game.channel.subscribers.filter(user=current_user_profile).exists():
                raise GraphQLError('You must be suscribed to channel to validate posts for game!')

            post = Post.objects.get(post_id=post_id)
            validate_post = ValidatePost.objects.get(game=game, post=post)

            if modifier == ValidatorEnumsType.ACCEPT:
                game.posts.add(post)
                game.save()
                post.author.points = post.author.points + 100
                post.author.save()
                current_user_profile.points = current_user_profile.points + 50
                current_user_profile.save()
                validate_post.delete()
                post_added_to_game.send(sender=self.__class__, post_author = post.author.user.username, gamename=game.name, channelname=game.channel.name)
            if modifier == ValidatorEnumsType.REJECT:
                validate_post.delete()
                current_user_profile.points = current_user_profile.points + 200
                current_user_profile.save()

            game.save()

            return ValidatePostMutationMethod(
                success=True
            )

class GameSubscription(graphene.Mutation):
    class Arguments:
        channel = graphene.String(required=True, description="Unique name of Channel of game")
        game = graphene.String(required=True, description="Unique name of game to be change membership")
        modifier = ModifierEnumsType(required=True, description="Add or remove")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was upvoted successfully.")
    
    def mutate(self, info, channel, game, modifier):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to add/remove channel memberships!')
        else:
            channelobj = Channel.objects.get(name=channel)
            game = Game.objects.filter(channel=channelobj, name=game)[0]
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if modifier == ModifierEnumsType.ADD:
                if not game.subscribers.filter(user=current_user_profile).exists():
                    game.subscribers.add(current_user_profile)
                    game.save()
            if modifier == ModifierEnumsType.REMOVE:
                if game.subscribers.filter(user=current_user_profile).exists():
                    game.subscribers.remove(current_user_profile)
                    game.save()
                
            return GameSubscription(
                success=True
            )

class ChannelMutation(graphene.ObjectType):
    create_channel = CreateChannel.Field()
    delete_channel = DeleteChannel.Field()
    channel_change_description = ChannelChangeDescription.Field()
    channel_change_cover_image = ChannelChangeCoverImage.Field()
    channel_change_avatar_image = ChannelChangeAvatarImage.Field()
    channel_subscription = ChannelSubscription.Field()
    edit_channel_tags = EditChannelTags.Field()
class GameMutation(graphene.ObjectType):
    create_game = CreateGame.Field()
    delete_game = DeleteGame.Field()
    game_change_description = GameChangeDescription.Field()
    game_change_image = GameChangeImage.Field()
    game_add_post = AddGamePosts.Field()
    game_remove_post = RemoveGamePosts.Field()
    edit_game_tags = EditGameTags.Field()
    game_subscription = GameSubscription.Field()

class ValidatePostMutation(graphene.ObjectType):
    validate_post = ValidatePostMutationMethod.Field()
