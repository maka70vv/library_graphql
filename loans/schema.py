from datetime import datetime
import graphene
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required, permission_required

from .models import Loan
from readers.models import Reader
from books.models import Book


class LoanType(DjangoObjectType):
    class Meta:
        model = Loan


class ReaderType(DjangoObjectType):
    class Meta:
        model = Reader


class Query(graphene.ObjectType):
    all_loans = graphene.List(LoanType)

    @login_required
    @permission_required('can_view_loan_list')
    def resolve_all_loans(self, info, **kwargs):
        return Loan.objects.all()

    @login_required
    @permission_required('can_view_loan_list')
    def resolve_reader_loans(self, info, reader_id):
        try:
            reader = Reader.objects.get(id=reader_id)
            current_loans = Loan.objects.filter(reader=reader, is_returned=False)
            return {
                "reader": reader,
                "loans": current_loans
            }
        except Reader.DoesNotExist:
            raise Exception("Читатель не найден.")

    @login_required
    def resolve_my_loans(self, info, **kwargs):
        current_user = info.context.user

        try:
            reader = Reader.objects.get(email=current_user.email)
            current_loans = Loan.objects.filter(reader=reader, is_returned=False)
            return {
                "reader": reader,
                "loans": current_loans
            }
        except Reader.DoesNotExist:
            raise Exception("Читатель не найден.")


class CreateLoan(graphene.Mutation):
    loan = graphene.Field(LoanType)

    class Arguments:
        book_id = graphene.ID(required=True)
        loan_end_date = graphene.Date(required=True)

    @login_required
    def mutate(self, info, book_id, loan_end_date):
        current_user = info.context.user

        reader, created = Reader.objects.get_or_create(
            email=current_user.email,
            name=f"{current_user.first_name if current_user.first_name else ''} "
                 f"{current_user.last_name if current_user.last_name else ''}",
        )

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise Exception("Book not found")

        loan = Loan.objects.create(
            book=book,
            reader=reader,
            loan_date=datetime.now().date(),
            loan_end_date=loan_end_date
        )
        return CreateLoan(loan=loan)


class ReturnBook(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        loan_id = graphene.ID(required=True)

    @login_required
    def mutate(self, info, loan_id):
        try:
            loan = Loan.objects.get(id=loan_id)

            if loan.is_returned:
                raise Exception("Книга уже возвращена.")

            loan.return_date = datetime.now().date()
            loan.is_returned = True
            loan.save()

            return ReturnBook(success=True)
        except Loan.DoesNotExist:
            raise Exception("Запись займа не найдена.")
        except Exception as e:
            raise Exception(str(e))


class Mutation(graphene.ObjectType):
    create_loan = CreateLoan.Field()
    return_book = ReturnBook.Field()
