from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
import os
import tempfile

from PIL import Image

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe,Tag

from recipe.serializer import RecipeSerializer , RecipeDetailSerializer     
RECIPES_URL =reverse('recipe:recipe-list')


def detail_url(recipe_id):
      return reverse('recipe:recipe-list',args=[recipe_id])


def image_upload_url(recipe_id):
     return reverse('recipe:recipe-upload-image',args=[recipe_id])




def create_user(**params):
     return get_user_model().objects.create(**params)

def create_recipe(user,**params):
    defaults={
        'title':'panner',
        'time_minutes':22,
        'price':25,
        'description':'sample discription',
        'url':'http://example.com/recipe.pdf'

    }
    defaults.update(params)
    recipe =recipe.objects.create(user=user,**defaults)
    return recipe   

class PublicRecipeAPITests(TestCase):
        def setUp(self):
              self.client=APIClient()
              self.user=create_user(email='user@example.com',password='test123')
              self.user=get_user_model().objects.crerate_user(
                   'user@exmaple.com'
                   'testpass123'
              )
              self.client.force_authenticate(self.user)
        
        def test_auth_required(self):
            res=self.client.get(RECIPES_URL)
            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)  


class PrivateRecipeAPITests(TestCase):
 
        def setUp(self):
              self.client=APIClient
              self.user=get_user_model().objects.client(
                    'user@example.com'
                    'Testpass123'
              )
              self.client.force_authenticate(self.user)

        def test_retrive_recipes(self):
              create_recipe(user=self.user)
              create_recipe(user=self.user)

              res=self.client.get(RECIPES_URL)
              recipes=Recipe.objects.all().order_by('-id')
              serializer=RecipeSerializer(recipes,many=True)
              self.assertEqual(res.status_code,status.HTTP_200_OK)     
              self.assertEqual(res.data,serializer.data)         
        
        def  test_recipe_list_limited_to_user(self):
            other_user=create_user(
                 email= 'other@example.com',
                  password='test123'
            )
            create_recipe(user=other_user)
            create_recipe(user=self.user)

            res=self.client.get(RECIPES_URL)
            recipes=Recipe.objects.all().order_by('-id')
            serializer=RecipeSerializer(recipes,many=True)
            self.assertEqual(res.status_code,status.HTTP_200_OK)     
            self.assertEqual(res.data,serializer.data)         
        
        def test_get_recipe_detail(self):

            recipe=create_recipe(user=self.user)
            url=detail_url(recipe.id)           
            res=self.client.get(url)

            serializer=RecipeDetailSerializer(recipe)
            self.assertEqual(res.data,serializer.data)   

        def test_create_recipe(self):
            payload={
                   'title':'paneeer',
                    'time_minutes':30,
                    'price':25
              }    

            res = self.client.post(RECIPES_URL,payload)
            self.assertEqual(res.status_code,status.HTTP_201_CREATED)
            recipe=Recipe.objects.get(id=res.data['id'])
            for k,v in payload.items():
                 self.asssertEqual(getattr(recipe ,k),v)
            self.assertEqual(recipe.user,self.user)

        def test_partial_update(self):
             original_link='http://example.com/recipe.pdf'
             recipe=create_recipe(
                  user=self.user,
                  title='sample recipe',
                  link=original_link      
             )
             payload={'title':'new recipe'}
             url=detail_url(recipe.id)
             res=self.client.patch(url,payload)

             self.assertEqual(res.status_code,status.HTTP_200_OK)
             self.assertEqual(recipe.title,payload['title'])
             self.assertEqual(recipe.link,original_link)
             self.assertEqual(recipe.user,self.user)
        
        def test_full_update(self):
             recipe=create_recipe(
                  user=self.user,
                  title="sample recipe",
                  description="sample recipe",
                  link='http://example.com/recipe.pdf'
             )     

             payload={
                  'title':'',
                  'description':'',
                  'link':'http://example.com/recipe.pdf',
                  'time_minute':10,
                  'price':20
            }
             url =detail_url(recipe.id)
             res=self.client.put(url,payload) 
             
             self.assertEqual(res.status_code,status.HTTP_200_OK)
             recipe.refresh_from_db()
             for k,v in payload.items():
                 self.assertEqual(getattr(recipe ,k),v)
             self.assertEqual(recipe.user,self.user)

        def test_update_user_returns_error(self):
             new_user=create_user()
             recipe=create_recipe(user=self.user)

             payload={'user':new_user.id}
             url= detail_url(recipe.id)
             self.client.patch(url,payload)
             
             recipe.refresh_from_db()

             self.assertEqual(recipe.user,self.user)
        
              
        
        def test_delete_recipe(self):
             recipe =create_recipe(user=self.user)
             url=detail_url(recipe.id)   
             res=self.client.delete(url) 

             self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
             self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())
       
        def test_delete_other_users_recipe(self):
              new_user=create_user(email='test@example.com',password='testpass123')
              recipe=create_recipe(user=new_user)

              url=detail_url(recipe.id)
              res=self.client.delete(url)
              self.assertEqual(res.status_code,status.HTTP_404_NOT_FOUND)
              self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

        def test_create_recipe_with_new_tag(self):

               payload={
                     'title':'thai papua curry',
                     'price':30,
                     'tags':[{'name':'thai'},{'name':'dinner'}],
                     'time_minutes':20,
                }
               
               res=self.client.post(RECIPES_URL,payload,format='json')
               self.assertEqual(res.status_code,status.HTTP_201_CREATED)
               recipes=Recipe.objects.filter(user=self.user)
               self.assertEqual(Recipe.count(),1)
               Recipe=recipes[0]
               self.assertEqual(Recipe.tags.count(),2)

               for tag in payload['tags']:
                    exists=recipes.tag.filter(
                         name=tag['name'],
                         user=self.user,
                    ).exists()
                    self.assertTrue(exists)
  
        def test_create_recipe_with_new_tag(self):
               tag_indian=tag.objects.create(user=self.user,nmae='Indian')
               payload={
                     'title':'pongal',
                     'price':30,
                     'tags':[{'name':'Indian'},{'name':'dinner'}],
                     'time_minutes':20
                }
               
               res=self.client.post(RECIPES_URL,payload,format='json')
               self.assertEqual(res.status_code,status.HTTP_201_CREATED)
               recipes=Recipe.objects.filter(user=self.user)
               self.assertEqual(Recipe.count(),1)
               Recipe=recipes[0]
               self.assertEqual(Recipe.tags.count(),2)

               for tag in payload['tags']:
                    exists=recipes.tag.filter(
                         name=tag['name'],
                         user=self.user,
                    ).exists()

        def test_create_tag_on_update(self):
          recipe=create_recipe(user=self.user)
          payload={'tags':[{'name':'lunch'}]}
          url=detail_url(recipe.id)
          res=self.client.patch(url,payload)
          self.assertEqual(res.status_code,status.HTTP_200_OK)
          new_tag=Tag.objects.get(user=self.user,namr='lunch')
          self.assertIn(new_tag,Recipe.tags.all())
        
        def test_update_recipe_assign_tag(self):
             tag_breakfast=Tag.objects.create(user=self.user,name='Breakfast')
             recipe=create_recipe(user=self.user)
             recipe.tags.add(tag_breakfast)

             tag_lunch=Tag.objects.create(user=self.user,name='Lunch')        
             payload={'tags':[{'name':'lunch'}]}
             url=detail_url(recipe.id)
             res=self.client.patch(url,payload)
             self.assertEqual(res.status_code,status.HTTP_200_OK)
             self.assertIn(tag_lunch,Recipe.tags.all())
             self.assertNotIn(tag_breakfast,Recipe.tags.all())
             
        def test_update_recipe_assign_tag(self):
             tag=Tag.objects.create(user=self.user,name='Breakfast')
             recipe=create_recipe(user=self.user)
             recipe.tags.add(tag)

             payload={'tags':[{'name':'lunch'}]}
             url=detail_url(recipe.id)
             res=self.client.patch(url,payload,format='json')

             self.assertEqual(res.status_code,status.HTTP_200_OK)
             self.assertEqual(recipe.tags.count(),0)

        def test_filter_by_tags(self):
             r1 =create_recipe(user=self.user, title='Thai vegetable curry')
             r2 =create_recipe(user=self.user, title='Aubergine with Tahini')
             tag1 =Tag.objects.create(user=self.user,name='vegan')
             tag2 =Tag.objects.create(user=self.user,name='vegetarian')
             r1.tags.add(tag1)
             r2.tags.add(tag2)
             r3= create_recipe(user=self.user,title='Fish and ')
             
             params = {'tags':f'{tag1.id},{tag2.id}'}
             res =self.client.get(RECIPES_URL,params)

             s1=RecipeSerializer(r1)
             s2=RecipeSerializer(r2)
             s3=RecipeSerializer(r3)
             self.assertIn(s1.data,res.data)
             self.assertIn(s2.data,res.data)
             self.assertNotIn(s3.data,res.data)






class ImageUploadTests(TestCase):
     def SetUp(self):
          self.client=APIClient()
          self.user=get_user_model().objects.create_user(
               'user@example.com',
               'password',
          )             
          self.client.force_authenticate(self.user)
          self.recipe=create_recipe(user=self.user)


     def teraDown(self):
          self.recipe.image.delete() 

     def test_upload_image(self):
               url=image_upload_url(self.recipe.id) 
               with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
                     img=Image.new('RGB',(10,10))
                     img.save(image_file,formae='JPEG')
                     image_file.seek(0)
                     payload={'image':image_file}
                     res=self.client.post(url,payload,formate='multipart')
               self.recipe.refresh_from_db()
               self.assertEqual(res.status_code,status.HTTP_200_OK)
               self.assertIn('image',res.data)
               self.assertTrue(os.path.exists(self.recipe.image.path))      

     def test_upload_image_bad_request(self):
          url=image_upload_url(self.recipe_id)
          payload={'image':'notanimage'}
          res=self.client.post(url,payload,format='multipart')

          self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)