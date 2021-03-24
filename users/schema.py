import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphql_auth import mutations as gqlAuthMutations
from graphql import GraphQLError

from .models import User, Profile
from .enums import ProfileVisibilityEnums
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = (
            "username", "email",
            "first_name", "last_name",
            "date_joined"
        )

class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile
        fields = "__all__"

class ProfileVisibilityType(graphene.Enum):
    PUBLIC = ProfileVisibilityEnums.PUBLIC
    PRIVATE = ProfileVisibilityEnums.PRIVATE


class UsersQuery(graphene.AbstractType):
    users = graphene.List(UserType)
    userprofile = graphene.Field(ProfileType, username=graphene.String(required=True))

    @login_required
    def resolve_users(self, info):
        return User.objects.all()
    
    @login_required
    def resolve_userprofile(self, info, username):
        user = User.objects.get(username=username)
        return Profile.objects.get(user=user)

class EditProfileFirstName(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True, description="Name")

    success = graphene.Boolean(default_value=False, description="Returns whether the change was successful.")

    def mutate(self, info, name):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to edit profile!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            current_user_profile.user.first_name = name
            current_user_profile.user.save()
            current_user_profile.save()
                
            return EditProfileFirstName(
                success=True
            )

class EditProfileLastName(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True, description="Name")

    success = graphene.Boolean(default_value=False, description="Returns whether the change was successful.")

    def mutate(self, info, name):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to edit profile!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            current_user_profile.user.last_name = name
            current_user_profile.user.save()
            current_user_profile.save()
                
            return EditProfileLastName(
                success=True
            )

class EditProfileBio(graphene.Mutation):
    class Arguments:
        text = graphene.String(required=True, description="Bio")

    success = graphene.Boolean(default_value=False, description="Returns whether the change was successful.")

    def mutate(self, info, text):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to edit profile!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            current_user_profile.bio = text
            current_user_profile.save()
                
            return EditProfileBio(
                success=True
            )

class EditProfileVisibility(graphene.Mutation):
    class Arguments:
        modifier = ProfileVisibilityType(required=True, description="PRIVATE or Visibile")

    success = graphene.Boolean(default_value=False, description="Returns whether the post was edited successfully.")

    
    def mutate(self, info, modifier):

        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to edit posts!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            
            if modifier == ProfileVisibilityEnums.PUBLIC:
                current_user_profile.visibility = ProfileVisibilityEnums.PUBLIC
                current_user_profile.save()
            if modifier == ProfileVisibilityEnums.PRIVATE:
                current_user_profile.visibility = ProfileVisibilityEnums.PRIVATE
                current_user_profile.save()

            return EditProfileVisibility(
                success=True
            )

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

    #custom mine
    update_firstname = EditProfileFirstName.Field()
    update_lastname = EditProfileLastName.Field()
    update_bio = EditProfileBio.Field()
    update_profile_visibility = EditProfileVisibility.Field()