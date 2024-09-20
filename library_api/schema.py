import graphene
import books.schema
import readers.schema
import loans.schema
import users.schema


class Query(
    books.schema.Query,
    readers.schema.Query,
    loans.schema.Query,
    users.schema.Query,
    graphene.ObjectType):
    pass


class Mutation(
    books.schema.Mutation,
    readers.schema.Mutation,
    loans.schema.Mutation,
    users.schema.Mutation,
    graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
