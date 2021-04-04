import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import ChatRoom, Message
from users.models import Profile, User
from posts.models import Post

from posts.schema import ModifierEnumsType

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

    chatroom = graphene.Field(ChatRoomType, description="Returns the new chatroom that was created successfully.")
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
                chatroom,
                success=True
            )

class DeleteChatRoom(graphene.Mutation):

    class Arguments:
        id = graphene.ID(required=True, description="Unique ID of Chat to be deleted")

    success = graphene.Boolean(default_value=False, description="Returns whether the chatroom was deleted successfully.")

    
    def mutate(self, info, id):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to delete on posts!')
        else:
            chatroom = ChatRoom.objects.get(id=id)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if (chatroom.created_by != current_user_profile):
                raise GraphQLError('You must be chat creator to delete on chatroom!')
            else:
                chatroom.delete()
                
                return DeleteChatRoom(
                    success=True
                )

class TextMessage(graphene.Mutation):
    class Arguments:
        room = graphene.ID(required=True, description="Unique ID for chatroom for message to be posted in")
        text = graphene.String(default_value="", description="An (optional) text message.")

    message = graphene.Field(MessageType, description="Returns the new message that was created successfully.")
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
                message,
                success=True
            )

class ImageMessage(graphene.Mutation):
    class Arguments:
        room = graphene.ID(required=True, description="Unique ID for chatroom for message to be posted in")
        image = graphene.String(description="Image media for chat.")

    message = graphene.Field(MessageType, description="Returns the new message that was created successfully.")
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
                message,
                success=True
            )

class PostMessage(graphene.Mutation):
    class Arguments:
        room = graphene.ID(required=True, description="Unique ID for chatroom for message to be posted in")
        post = graphene.ID(description="Unique ID for post to send")

    message = graphene.Field(MessageType, description="Returns the new message that was created successfully.")
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
                message,
                success=True
            )

class DeleteMessage(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True, description="Unique ID of Message to be deleted")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was upvoted successfully.")

    def mutate(self, info, id):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to delete on posts!')
        else:
            message = Message.objects.get(id=id)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if (message.author != current_user_profile):
                raise GraphQLError('You must be chat creator to delete on chatroom!')
            else:
                message.delete()
                
                return DeleteMessage(
                    success=True
                )

class ChatMembership(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True, description="Unique ID of Chatroom to be change membership")
        modifier = ModifierEnumsType(required=True, description="Add or remove")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was upvoted successfully.")
    
    def mutate(self, info, id, modifier):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to upvote posts!')
        else:
            chatroom = ChatRoom.objects.get(id=id)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if modifier == ModifierEnumsType.ADD:
                if not chatroom.members.filter(user=current_user_profile).exists():
                    chatroom.members.add(current_user_profile)
                    chatroom.save()
            if modifier == ModifierEnumsType.REMOVE:
                if chatroom.members.filter(user=current_user_profile).exists():
                    chatroom.members.remove(current_user_profile)
                    chatroom.save()
                
            return ChatMembership(
                success=True
            )

class EditChatRoomName(graphene.Mutation):

    class Arguments:
        id = graphene.ID(required=True, description="Unique ID of Chat to be edited")
        text = graphene.String(required=True, description="New name of ChatRoom")

    success = graphene.Boolean(default_value=False, description="Returns whether the chatroom was deleted successfully.")

    
    def mutate(self, info, id, text):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to delete on posts!')
        else:
            chatroom = ChatRoom.objects.get(id=id)
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if (chatroom.created_by != current_user_profile):
                raise GraphQLError('You must be chat creator to edit name of chatroom!')
            else:
                chatroom.name = text
                chatroom.save()
                
                return EditChatRoomName(
                    success=True
                )

class ChatMutation(graphene.ObjectType):
    create_chatroom = CreateChatRoom.Field()
    delete_chatroom = DeleteChatRoom.Field()
    text_message = TextMessage.Field()
    image_message = ImageMessage.Field()
    post_message = PostMessage.Field()
    delete_message = DeleteMessage.Field()
    modify_membership_chatroom = ChatMembership.Field()
    edit_chatroom_name = EditChatRoomName.Field()