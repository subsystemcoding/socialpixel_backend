import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import ChatRoom, Message
from users.models import Profile, User
from posts.models import Post

class MessageType(DjangoObjectType):
    def resolve_image(self, info):
        """Resolve product image absolute path"""
        if self.image:
            self.image = info.context.build_absolute_uri(self.image.url)
        return self.image
        
    class Meta:
        model = Message
        fields = "__all__"

class ChatRoomType(DjangoObjectType):
    class Meta:
        model = ChatRoom
        fields = "__all__"


class ChatQuery(graphene.AbstractType):

    chatroom = graphene.Field(ChatRoomType, id=graphene.ID(required=True), description="Get one chatroom based on given id")
    chatrooms = graphene.List(ChatRoomType, description="Get all chatrooms in the database for given user")

    def resolve_chatroom(self, info, id):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get chatroom by chatroom_id!')
        else:
            chatroom = ChatRoom.objects.get(id=id)
            current_user_profile = Profile.objects.get(user=info.context.user)

            if not current_user_profile.member_in.filter(id=chatroom.id).exists():
                raise GraphQLError('You must be part of chatroom to get chatroom details!')
            else:
                return chatroom

    def resolve_chatrooms(self, info):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get chatrooms!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            return current_user_profile.member_in.get_queryset().order_by('-last_messaged_timestamp')

class CreateChatRoom(graphene.Mutation):

    class Arguments:
        members = graphene.List(graphene.String, description="List of usernames of members.")
        name = graphene.String(required=True, description="Name of Chat.")

    success = graphene.Boolean(default_value=False, description="Returns whether the chatroom was created successfully.")

    
    def mutate(self, info, name, members=[]):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to create chatroom!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            chatroom = ChatRoom(created_by=current_user_profile, name=name)
            chatroom.save()
            chatroom.members.add(current_user_profile)

            for user in members:
                chatroom.members.add(Profile.objects.get(user=User.objects.get(username=user)))

            chatroom.save()
        
            return CreateChatRoom(
                success=True
            )

class TextMessage(graphene.Mutation):
    class Arguments:
        room = graphene.ID(required=True, description="Unique ID for chatroom for message to be posted in")
        text = graphene.String(default_value="", description="An (optional) text message.")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was upvoted successfully.")

    def mutate(self, info, text, room):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to create post!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            chatroom = ChatRoom.objects.get(id=room)
            message = Message(author=current_user_profile, room=chatroom, text=text)
            message.save()

            return TextMessage(
                success=True
            )

class ImageMessage(graphene.Mutation):
    class Arguments:
        room = graphene.ID(required=True, description="Unique ID for chatroom for message to be posted in")
        image = graphene.String(description="Image media for chat.")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was upvoted successfully.")

    def mutate(self, info, image, room):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to create post!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            chatroom = ChatRoom.objects.get(id=room)
            message = Message(author=current_user_profile, room=chatroom, image=info.context.FILES[image])
            message.save()

            return TextMessage(
                success=True
            )

class PostMessage(graphene.Mutation):
    class Arguments:
        room = graphene.ID(required=True, description="Unique ID for chatroom for message to be posted in")
        post = graphene.ID(description="Unique ID for post to send")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was upvoted successfully.")

    def mutate(self, info, room, post):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to create post!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            chatroom = ChatRoom.objects.get(id=room)
            message = Message(author=current_user_profile, room=chatroom, post = Post.objects.get(post_id=post))
            message.save()

            return TextMessage(
                success=True
            )


class ChatMutation(graphene.ObjectType):
    create_chatroom = CreateChatRoom.Field()
    text_message = TextMessage.Field()
    image_message = ImageMessage.Field()
    post_message = PostMessage.Field()