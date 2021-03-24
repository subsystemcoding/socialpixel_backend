import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphql_auth import mutations as gqlAuthMutations

from .models import User, Profile

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