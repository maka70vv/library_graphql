from django.db import models

from users.models import User


class Reader(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Электронная почта")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Читатель"
        verbose_name_plural = "Читатели"
