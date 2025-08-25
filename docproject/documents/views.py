from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Document
from .forms import DocumentForm
from rest_framework import viewsets, permissions, filters
from .serializers import DocumentSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm

def home(request):
    return render(request, 'documents/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'documents/register.html', {'form': form})


@login_required
def document_list(request):
    documents = Document.objects.filter(owner=request.user)
    return render(request, 'documents/document_list.html', {'documents': documents})

@login_required
def document_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.owner = request.user
            document.save()
            return redirect('document_list')
    else:
        form = DocumentForm()
    return render(request, 'documents/document_upload.html', {'form': form})

@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk, owner=request.user)
    document.tags_list = [tag.strip() for tag in document.tags.split(',')] if document.tags else []
    document.filename = document.file.name.split('/')[-1]
    return render(request, 'documents/document_detail.html', {'document': document})

@login_required
def search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = Document.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query),
            owner=request.user
        )
    return render(request, 'documents/search.html', {'results': results, 'query': query})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'documents/register.html', {'form': form})

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'description', 'tags']
    filterset_fields = ['owner', 'uploaded_at']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)