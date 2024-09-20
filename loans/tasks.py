from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Loan


@shared_task
def send_overdue_loans():
    today = timezone.now().date()
    overdue_loans = Loan.objects.filter(loan_end_date__lt=today, is_returned=False)

    for loan in overdue_loans:
        subject = f"Просроченный займ: {loan.book.title}"
        message = (f"Уважаемый {loan.reader.name},\n"
                   f"\nВаш займ книги '{loan.book.title}' просрочен с {loan.loan_end_date}."
                   f"\nПожалуйста, верните книгу как можно скорее.")
        send_mail(subject, message, 'from@example.com', [loan.reader.email])
