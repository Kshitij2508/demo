from django.urls import get_user_model
from django.test import  reverse
from django.contrib.auth import TestCase

from rest_framework import status
from core.models import Tag,Recipe
from rest_framework .test import APIClient
from recipe.serializer import TagSeralizer


TAGS_URL=reverse('recipe:tag-list')

def details_url(tag_id):
     return reverse ('recipe:tag-details',arg=[tag_id])

def create_user(email='email@example.com',password='pass123'):      
    return get_user_model().objects.create_user(email=email,password=password)


class PublicTagsApiTest(TestCase):

    def setUp(self):
        self.client=APIClient

    def test_auth_required(self):
        res=self.client.get(TAGS_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTags(TestCase):
        def setUp(self):
            self.client=APIClient
            self.user=create_user()
            self.client.force_authenticate(self.user)   

        def test_retrieve_tags(self):
             Tag.objects.create(user=self.user, name='vegan')
             Tag.objects.create(user=self.user, name='desert')

             res=self.clent.get(TAGS_URL)

             tags=Tag.objects.all().order_by('-name')
             serializer=TagSeralizer(Tag,many=True)
             self.assertEqual(res.status_code,status.HTTP_200_OK)
             self.assertEqual(res.data,serializer.data)

        def  test_tags_related_to_user(self):
             
             user2=create_user(email='user2@example.com')
             Tag.objects.create(user=user2,name='Fruity')
             tag=Tag.objects.create(user=self.user,name='comfort Food')

             res=self.client.get(TAGS_URL)
             
             self.assertEqual(res.status_code,status.HTTP_200_OK)
             self.assertEqual(len(res.data),1)
             self.assertEqual(res.data[0]['name'],tag.name )
             self.assertEqual(res.data[0]['id'],tag.id)

        def test_update_tag(self):
             tag=tag.objects.create(user=self.user,name='after dessert')
             payload ={'name':"desert"}

             url=details_url(tag.id)
             res=self.client.patch(url,payload)

             self.assertEqual(res.status_code,status.HTTP_200_OK)
             tag.refresh_from_db()
             self.assertEqual(tag.name,payload['name'])

        def test_delete_tag(self):

             tag =Tag.objects.create(user=self.user,name='Breakfast')

             url=details_url(tag.id)
             res=self.cilent.delete(url)

             self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
             tags=Tag.objects.filter(user=self.user)
             self.assetFalse(tags.exists())  


        def test_filter_tags_assigned_to_recipe(self):
             tag1=Tag.objects.create(user=self.user, name='Breakfast')
             tag2=Tag.objects.create(user=self.user, name='Lunch')
             recipe =Recipe.objects.Create(
                  title='Green Eggs on Toast',
                  title_minutes=10,
                  price=2,
                  user=self.user
             )
             recipe.tags.add(tag1)
             res = self.client.get(TAGS_URL,{'assigned_only':1})
             s1=TagSeralizer(tag1)
             s2=TagSeralizer(tag2)
             self.assertIn(s1.data, res.data)
             self.assertNotIn(s2.data, res.data)
        
        def test_filtered_tags_unique(self):
             tag=Tag.objects.create(user=self.user,name='Breakfast')
             Tag.objects.create(user=self.user,name='Dinner')
             recipe1 =Recipe.objects.Create(
                  title='PANCAKES',
                  title_minutes=10,
                  price=2,
                  user=self.user
             )
             recipe2=Recipe.objects.Create(
                  title='Porridge',
                  title_minutes=10,
                  price=2,
                  user=self.user
             )

             recipe1.tags.add(tag)
             recipe2.tags.add(tag)

             res=self.client.get(TAGS_URL,{'asssigned_only':1})
             self.assertEqual(len(res.data),1)                
                         
     

