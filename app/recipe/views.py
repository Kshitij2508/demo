from django.shortcuts import render

from drf_spectacular.utils import extend_schema_view , extend_schema,OpenApiParameter,OpenApiTypes
# Create your views here.
from rest_framework import viewsets,mixins,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from  core.models import Recipe,Tag
from  recipe import serializer


@extend_schema_view(

   list=extend_schema(
       parameters=[
           OpenApiParameter(
               'tags',
               OpenApiTypes.STR,
               description='comma'
            ),
           
       ]
   )



)

class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class=serializer.RecipeSerializer
    authetication_class=[TokenAuthentication]
    queryset=Recipe.objects.all()
    permission_class=[IsAuthenticated]


    def _params_to_ints(self, qs):

        return [int(str_id) for str_id in qs.split(',') ]

    def get_querset(self):
        tags=self.request.query_params.get('tags')
        queryset=self.queryset
        if tags:
            tags_ids =self._params_to_ints(tags)
            queryset=queryset.filter(tags__id__in=tags_ids)
        return queryset.filter(user=self.request.user).order_by('-id').distinct()   
    
    def get_serializer_class(self):
        if self.action== 'list':
            return serializer.RecipeDetailSerializer    
        elif self.action== 'upload_image':
            
            return serializer.RecipeImageSerializer  
        
        return self.serializer_class
    
    def perform_create(self,serializer):
        serializer.save(user=self.request.user)


    @action(methods=['POST'],detail=True,url_path='upload_image')
    def upload_image(self,request,pk=None):
        recipe=self.get_object() 
        serializer=self.get_serializer(recipe,data=request.data)       
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK )
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST )

class BaseRecipeAttrViewset(mixins.DestroyModelMixin,mixins.UpdateModelMixin,mixins.ListModelMixin,viewsets.GenericViewSet):

    authentication_classes=[TokenAuthentication]
    Permission_classes=[IsAuthenticated]

    def get_queryset(self):
         
         assigned_only=bool(
             int(self.request.query_params.get)
         )
         queryset=self.queryset
         if assigned_only:
             queryset=queryset.filter(recipe__isnull=False)  
         return queryset.filter(user=self.request.user).order_by('-name').distinct()


class TagViewSet(mixins.DestroyModelMixin,mixins.UpdateModelMixin,mixins.ListModelMixin,viewsets.GenericViewSet):

    serializer_class=serializer.TagSerializer
    queryset =Tag.objects.all() 
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]

    def get_query(self):
        return self.queryset.filter(uer=self.request.user).order_by ('-name')