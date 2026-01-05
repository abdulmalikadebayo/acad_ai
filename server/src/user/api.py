from django.contrib.auth import authenticate, login

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile, User
from .serializers import ProfileSerializer, UserSerializer


class LoginAPIView(APIView):

    def post(self, request, *args, **kwargs):
        user = authenticate(
            username=request.data.get("email", "").strip().lower(),
            password=request.data.get("password", ""),
        )
        if not user:
            return Response(
                {"error": "Invalid e-mail or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile: Profile = user.profile

        login(request, user)

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "profile": ProfileSerializer(profile).data,
                "token": token.key,
            },
            status=status.HTTP_200_OK,
        )


class RegisterAPIView(APIView):
    serializer_class = ProfileSerializer

    @staticmethod
    def sanitize_string(s: str) -> str:
        return (s or "").strip().lower()

    @staticmethod
    def split_fullname(full: str) -> tuple[str, str]:
        parts = full.split()
        if len(parts) == 1:
            return parts[0], ""
        first = parts[0]
        last = " ".join(parts[1:])
        return first, last

    def post(self, request):
        data = request.data

        try:
            email = self.sanitize_string(data["email"])
            password = data["password"]
            full_name = data["full_name"].strip()
        except KeyError as miss:
            return Response(
                {"error": f"Missing field: {miss.args[0]}"},
                status=400,
            )

        if User.objects.filter(username=email).exists():
            return Response({"error": "User already exists"}, status=400)

        first_name, last_name = self.split_fullname(full_name)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        profile, profile_created = Profile.objects.get_or_create(user=user)
        if not profile_created:
            return Response({"error": "Profile already exists"}, status=400)

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "profile": ProfileSerializer(profile).data,
                "token": token.key,
            },
            status=201,
        )


class RetrieveProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            data=ProfileSerializer(request.user.profile).data,
            status=200,
        )
