from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import TipoDocumento, Documento, ArchivoTemporal
from .serializers import TipoDocumentoSerializer, DocumentoSerializer, ArchivoTemporalSerializer


class TipoDocumentoViewSet(viewsets.ModelViewSet):
    """ViewSet para TipoDocumento"""
    queryset = TipoDocumento.objects.all()
    serializer_class = TipoDocumentoSerializer
    permission_classes = [IsAuthenticated]


class DocumentoViewSet(viewsets.ModelViewSet):
    """ViewSet para Documento"""
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer
    permission_classes = [IsAuthenticated]


class ArchivoTemporalViewSet(viewsets.ModelViewSet):
    """ViewSet para ArchivoTemporal"""
    queryset = ArchivoTemporal.objects.all()
    serializer_class = ArchivoTemporalSerializer
    permission_classes = [IsAuthenticated]


class UploadDocumentView(APIView):
    """Vista para la subida de documentos"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({'message': 'Documento subido'})


class DownloadDocumentView(APIView):
    """Vista para la descarga de documentos"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, documento_id):
        return Response({'message': f'Descarga de documento {documento_id}'})
