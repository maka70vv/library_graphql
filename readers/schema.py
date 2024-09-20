import graphene
from graphene_django.types import DjangoObjectType
from .models import Reader


class ReaderType(DjangoObjectType):
    class Meta:
        model = Reader


class Query(graphene.ObjectType):
    all_readers = graphene.List(ReaderType)

    def resolve_all_readers(self, info, **kwargs):
        return Reader.objects.all()


class CreateReader(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        email = graphene.String()

    reader = graphene.Field(ReaderType)

    def mutate(self, info, name, email):
        reader = Reader(name=name, email=email)
        reader.save()
        return CreateReader(reader=reader)


class Mutation(graphene.ObjectType):
    create_reader = CreateReader.Field()
