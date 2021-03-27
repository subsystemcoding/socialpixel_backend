from collections import defaultdict
import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
import random
from .models import Channel, Game, Leaderboard, LeaderboardRow
from users.models import Profile, User
from posts.models import Post

from posts.schema import ModifierEnumsType

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

class ChannelQuery(graphene.AbstractType):

    channel = graphene.Field(ChannelType, id=graphene.ID(required=True), description="Get one channel based on given id")
    channelname = graphene.Field(ChannelType, name=graphene.String(required=True), description="Get one channel based on given name")
    channels = graphene.List(ChannelType, description="Get all channels")

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

class GameQuery(graphene.AbstractType):

    game = graphene.Field(GameType, id=graphene.ID(required=True), description="Get one game based on given id")
    gamename = graphene.Field(GameType, name=graphene.String(required=True), description="Get one game based on given name")
    games = graphene.List(GameType, description="Get all games")

    def resolve_game(self, info, id):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get channel by channel_id!')
        else:
            return Game.objects.get(id=id)
    
    def resolve_gamename(self, info, name):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get channel by channel_id!')
        else:
            return Game.objects.get(name=name)

    def resolve_games(self, info):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get channels!')
        else:
            return Game.objects.all()

class CreateChannel(graphene.Mutation):

    class Arguments:
        name = graphene.String(required=True, description="Name of Channel.")
        description = graphene.String(default_value="", description="Description of the Channel.")
        cover_image = graphene.String(default_value="", description="Cover image media for Channel.")
        avatar_image = graphene.String(default_value="", description="Avatar image media for Channel.")

    success = graphene.Boolean(default_value=False, description="Returns whether the chatroom was created successfully.")

    
    def mutate(self, info, name, description, cover_image, avatar_image):
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
        
            return CreateChannel(
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
                    channel.save()
            if modifier == ModifierEnumsType.REMOVE:
                if channel.subscribers.filter(user=current_user_profile).exists():
                    channel.subscribers.remove(current_user_profile)
                    channel.save()
                
            return ChannelSubscription(
                success=True
            )

class CreateGame(graphene.Mutation):

    class Arguments:
        name = graphene.String(required=True, description="Name of Game.")
        channel = graphene.String(required=True, description="Name of Channel.")
        description = graphene.String(default_value="", description="Description of the Channel.")
        game_image = graphene.String(default_value="", description="Game image media for Channel.")

    success = graphene.Boolean(default_value=False, description="Returns whether the game was created successfully.")

    
    def mutate(self, info, name, description, game_image, channel):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to create game!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            channel = Channel.objects.get(name=channel)

            if not channel.subscribers.filter(user=current_user_profile).exists():
                raise GraphQLError('You must be suscribed to channel to add games!')

            if Game.objects.filter(name=name, channel=channel).exists():
                raise GraphQLError('Game with same name exists in Channel. PLease try another name!')
            

            game = Game(name=name, channel=channel, description=description)
            game.save()
            color = "%06x"%random.randint(0,0xFFFFFF)
            while Game.objects.all().values('pinColorHex').filter(pinColorHex=color).exists():
                color = "%06x"%random.randint(0,0xFFFFFF)
            game.pinColorHex = color
            game.save()

            if game_image != "":
                game.image = image=info.context.FILES[game_image]
                game.save()
        
            return CreateChannel(
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
        name = graphene.ID(required=True, description="Unique name of Game to be add post too")
        post_id = graphene.ID(required=True, description="Unique ID for post to be added")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was added successfully.")
    
    def mutate(self, info, name, post_id):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to add posts to games!')
        else:
            game = Game.objects.get(name=name)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if not game.channel.subscribers.filter(user=current_user_profile).exists():
                raise GraphQLError('You must be suscribed to channel to add post to game!')

            post = Post.objects.get(post_id=post_id)

            if post.author != current_user_profile:
                raise GraphQLError('You must be post author to add post to game!')
            
            game.posts.add(post)
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

class ChannelMutation(graphene.ObjectType):
    create_channel = CreateChannel.Field()
    delete_channel = DeleteChannel.Field()
    channel_change_description = ChannelChangeDescription.Field()
    channel_change_cover_image = ChannelChangeCoverImage.Field()
    channel_change_avatar_image = ChannelChangeAvatarImage.Field()
    channel_subscription = ChannelSubscription.Field()

class GameMutation(graphene.ObjectType):
    create_game = CreateGame.Field()
    delete_game = DeleteGame.Field()
    game_change_description = GameChangeDescription.Field()
    game_change_image = GameChangeImage.Field()
    game_add_post = AddGamePosts.Field()
    game_remove_post = RemoveGamePosts.Field()
