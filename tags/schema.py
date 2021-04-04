import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from .models import Tag
from users.models import Profile

class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = "__all__"

class TagQuery(graphene.AbstractType):

    tag = graphene.Field(TagType, name=graphene.String(required=True), description="Get one tag based on given name")
    tags = graphene.List(TagType, description="Get all tags")
    tag_search = graphene.List(TagType, query=graphene.String(required=True) ,description="Gets all tags based on given query")

    def resolve_tag(self, info, name):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get tag by name!')
        else:
            return Tag.objects.get(name=name)

    def resolve_tags(self, info):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get tags!')
        else:
            return Tag.objects.all()

    def resolve_tag_search(self, info, query):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to get tags by search!')
        else:
            return Tag.objects.filter(name__iregex=r""+ query +"")

class CreateTag(graphene.Mutation):

    class Arguments:
        name = graphene.String(required=True, description="Tag name.")
        description = graphene.String(default_value="", description="Description of the tag.")

    tag = graphene.Field(TagType, description="Returns the new tag that was created successfully.")
    success = graphene.Boolean(default_value=False, description="Returns whether the tag was created successfully.")

    
    def mutate(self, info, name, description):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to create tags!')
        else:
            current_user_profile = Profile.objects.get(user=info.context.user)
            if Tag.objects.filter(name=name).exists():
                raise GraphQLError('Tag with same name exists. Please try another name!')
            tag = Tag(name=name, description=description)
            tag.save()
        
            return CreateTag(
                tag,
                success=True
            )

class DeleteTag(graphene.Mutation):

    class Arguments:
        name = graphene.String(required=True, description="Unique name of tag to be deleted")

    success = graphene.Boolean(default_value=False, description="Returns whether the tag was deleted successfully.")

    
    def mutate(self, info, name):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to delete on posts!')
        else:
            Tag.objects.get(name=name).delete()
                
            return DeleteTag(
                success=True
            )

class TagChangeDescription(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True, description="Unique name for tag to be edited")
        description = graphene.String(required=True, description="New description")

    success = graphene.Boolean(default_value=False, description="Returns whether the description was changed successfully.")

    def mutate(self, info, name, description):
        if not info.context.user.is_authenticated:
            raise GraphQLError('You must be logged to change tag description!')
        else:

            tag = Tag.objects.get(name=name)
            tag.description = description
            tag.save()

            return TagChangeDescription(
                success=True
            )

class TagMutation(graphene.ObjectType):
    create_tag = CreateTag.Field()
    delete_tag = DeleteTag.Field()
    tag_change_description = TagChangeDescription.Field()
