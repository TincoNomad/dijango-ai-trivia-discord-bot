"""
Factories for user-related tests.
Using Factory Boy to generate test data.
"""

import factory
from django.contrib.auth import get_user_model
from api.utils.logging_utils import log_exception

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    """Factory para crear instancias de prueba de User"""
    
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    username = factory.Sequence(lambda n: f'testuser_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    role = 'user'
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override para usar create_user o create_superuser según corresponda"""
        manager = cls._get_manager(model_class)
        
        # Extraer flags importantes
        is_superuser = kwargs.pop('is_superuser', False)
        is_staff = kwargs.pop('is_staff', False)
        role = kwargs.get('role', 'user')
        password = kwargs.pop('password', 'testpass123')
        
        # Crear usuario según sus permisos
        if is_superuser or role == 'admin':
            user = manager.create_superuser(
                *args,
                password=password,
                **kwargs
            )
        else:
            user = manager.create_user(
                *args,
                password=password,
                **kwargs
            )
        
        # Asignar permisos adicionales
        user.is_staff = is_staff or is_superuser
        user.is_superuser = is_superuser
        user.save()
        
        return user

    @classmethod
    @log_exception
    def create_admin(cls, **kwargs):
        """Crear usuario administrador"""
        kwargs.update({
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True
        })
        return cls.create(**kwargs)

    @classmethod
    @log_exception
    def create_regular_user(cls, **kwargs):
        """Crear usuario regular"""
        kwargs.update({
            'role': 'user',
            'is_staff': False,
            'is_superuser': False
        })
        return cls.create(**kwargs)

    @classmethod
    @log_exception
    def create_unauthenticated_user(cls, **kwargs):
        """Crear usuario sin autenticar"""
        kwargs.update({
            'is_authenticated': False,
            'password': '',
            'email': ''
        })
        return cls.create(**kwargs)

    @classmethod
    @log_exception
    def create_batch_users(cls, size=3, **kwargs):
        """Crear múltiples usuarios"""
        return cls.create_batch(size=size, **kwargs)