from django.db.models import Q
from django.contrib.auth.hashers import check_password
from sendhut.accounts.models import User


class UsernamePhoneAuthentication:

    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.filter(
                Q(username=username) |
                Q(phone=username) |
                Q(email=username))
            user = user[0] if user else None
        except User.DoesNotExist:
            return None

        if user:
            # Check password of the user we found
            if check_password(password, user.password):
                return user

        # No user was found, return None - triggers default login failed
        return None

    # Required for the backend to work properly - unchanged in most scenarios
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
