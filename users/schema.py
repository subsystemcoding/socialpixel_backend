import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphql_auth import mutations as gqlAuthMutations
from graphql import GraphQLError

from .models import User, Profile, UserFollows
from .enums import ProfileVisibilityEnums
from posts.schema import ModifierEnumsType

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
    userprofilefollowers = graphene.List(ProfileType)
    userprofilefollowing = graphene.List(ProfileType)
    userprofilefollowersnumber = graphene.Int()
    userprofilefollowingnumber = graphene.Int()

    @login_required
    def resolve_users(self, info):
        return User.objects.all()
    
    @login_required
    def resolve_userprofile(self, info, username):
        user = User.objects.get(username=username)
        return Profile.objects.get(user=user)

    @login_required
    def resolve_userprofilefollowers(self, info):
        current_user_profile = Profile.objects.get(user=info.context.user)
        return Profile.objects.filter(following__in=current_user_profile.followers.all())

    @login_required
    def resolve_userprofilefollowing(self, info):
        current_user_profile = Profile.objects.get(user=info.context.user)
        return Profile.objects.filter(followers__in=current_user_profile.following.all())

    @login_required
    def resolve_userprofilefollowersnumber(self, info):
        current_user_profile = Profile.objects.get(user=info.context.user)
        return Profile.objects.filter(following__in=current_user_profile.followers.all()).count()

    @login_required
    def resolve_userprofilefollowingnumber(self, info):
        current_user_profile = Profile.objects.get(user=info.context.user)
        return Profile.objects.filter(followers__in=current_user_profile.following.all()).count()

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

class UserRelationship(graphene.Mutation):

    class Arguments:
        username = graphene.String(required=True, description="Username of profile to establish relationship")
        modifier = ModifierEnumsType(required=True, description="Add or remove")

    success = graphene.Boolean(default_value=False, description="Returns whether the user relationhip operation successful.")

    def mutate(self, info, username, modifier):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to follow on unfollow users!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            user_profile_to_follow = Profile.objects.get(user=User.objects.get(username=username))

            if modifier == ModifierEnumsType.ADD:
                if not UserFollows.objects.filter(user_profile=current_user_profile, following_user_profile=user_profile_to_follow).exists():
                    user_follow = UserFollows(user_profile=current_user_profile, following_user_profile=user_profile_to_follow)
                    user_follow.save()
            if modifier == ModifierEnumsType.REMOVE:
                if UserFollows.objects.filter(user_profile=current_user_profile, following_user_profile=user_profile_to_follow).exists():
                    user_follow = UserFollows.objects.get(user_profile=current_user_profile, following_user_profile=user_profile_to_follow)
                    user_follow.delete()

            return UserRelationship(
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
    user_relationship = UserRelationship.Field()