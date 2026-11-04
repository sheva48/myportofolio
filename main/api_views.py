from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Education, Project
from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly, IsPortfolioOwnerOrReadOnly
from main.serializers import EducationSerializer, ProjectSerializer


def _list(request, model, serializer_class, search_field, search_param):
    if request.method in ("GET", "HEAD"):
        objects = model.objects.prefetch_related("starred_by").order_by(search_field, "id")
        query = request.query_params.get(search_param, "").strip()
        if query:
            objects = objects.filter(**{f"{search_field}__icontains": query})
        return Response(serializer_class(objects, many=True, context={"request": request}).data)
    serializer = serializer_class(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def _detail(request, model, serializer_class, object_id):
    obj = get_object_or_404(model.objects.prefetch_related("starred_by"), pk=object_id)
    if request.method in ("GET", "HEAD"):
        return Response(serializer_class(obj, context={"request": request}).data)
    if request.method == "DELETE":
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = serializer_class(
        obj, data=request.data, partial=request.method == "PATCH", context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


def _star(request, model, serializer_class, object_id):
    obj = get_object_or_404(model, pk=object_id)
    if obj.starred_by.filter(pk=request.user.pk).exists():
        obj.starred_by.remove(request.user)
    else:
        obj.starred_by.add(request.user)
    return Response(serializer_class(obj, context={"request": request}).data)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_list(request):
    return _list(request, Project, ProjectSerializer, "title", "title")


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_detail(request, project_id):
    return _detail(request, Project, ProjectSerializer, project_id)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_star(request, project_id):
    return _star(request, Project, ProjectSerializer, project_id)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def education_list(request):
    return _list(request, Education, EducationSerializer, "institution_name", "institution")


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def education_detail(request, education_id):
    return _detail(request, Education, EducationSerializer, education_id)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def education_star(request, education_id):
    return _star(request, Education, EducationSerializer, education_id)
