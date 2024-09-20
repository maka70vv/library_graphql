from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, GroupManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class UserPermission(models.Model):
    codename = models.CharField(
        max_length=255, verbose_name='Кодовое имя', unique=True)
    description = models.TextField(verbose_name='Описание', null=True)
    name = models.CharField(max_length=100, verbose_name='Название', null=True)

    class Meta:
        verbose_name = 'Право доступа'
        verbose_name_plural = 'Права доступа'

    def __str__(self):
        return self.codename


class UserGroup(models.Model):
    name = models.CharField(max_length=150, unique=True)
    permissions = models.ManyToManyField(
        UserPermission,
        verbose_name='Права доступа',
        blank=True,
    )

    objects = GroupManager()

    class Meta:
        verbose_name = 'Группа пользователей'
        verbose_name_plural = 'Группы пользователей'

    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    groups = models.ManyToManyField(
        UserGroup,
        related_name='user_groups',
        blank=True,
        verbose_name="Группы пользователя"
    )
    extra_permissions = models.ManyToManyField(
        UserPermission,
        verbose_name='Права доступа пользователя',
        blank=True
    )

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.saved = False

    def has_permission_user(self, perm: str, obj=None) -> bool:
        if self.is_superuser:
            return True

        user_groups = self.groups.all().prefetch_related('permissions')
        for group in user_groups:
            if group.permissions.filter(codename=perm).exists():
                return True
        for permission in self.extra_permissions.all():
            if permission.codename == perm:
                return True
        return False
