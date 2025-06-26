import graphene
from graphene_django import DjangoObjectType
from blogapp.models import Blog
from django.contrib.auth.models import User
from taggit.models import Tag

class BlogType(DjangoObjectType):
    average_rating = graphene.Float() #campos personalizados
    tags = graphene.List(graphene.String)  

    class Meta:
        model = Blog
        exclude = ("tags",)  

    def resolve_average_rating(self, info):
        return self.average_rating()

    def resolve_tags(self, info):
        return [tag.name for tag in self.tags.all()]


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hi!")
    all_blogs = graphene.List(BlogType)
    blog_by_id = graphene.Field(BlogType, id=graphene.ID(required=True))

    def resolve_all_blogs(root, info):
        return Blog.objects.all()

    def resolve_blog_by_id(root, info, id):
        return Blog.objects.get(pk=id)




class CreateBlog(graphene.Mutation):
    # Campos que devuelve la mutación
    blog = graphene.Field(BlogType)  # El blog recién creado

    # Entradas requeridas para la mutación (lo que el usuario debe enviar)
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        image = graphene.String()  
        author_id = graphene.ID(required=True)
        tags = graphene.List(graphene.String)  # Lista de etiquetas como strings

    # Función que se ejecuta cuando se llama a la mutación
    def mutate(self, info, title, content, author_id, tags=None, image=None):
        author = User.objects.get(pk=author_id)  # Obtenemos el autor (usuario) desde la base de datos
        blog = Blog(title=title, content=content, author=author)

        if image:
            blog.image = image  # Si se envía una imagen, la asignamos

        blog.save()  # Guardamos el blog en la base de datos

        if tags:
            blog.tags.set(tags)  # Asignamos las etiquetas al blog

        return CreateBlog(blog=blog)

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


class Mutation(graphene.ObjectType):   #donde  registramos las mutaciones
    create_blog = CreateBlog.Field() 
    update_blog = UpdateBlog.Field()
    delete_blog = DeleteBlog.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)