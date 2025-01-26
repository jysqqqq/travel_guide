from rest_framework import serializers
from wagtail.images.models import Image
from .models import Destination, Attraction, AttractionImage, Comment, Favorite, Tag, Itinerary, ItineraryDay, ItineraryItem
from django.conf import settings
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ImageSerializer(serializers.ModelSerializer):
    """图片序列化器"""
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Image
        fields = ['id', 'title', 'url']
        
    def get_url(self, obj):
        if not obj:
            return None
        try:
            return settings.MEDIA_URL + obj.file.name
        except Exception as e:
            print(f"获取图片URL时出错: {str(e)}")
            return None

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'category']

class CommentSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'user_detail', 'destination', 'attraction',
            'content', 'rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user']

class AttractionImageSerializer(serializers.ModelSerializer):
    """景点图片序列化器"""
    image = ImageSerializer()
    
    class Meta:
        model = AttractionImage
        fields = ['id', 'image', 'title', 'description', 'order']

class AttractionSerializer(serializers.ModelSerializer):
    """景点序列化器"""
    cover_image = ImageSerializer()
    images = AttractionImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Attraction
        fields = [
            'id', 'name', 'description', 'destination', 
            'cover_image', 'images', 'location', 'latitude', 
            'longitude', 'opening_hours', 'ticket_price', 
            'category', 'tags', 'rating', 'views_count', 
            'recommended_duration', 'comments'
        ]

class DestinationSerializer(serializers.ModelSerializer):
    cover_image = ImageSerializer()
    tags = TagSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Destination
        fields = [
            'id', 'title', 'description', 'long_description', 'cover_image', 'location',
            'province', 'country', 'latitude', 'longitude', 'category', 'tags', 'best_season',
            'views_count', 'rating', 'comments'
        ]

class ItineraryItemSerializer(serializers.ModelSerializer):
    attraction_detail = AttractionSerializer(source='attraction', read_only=True)

    class Meta:
        model = ItineraryItem
        fields = [
            'id', 'attraction', 'attraction_detail', 'custom_location',
            'start_time', 'end_time', 'description', 'transportation'
        ]

class ItineraryDaySerializer(serializers.ModelSerializer):
    items = ItineraryItemSerializer(many=True, read_only=True)

    class Meta:
        model = ItineraryDay
        fields = ['id', 'day_number', 'date', 'note', 'items']

class ItinerarySerializer(serializers.ModelSerializer):
    days = ItineraryDaySerializer(many=True, read_only=True)
    user_detail = UserSerializer(source='user', read_only=True)
    destination_detail = DestinationSerializer(source='destination', read_only=True)

    class Meta:
        model = Itinerary
        fields = [
            'id', 'title', 'description', 'user', 'user_detail',
            'destination', 'destination_detail', 'start_date', 'end_date',
            'is_public', 'created_at', 'updated_at', 'days'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

class FavoriteSerializer(serializers.ModelSerializer):
    attraction_detail = AttractionSerializer(source='attraction', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'attraction', 'attraction_detail', 'username', 'created_at', 'note']
        read_only_fields = ['user'] 