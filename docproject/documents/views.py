from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.conf import settings
import os
from .models import Document
from .forms import DocumentForm
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import DocumentSerializer


def home(request):
    return render(request, 'documents/home.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            messages.success(request, 'Registration successful! Welcome!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'documents/register.html', {'form': form})


@login_required
def document_list(request):
    documents = Document.objects.filter(owner=request.user).order_by('-uploaded_at')
    return render(request, 'documents/document_list.html', {'documents': documents})


@login_required
def document_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.owner = request.user
            document.save()
            messages.success(request, f'Document "{document.title}" uploaded successfully!')
            return redirect('document_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DocumentForm()
    return render(request, 'documents/document_upload.html', {'form': form})


@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk, owner=request.user)
    # Add helper attributes for template
    document.tags_list = [tag.strip() for tag in document.tags.split(',') if tag.strip()] if document.tags else []
    document.filename = os.path.basename(document.file.name) if document.file else 'Unknown'
    
    # Debug information
    if document.file:
        full_path = os.path.join(settings.MEDIA_ROOT, document.file.name)
        document.file_exists = os.path.exists(full_path)
        document.full_path = full_path
        document.file_size = document.file.size if hasattr(document.file, 'size') else 'Unknown'
    else:
        document.file_exists = False
        document.full_path = 'No file'
        document.file_size = 'No file'
    
    return render(request, 'documents/document_detail.html', {'document': document})


@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    results = []
    
    if query:
        results = Document.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query),
            owner=request.user
        ).order_by('-uploaded_at')
        
        # Add tags_list to each result for template
        for result in results:
            result.tags_list = [tag.strip() for tag in result.tags.split(',') if tag.strip()] if result.tags else []
    
    context = {
        'results': results, 
        'query': query,
        'total_results': len(results) if query else 0
    }
    return render(request, 'documents/search.html', context)


@login_required
def download_document(request, pk):
    """Custom download view with proper error handling"""
    document = get_object_or_404(Document, pk=pk, owner=request.user)
    
    if not document.file:
        messages.error(request, 'No file associated with this document.')
        return redirect('document_detail', pk=pk)
    
    file_path = document.file.path
    
    if not os.path.exists(file_path):
        messages.error(request, 'File not found on server. It may have been moved or deleted.')
        return redirect('document_detail', pk=pk)
    
    try:
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    except Exception as e:
        messages.error(request, f'Error downloading file: {str(e)}')
        return redirect('document_detail', pk=pk)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for documents
    """
    queryset = Document.objects.all()  # This is required for the router
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'description', 'tags']
    filterset_fields = ['uploaded_at']

    def get_queryset(self):
        """Return documents for the current user only"""
        return Document.objects.filter(owner=self.request.user).order_by('-uploaded_at')

    def perform_create(self, serializer):
        """Set the owner to the current user when creating a document"""
        serializer.save(owner=self.request.user)