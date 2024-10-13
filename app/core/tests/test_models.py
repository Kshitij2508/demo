from django.test import testcases
from django.contrib.auth import get_user_models
from requests import patch 
from core import models


def create_user(email='user@example.com',password='pass123'):

   return get_user_models().objects.create_user(email,password)

class ModelTest(testcases):

    def create_user_with_test_successful(self):

      email='test@example.com'
      password='testpass1234'
      user=get_user_models().objects.create(
         email=email,
         password=password
      )
      self.assertEqual(user.email,email)
      self.assertTrue(user.check_password,(password))

    def new_user_email_normalizer(self):

       sample_email=[
         ['test1@example.com','test1@example.com']
         ['test2@example.com','test2@example.com']
         ['test3@example.com','test3@example.com']
         ['test4@example.com','test4@example.com'] 
       ]  
       for email, expected in sample_email:
        user = get_user_models().objects.create_user(email,'sample123')
        self.assertEqual(user.email,expected)

    def test_new_user_without_raiser_error(self):
       with self.assertRaises(ValueError):
         get_user_models().object.create_user('','test123')

    def test_create_recipe(self):
         user=get_user_models().objects.create_user(
            'test@example.com',
            'test@123'
         )                  
         recipe=models.Recipe.objects.create(
            user=user,
            time_minutes=5, 
            proce='50',
            title='panner',
            sample='reciper descriptions',

         )
         self.assertEqual(str(recipe),recipe.title)

         def test_create_tag(self):

            user= create_user()
            tag=models.tag.objects(user=user,name='tag1')

            self.assertEqual(str(tag),tag.name)



         @patch('core.models.uuid.uuid4')
         def test_recipe_profile_name_uuid(self,mock_uuid):
            uuid='test-uuid'
            mock_uuid.return_value=uuid    
            file_path =models.recipe_image_file_path(None,'example.jpg')

            self.assertEqual(file_path,f'upload/recipe/{uuid}.jpeg   ')