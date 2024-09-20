import graphene
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required, permission_required

from .business_logic.get_book_info import get_book_info
from .models import Book, Author, Rating


class AuthorType(DjangoObjectType):
    class Meta:
        model = Author


class BookType(DjangoObjectType):
    average_rating = graphene.Float()
    authors = graphene.List(AuthorType)

    class Meta:
        model = Book
        fields = ('id', 'title', 'authors', 'publication_year', 'isbn', 'average_rating')


class RatingType(DjangoObjectType):
    class Meta:
        model = Rating


class PaginatedBooks(graphene.ObjectType):
    books = graphene.List(BookType)
    total_count = graphene.Int()

    def __init__(self, books, total_count):
        self.books = books
        self.total_count = total_count


class Query(graphene.ObjectType):
    all_books = graphene.Field(PaginatedBooks, page=graphene.Int(), size=graphene.Int())
    all_authors = graphene.List(AuthorType)
    book_ratings = graphene.List(RatingType, book_id=graphene.ID())

    search_books = graphene.List(
        BookType,
        title=graphene.String(),
        author_name=graphene.String(),
        year_gte=graphene.Int(),
        year_lte=graphene.Int()
    )

    def resolve_all_books(self, info, page=1, size=10):
        books_list = Book.objects.all()
        paginator = Paginator(books_list, size)

        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)

        return PaginatedBooks(books=books, total_count=paginator.count)

    def resolve_book_ratings(self, info, book_id):
        return Rating.objects.filter(book_id=book_id)

    def resolve_all_authors(self, info, **kwargs):
        return Author.objects.all()

    def resolve_search_books(self, info, title=None, author_name=None, year_gte=None, year_lte=None):
        books = Book.objects.all()

        if title:
            books = books.filter(title__icontains=title)

        if author_name:
            books = books.filter(author__name__icontains=author_name)

        if year_gte is not None:
            books = books.filter(publication_year__gte=year_gte)

        if year_lte is not None:
            books = books.filter(publication_year__lte=year_lte)

        return books


class CreateRating(graphene.Mutation):
    class Arguments:
        book_id = graphene.ID(required=True)
        score = graphene.Int(required=True)

    rating = graphene.Field(RatingType)

    @login_required
    def mutate(self, info, book_id, score):
        current_user = info.context.user

        if score < 1 or score > 5:
            raise Exception("Оценка должна быть от 1 до 5")

        Rating.objects.update_or_create(
            book_id=book_id,
            user=current_user,
            defaults={'score': score}
        )

        rating = Rating.objects.get(book_id=book_id, user=current_user)
        return CreateRating(rating=rating)


class CreateAuthor(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        biography = graphene.String()
    author = graphene.Field(AuthorType)

    # @login_required
    def mutate(self, info, name, biography):
        if not info.context.user.has_permission_user('can_add_author'):
            raise Exception("У вас нет разрешения на выполнение этого действия.")
        else:
            author = Author(name=name, biography=biography)
            author.save()
            return CreateAuthor(author=author)


class CreateBook(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        author_ids = graphene.List(graphene.Int)
        publication_year = graphene.Int()
        isbn = graphene.String()

    book = graphene.Field(BookType)

    # @login_required
    def mutate(self, info, title, author_ids, publication_year, isbn):
        if not info.context.user.has_permission_user('can_add_book'):
            raise Exception("У вас нет разрешения на выполнение этого действия.")
        else:
            authors = Author.objects.filter(id__in=author_ids)
            book = Book(title=title, publication_year=publication_year, isbn=isbn)
            book.save()
            book.authors.set(authors)
            return CreateBook(book=book)


class CreateBookByISBN(graphene.Mutation):
    class Arguments:
        isbn = graphene.String(required=True)

    book = graphene.Field(BookType)

    # @login_required
    def mutate(self, info, isbn):
        if not info.context.user.has_permission_user('can_add_book'):
            raise Exception("У вас нет разрешения на выполнение этого действия.")
        else:
            book_info = get_book_info(isbn)
            if not book_info:
                raise Exception("Книга с таким ISBN не найдена.")

            author_names = book_info['authors']
            authors = []
            for name in author_names:
                author, created = Author.objects.get_or_create(name=name)
                authors.append(author)

            book = Book(
                title=book_info['title'],
                publication_year=book_info['publication_year'],
                isbn=isbn
            )
            book.save()
            book.authors.set(authors)

            return CreateBookByISBN(book=book)


class Mutation(graphene.ObjectType):
    create_book = CreateBook.Field()
    create_book_by_isbn = CreateBookByISBN.Field()
    create_rating = CreateRating.Field()
    create_author = CreateAuthor.Field()
