from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = response.data.pop('refresh')

        response.set_cookie(
            key='refresh_token',
            value=refresh,
            httponly=True,
            secure=not settings.DEBUG,  # HTTPS only in production
            samesite='Strict',
            max_age=60 * 60 * 24 * 7,  # 7 days, matches SIMPLE_JWT setting
            path='/api/token/refresh/',  # only sent to the refresh endpoint
        )

        return response

    
class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'No refresh token provided'}, status=400)

        request.data['refresh'] = refresh_token
        return super().post(request, *args, **kwargs)
    

class CookieTokenLogoutView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()  # Blacklist the token to invalidate it
            except (TokenError, InvalidToken):
                pass  # Token is invalid or already blacklisted

        response = Response({'detail': 'Logged out successfully'}, status=200)
        response.delete_cookie('refresh_token', path='/api/token/refresh/')
        return response