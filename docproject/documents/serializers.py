from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'description', 'file', 'uploaded_at', 'owner', 'tags']
        read_only_fields = ['owner', 'uploaded_at']