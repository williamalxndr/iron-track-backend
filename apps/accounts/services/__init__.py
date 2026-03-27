from django.contrib.auth import get_user_model

User = get_user_model()


def create_user(data: dict) -> 'User':
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()

    if not username:
        raise ValueError('Username is required')
    if not password:
        raise ValueError('Password is required')
    if len(password) < 8:
        raise ValueError('Password must be at least 8 characters')
    if User.objects.filter(username=username).exists():
        raise ValueError('Username already taken')
    if email and User.objects.filter(email=email).exists():
        raise ValueError('Email already in use')

    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
