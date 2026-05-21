"""
users/views.py

Authentication views using Django's built-in session-based auth.
Sessions are stored server-side; the client holds a session cookie.
All views under /api/v1/auth/.

Why session auth instead of JWT?
  Single-domain SPA, no mobile client — sessions are simpler and more
  secure (HttpOnly cookies, no token storage in JS).
"""

from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, UserSerializer


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CsrfView(APIView):
    """
    GET /api/v1/auth/csrf/

    Seeds the csrftoken cookie so the SPA can attach X-CSRFToken on its first
    mutating request (e.g. login). Without this, a fresh browser has no CSRF
    cookie and the initial login POST is rejected with 403.

    Response:
        200 -- {'detail': 'CSRF cookie set'} and sets the csrftoken cookie
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'detail': 'CSRF cookie set'})


class LoginView(APIView):
    """
    POST /api/v1/auth/login/

    Authenticates the user and creates a Django session.
    No authentication required to call this endpoint.

    Request body:
        username (str) -- existing username
        password (str) -- plaintext password (transmitted over HTTPS in production)

    Response:
        200 -- {id, username, email, date_joined} and sets session cookie
        401 -- {'detail': 'Invalid credentials.'}
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        login(request, user)
        return Response(UserSerializer(user).data)


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/

    Destroys the current session. Requires an active session cookie.

    Response:
        200 -- {'detail': 'Logged out.'}
    """
    def post(self, request):
        logout(request)
        return Response({'detail': 'Logged out.'})


class RegisterView(APIView):
    """
    POST /api/v1/auth/register/

    Creates a new user account and immediately logs them in.
    No authentication required to call this endpoint.

    Request body:
        username (str)          -- desired username (must be unique)
        email    (str, optional)-- email address
        password (str)          -- minimum 8 characters

    Response:
        201 -- {id, username, email, date_joined} and sets session cookie
        400 -- validation errors (e.g. duplicate username, short password)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    """
    GET /api/v1/auth/me/

    Returns profile data for the currently authenticated user.
    Used by the frontend on page load to restore auth state from the session cookie.

    Response:
        200 -- {id, username, email, date_joined}
        403 -- if no valid session cookie is present
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
