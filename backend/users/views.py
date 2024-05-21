from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from djoser.views import UserViewSet

from users.models import Subscription
from users.serializers import AvatarSerializer, MyUserSerializer
from recipes.serializers import SubscriptionSerializer
from recipes.permissions import IsOwner


User = get_user_model()


class MyUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    pagination_class = None

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        permission_classes=[IsOwner]
    )
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(subscriber=request.user)
        paginator = LimitOffsetPagination()
        paginator.default_limit = 6
        paginated_subscriptions = paginator.paginate_queryset(subscriptions, request)
        serializer = SubscriptionSerializer(paginated_subscriptions, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'patch', 'delete'],
        url_path='me/avatar',
        url_name='avatar',
        permission_classes=[IsAuthenticated])
    def update_avatar(self, request):
        if request.method == 'PATCH' or request.method == 'PUT':
            serializer = AvatarSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            request.user.avatar.delete(save=True)
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def subscribe(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if request.user == user:
            return JsonResponse(
                {'error': 'Вы не можете подписаться на самого себя.'},
                status=400
            )
        subscription_exists = Subscription.objects.filter(
            subscriber=request.user, subscription=user
        ).exists()
        if not subscription_exists:
            subscription = Subscription.objects.create(
                subscriber=request.user, subscription=user
            )
            serializer = SubscriptionSerializer(subscription)
            return JsonResponse(serializer.data, status=201)
        else:
            return JsonResponse(
                {'error': 'Вы уже подписаны на этого пользователя.'},
                status=400
            )

    elif request.method == 'DELETE':
        subscription = get_object_or_404(
            Subscription, subscriber=request.user,
            subscription=user
        )
        if subscription:
            subscription.delete()
            return JsonResponse(
                {'message': 'Подписка удалена успешно.'},
                status=201
            )
        else:
            return JsonResponse(
                {'error': 'Вы не подписаны на этого пользователя.'},
                status=400
            )
