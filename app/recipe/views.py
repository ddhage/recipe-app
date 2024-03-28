"""
Views for the recipe APIs.
"""

from drf_spectacular.utils import(
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    mixins,)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag,
    Ingredient,
    )
from recipe import serializers

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tag IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter',
            ),
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags_id_in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients_id_in=ingredient_ids)
            
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()
        
    
    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer
        
        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)
        
class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin, 
                 mixins.ListModelMixin, 
                 viewsets.GenericViewSet):
    """Base view set for handling recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """filter queryset to authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
    
    
class TagViewSet(BaseRecipeAttrViewSet):
    """manage tags in the databse"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    
    
    
    
class IngredientViewSet(BaseRecipeAttrViewSet):
    """manage ingre in the db"""  
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    
    
    

        
        