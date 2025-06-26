import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import django_filters

from blogapp.models import Blog
from django.contrib.auth.models import User


# Tipo para usuario
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email")


# Tipo simple BlogType
class BlogType(DjangoObjectType):
    average_rating = graphene.Float()
    tag_list = graphene.List(graphene.String)
    author = graphene.Field(UserType)

    class Meta:
        model = Blog
        fields = ('id', 'title', 'content', 'author', 'image', 'created_at', 'updated_at')

    def resolve_average_rating(self, info):
        return self.average_rating()

    def resolve_tag_list(self, info):
        return [tag.name for tag in self.tags.all()]


# Tipo Relay BlogNode para paginación y filtros
class BlogNode(DjangoObjectType):
    average_rating = graphene.Float()
    tag_list = graphene.List(graphene.String)
    author = graphene.Field(UserType)

    class Meta:
        model = Blog
        interfaces = (relay.Node,)
        fields = ('id', 'title', 'content', 'author', 'image', 'created_at', 'updated_at')

    def resolve_average_rating(self, info):
        return self.average_rating()

    def resolve_tag_list(self, info):
        return [tag.name for tag in self.tags.all()]


# Filtros para Relay (nombres amigables para GraphQL)
class BlogFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    authorUsername = django_filters.CharFilter(field_name='author__username', lookup_expr='icontains')

    class Meta:
        model = Blog
        fields = ['title', 'authorUsername']


# Query unificada
class Query(graphene.ObjectType):
    all_blogs_simple = graphene.List(BlogType)

    # Este campo usa Relay con filtros y paginación, no definas resolver
    all_blogs = DjangoFilterConnectionField(BlogNode, filterset_class=BlogFilter)

    blog_by_id = graphene.Field(BlogType, id=graphene.ID(required=True))

    def resolve_all_blogs_simple(root, info):
        return Blog.objects.all()

    def resolve_blog_by_id(root, info, id):
        return Blog.objects.get(pk=id)


# Mutaciones
class CreateBlog(graphene.Mutation):
    blog = graphene.Field(BlogType)

    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        image = graphene.String()
        author_id = graphene.ID(required=True)
        tags = graphene.List(graphene.String)

    def mutate(self, info, title, content, author_id, tags=None, image=None):
        author = User.objects.get(pk=author_id)
        blog = Blog(title=title, content=content, author=author)

        if image:
            blog.image = image

        blog.save()

        if tags:
            blog.tags.set(tags)

        return CreateBlog(blog=blog)


class UpdateBlog(graphene.Mutation):
    blog = graphene.Field(BlogType)

    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        content = graphene.String()
        image = graphene.String()
        tags = graphene.List(graphene.String)

    def mutate(self, info, id, title=None, content=None, image=None, tags=None):
        try:
            blog = Blog.objects.get(pk=id)
        except Blog.DoesNotExist:
            raise Exception("Blog no encontrado")

        if title is not None:
            blog.title = title
        if content is not None:
            blog.content = content
        if image is not None:
            blog.image = image

        blog.save()

        if tags is not None:
            blog.tags.set([tag.strip() for tag in tags])

        return UpdateBlog(blog=blog)


class DeleteBlog(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        try:
            blog = Blog.objects.get(pk=id)
            blog.delete()
            return DeleteBlog(ok=True, message="Blog eliminado correctamente")
        except Blog.DoesNotExist:
            return DeleteBlog(ok=False, message="Blog no encontrado")


class Mutation(graphene.ObjectType):
    create_blog = CreateBlog.Field()
    update_blog = UpdateBlog.Field()
    delete_blog = DeleteBlog.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
