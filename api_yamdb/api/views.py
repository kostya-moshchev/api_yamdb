from django.core.mail import send_mail
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import UserSerializer
from reviews.models import User
from .utils import generate_confirmation_code


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(**serializer.validated_data)
            headers = self.get_success_headers(serializer.data)
            user_serializer = UserSerializer(user)
            code = generate_confirmation_code()
            send_mail(
               'Код подтверждения',
               f'Ваш код подтверждения: {code}',
               'noreply@yamdb.com',
               [user.email],
               fail_silently=False,
            )
            return Response(
                user_serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
