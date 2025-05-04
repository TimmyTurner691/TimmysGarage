from rest_framework import serializers
from .models import Game, Genre, Platform

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ['id', 'name', 'manufacturer']

class GameSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    platform = PlatformSerializer(many=True, read_only=True)
    
    class Meta:
        model = Game
        fields = [
            'id', 'title', 'description', 'release_date', 
            'price', 'stock', 'genre', 'platform', 'image', 'rating'
        ]