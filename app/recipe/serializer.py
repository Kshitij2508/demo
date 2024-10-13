from rest_framework import serializers

from core.models import Recipe,Tag


class TagSerializer(serializers.ModelSerializer):   
    class Meta: 
        model=Tag
        fields=['id','name']
        read_only_fields=["id"] 




class RecipeSerializer(serializers.ModelSerializer):

    tags =TagSerializer(many=True, required=False)

    class Meta:
        model=Recipe
        fields=['id','title','time_minutes','price','tags']
        read_only_fields=['id']

    def get_or_create_tags(self,tags,recipe):
        auth_user=self.context['request'].user
        for tag in tags:
            tag_obj, created=Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )    
            recipe.tags.add(tag_obj)        

    def create(self,validate_data):

        tags=validate_data.pop('tags',[])
        recipe=Recipe.objects.create(**validate_data)
        auth_user=self.context['request'].user  
        for tag in tags:
            tag_obj, created=Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )    
            recipe.tags.add(tag_obj)
        return recipe    
    
    def update(self,instance,validate_data):
        tags=validate_data.pop('tag',[])
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags,instance)

        for attr,value in validate_data.item():
            setattr(instance,attr,value)
            instance.save()
            return instance


class RecipeDetailSerializer(RecipeSerializer):

    class Meta(RecipeSerializer.Meta):
        fields=RecipeSerializer.Meta.fields + ['description']


class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=Recipe
        fields=['id','image']
        read_only_field='id'
        extra_kwargs={'image':{'required':'True'}}
