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
        members = graphene.List(graphene.String, description="List of usernames of tagged users in post.")

    success = graphene.Boolean(default_value=False, description="Returns whether the chatroom was created successfully.")

    
    def mutate(self, info, members=[]):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to create chatroom!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            chatroom = ChatRoom(created_by=current_user_profile)
            chatroom.save()
            chatroom.members.add(current_user_profile)

            for user in members:
                chatroom.members.add(Profile.objects.get(user=User.objects.get(username=user)))

            chatroom.save()
        
            return CreateChatRoom(
                id = chatroom.id,
                success=True
            )

class PostMessage(graphene.Mutation):
    class Arguments:
        room = graphene.ID(required=True, description="Unique ID for chatroom for message to be posted in")
        text = graphene.String(default_value="", description="An (optional) text message.")
        image = graphene.String(description="Image media for chat.")
        post = graphene.ID(description="Unique ID for post to send")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was upvoted successfully.")

    def mutate(self, info, image, text, room, post):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to create post!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            chatroom = ChatRoom.objects.get(id=room)
            message = Message(author=current_user_profile, room=chatroom)
            message.save()
            if text:
                message.text = text
            if image:
                message.image=info.context.FILES[image]
            if post:
                message.post = Post.objects.get(id=post)

        
            return PostMessage(
                id = message.id,
                success=True
            )

class ChatMutation(graphene.ObjectType):
    create_chatroom = CreateChatRoom.Field()
    post_message = PostMessage.Field()