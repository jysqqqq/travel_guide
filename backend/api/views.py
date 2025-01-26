from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import F
from .models import (
    Destination, Attraction, Itinerary, ItineraryDay,
    ItineraryItem, Favorite, Tag, Comment
)
from .serializers import (
    DestinationSerializer, AttractionSerializer, ItinerarySerializer,
    ItineraryDaySerializer, ItineraryItemSerializer, FavoriteSerializer,
    TagSerializer, CommentSerializer
)
from rest_framework.views import APIView

class TagViewSet(viewsets.ModelViewSet):
    """标签视图集"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'category']

class CommentViewSet(viewsets.ModelViewSet):
    """评论视图集"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.all()
        destination_id = self.request.query_params.get('destination', None)
        attraction_id = self.request.query_params.get('attraction', None)

        if destination_id:
            queryset = queryset.filter(destination_id=destination_id)
        elif attraction_id:
            queryset = queryset.filter(attraction_id=attraction_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DestinationViewSet(viewsets.ModelViewSet):
    """目的地视图集"""
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'location', 'category', 'tags__name']

    @action(detail=False)
    def popular(self, request):
        """获取热门目的地（按浏览量排序）"""
        popular_destinations = self.get_queryset().order_by('-views_count')[:3]
        serializer = self.get_serializer(popular_destinations, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 增加浏览量
        instance.views_count = F('views_count') + 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True)
    def attractions(self, request, pk=None):
        """获取目的地下的所有景点"""
        destination = self.get_object()
        attractions = destination.attractions.all()
        serializer = AttractionSerializer(attractions, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def comments(self, request, pk=None):
        """获取目的地的评论"""
        destination = self.get_object()
        comments = destination.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

class AttractionViewSet(viewsets.ModelViewSet):
    """景点视图集"""
    queryset = Attraction.objects.all()
    serializer_class = AttractionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'location', 'category', 'tags__name']

    def get_queryset(self):
        queryset = Attraction.objects.all()
        destination_id = self.request.query_params.get('destination', None)
        category = self.request.query_params.get('category', None)
        tag = self.request.query_params.get('tag', None)

        if destination_id:
            queryset = queryset.filter(destination_id=destination_id)
        if category:
            queryset = queryset.filter(category=category)
        if tag:
            queryset = queryset.filter(tags__name=tag)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 增加浏览量
        instance.views_count = F('views_count') + 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True)
    def comments(self, request, pk=None):
        """获取景点的评论"""
        attraction = self.get_object()
        comments = attraction.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

class ItineraryViewSet(viewsets.ModelViewSet):
    """行程视图集"""
    serializer_class = ItinerarySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Itinerary.objects.filter(
                user=self.request.user
            ) | Itinerary.objects.filter(is_public=True)
        return Itinerary.objects.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ItineraryDayViewSet(viewsets.ModelViewSet):
    """行程日程视图集"""
    serializer_class = ItineraryDaySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ItineraryDay.objects.filter(
            itinerary__user=self.request.user
        )

    def perform_create(self, serializer):
        itinerary = get_object_or_404(
            Itinerary,
            id=self.request.data.get('itinerary'),
            user=self.request.user
        )
        serializer.save(itinerary=itinerary)

class ItineraryItemViewSet(viewsets.ModelViewSet):
    """行程项目视图集"""
    serializer_class = ItineraryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ItineraryItem.objects.filter(
            day__itinerary__user=self.request.user
        )

    def perform_create(self, serializer):
        day = get_object_or_404(
            ItineraryDay,
            id=self.request.data.get('day'),
            itinerary__user=self.request.user
        )
        serializer.save(day=day)

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 测试视图
class TestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({"message": "Hello, World!"})
