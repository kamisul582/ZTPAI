from django.test import TestCase, Client, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from .models import CustomUser,Company,Worker,Worktime
from .views import RegistrationWizardView,generate_kiosk_codes,reset_new_password_view,get_worktime_details
from .forms import ChangePasswordForm,CustomLoginForm,RegistrationChoiceForm,CustomUserCreationForm,RegisterCompanyForm,RegisterWorkerForm
from django.urls import reverse
from django.contrib import messages
from rest_framework.test import APIClient
from django.contrib.auth.hashers import check_password
import json
from django.utils import timezone
class userTestCase(TestCase):
    def setUp(self):
        wizard = RegistrationWizardView()
        company_data = {'registration_choice':'company','username':'compuser','email':'compmail@alasfc.ca','password1':'asdasqwaaeqwe','name':'BigCompany','address':'Polna 142'}
        wizard.create_user(company_data)
        company = Company.objects.get(id=1)
        worker_data = {'registration_choice':'worker','username':'bsmith1','email':'bsmith@alasfc.ca','password1':'asdasqweqwe','firstname':'bob','lastname':'smith','company':company}
        wizard.create_user(worker_data)
    def test_user_data(self):
        
        user = CustomUser.objects.get(username="bsmith1")
        self.assertEqual(user.is_company,False)
        self.assertEqual(user.email,"bsmith@alasfc.ca")
    def test_worker_data(self):
        user = CustomUser.objects.get(username="bsmith1")
        worker = Worker.objects.get(user_id=user.id)
        self.assertEqual(worker.firstname,"bob")
        self.assertEqual(len(worker.kiosk_code),6)

class CustomLoginFormTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='testuser@example.com', password='QWERTYqwerty12345')

    def test_clean_username_or_email_with_username(self):
        form = CustomLoginForm(data={'username_or_email': 'testuser', 'password': 'QWERTYqwerty12345'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username_or_email'], 'testuser')

    def test_clean_username_or_email_with_email(self):
        form = CustomLoginForm(data={'username_or_email': 'testuser@example.com', 'password': 'QWERTYqwerty12345'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username_or_email'], 'testuser@example.com')

    def test_clean_username_or_email_invalid(self):
        form = CustomLoginForm(data={'username_or_email': 'nonexistentuser', 'password': 'QWERTYqwerty12345'})
        self.assertFalse(form.is_valid())
        self.assertIn('username_or_email', form.errors)
        print(form.errors)
        self.assertEqual(form.errors['username_or_email'], ['This username does not exist'])

    def test_clean_username_or_email_invalid_email(self):
        form = CustomLoginForm(data={'username_or_email': 'nonexistentuser@example.com', 'password': 'QWERTYqwerty12345'})
        self.assertFalse(form.is_valid())
        self.assertIn('username_or_email', form.errors)
        print(form.errors)
        self.assertEqual(form.errors['username_or_email'], ['This email does not exist'])

STEP_ONE = u'0'
STEP_TWO = u'1'
STEP_THREE = u'2'
STEP_FOUR = u'3'
class RegistrationWizardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/register/'

    def get_wizard_management_data(self, current_step):
        """Returns the management data for the given step."""
        return {
            'registration_wizard_view-current_step': current_step,
        }

    def test_step_one_choice_company(self):
        data = {
            '0-registration_choice': 'company',
        }
        data.update(self.get_wizard_management_data(STEP_ONE))
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context['wizard'])
        self.assertIsInstance(response.context['wizard']['form'], CustomUserCreationForm)

    def test_step_one_choice_worker(self):
        data = {
            '0-registration_choice': 'worker',
        }
        data.update(self.get_wizard_management_data(STEP_ONE))
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context['wizard'])
        self.assertIsInstance(response.context['wizard']['form'], CustomUserCreationForm)
    def test_step_one_choice_manager(self):
        data = {
            '0-registration_choice': 'manager',
        }
        data.update(self.get_wizard_management_data(STEP_ONE))
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context['wizard'])
        self.assertIsInstance(response.context['wizard']['form'], CustomUserCreationForm)

    def test_step_two_company_registration(self):
        # Step 1: Choose company registration
        step_one_data = {
            '0-registration_choice': 'company',
        }
        step_one_data.update(self.get_wizard_management_data(STEP_ONE))
        response = self.client.post(self.url, step_one_data)
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Submit user creation form
        step_two_data = {
            '1-username': 'companyuser',
            '1-password1': 'QWERTYqwerty12345',
            '1-password2': 'QWERTYqwerty12345',
        }
        step_two_data.update(self.get_wizard_management_data(STEP_TWO))
        response = self.client.post(self.url, step_two_data)
        if response.status_code != 200:
            print("Step 2 Errors: ", response.context['wizard']['form'].errors)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context['wizard'])
        self.assertIsInstance(response.context['wizard']['form'], RegisterCompanyForm)

    def test_step_two_worker_registration(self):
        # Step 1: Choose company registration
        step_one_data = {
            '0-registration_choice': 'worker',
        }
        step_one_data.update(self.get_wizard_management_data(STEP_ONE))
        response = self.client.post(self.url, step_one_data)
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Submit user creation form
        step_two_data = {
            '1-username': 'workeruser',
            '1-password1': 'QWERTYqwerty12345',
            '1-password2': 'QWERTYqwerty12345',
        }
        step_two_data.update(self.get_wizard_management_data(STEP_TWO))
        response = self.client.post(self.url, step_two_data)
        if response.status_code != 200:
            print("Step 2 Errors: ", response.context['wizard']['form'].errors)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context['wizard'])
        self.assertIsInstance(response.context['wizard']['form'], RegisterWorkerForm)

    def test_step_two_manager_registration(self):
        # Step 1: Choose company registration
        step_one_data = {
            '0-registration_choice': 'worker',
        }
        step_one_data.update(self.get_wizard_management_data(STEP_ONE))
        response = self.client.post(self.url, step_one_data)
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Submit user creation form
        step_two_data = {
            '1-username': 'manageruser',
            '1-password1': 'QWERTYqwerty12345',
            '1-password2': 'QWERTYqwerty12345',
        }
        step_two_data.update(self.get_wizard_management_data(STEP_TWO))
        response = self.client.post(self.url, step_two_data)
        if response.status_code != 200:
            print("Step 2 Errors: ", response.context['wizard']['form'].errors)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context['wizard'])
        self.assertIsInstance(response.context['wizard']['form'], RegisterWorkerForm)
    
    def test_step_three_company_registration(self):
        # Step 1: Choose company registration
        step_one_data = {
            '0-registration_choice': 'company',
        }
        step_one_data.update(self.get_wizard_management_data(STEP_ONE))
        response = self.client.post(self.url, step_one_data)
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Submit user creation form
        step_two_data = {
            '1-username': 'companyuser',
            '1-password1': 'QWERTYqwerty12345',
            '1-password2': 'QWERTYqwerty12345',
        }
        step_two_data.update(self.get_wizard_management_data(STEP_TWO))
        response = self.client.post(self.url, step_two_data)
        self.assertEqual(response.status_code, 200)

        # Step 3: Submit company registration form
        step_three_data = {
            '2-name': 'Test Company',
            '2-address': '123 Company St',
        }
        step_three_data.update(self.get_wizard_management_data(STEP_THREE))
        response = self.client.post(self.url, step_three_data)
        if response.status_code == 200:
            print("Step 3 Errors: ", response.context['wizard']['form'].errors)
        
        self.assertEqual(response.status_code, 302)  # Should redirect after successful registration

        self.assertTrue(CustomUser.objects.filter(username='companyuser').exists())
        self.assertTrue(Company.objects.filter(name='Test Company').exists())

        form = CustomLoginForm(data={'username_or_email': 'companyuser', 'password': 'QWERTYqwerty12345'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username_or_email'], 'companyuser')
        
    def test_step_three_worker_registration(self):
        # Create a company for the worker to register under
        company = Company.objects.create(user=CustomUser.objects.create(email='testcompany@example.test',username='company', password='QWERTYqwerty12345'), name='Test Company',address='Polna 13')
        # Step 1: Choose worker registration
        step_one_data = {
            '0-registration_choice': 'worker',
        }
        step_one_data.update(self.get_wizard_management_data(STEP_ONE))
        response = self.client.post(self.url, step_one_data)
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Submit user creation form
        step_two_data = {
            '1-username': 'workeruser',
            '1-password1': 'QWERTYqwerty12345',
            '1-password2': 'QWERTYqwerty12345',
        }
        step_two_data.update(self.get_wizard_management_data(STEP_TWO))
        response = self.client.post(self.url, step_two_data)
        if response.status_code != 200:
            print("Step 2 Errors: ", response.context['wizard']['form'].errors)
        
        self.assertEqual(response.status_code, 200)

        # Step 3: Submit worker registration form
        step_three_data = {
            '3-company': company.pk,
            '3-firstname': 'John',
            '3-lastname': 'Doe',
        }
        step_three_data.update(self.get_wizard_management_data(STEP_FOUR))
        response = self.client.post(self.url, step_three_data)
        
        # Add logging to print form errors if the status code is 200
        if response.status_code == 200:
            print("Step 3 Errors: ", response.context['wizard']['form'].errors)
            print("Step 3 Form: ", response.context['wizard']['form'])
        
        self.assertEqual(response.status_code, 302)  # Should redirect after successful registration

        self.assertTrue(CustomUser.objects.filter(username='workeruser').exists())
        self.assertTrue(Worker.objects.filter(firstname='John', lastname='Doe').exists())
    def test_step_three_manager_registration(self):
            # Create a company for the worker to register under
            company = Company.objects.create(user=CustomUser.objects.create(email='testcompany@example.test',username='company', password='QWERTYqwerty12345'), name='Test Company',address='Polna 13')
            # Step 1: Choose worker registration
            step_one_data = {
                '0-registration_choice': 'manager',
            }
            step_one_data.update(self.get_wizard_management_data(STEP_ONE))
            response = self.client.post(self.url, step_one_data)
            self.assertEqual(response.status_code, 200)

            # Step 2: Submit user creation form
            step_two_data = {
                '1-username': 'manageruser',
                '1-password1': 'QWERTYqwerty12345',
                '1-password2': 'QWERTYqwerty12345',
            }
            step_two_data.update(self.get_wizard_management_data(STEP_TWO))
            response = self.client.post(self.url, step_two_data)
            if response.status_code != 200:
                print("Step 2 Errors: ", response.context['wizard']['form'].errors)

            self.assertEqual(response.status_code, 200)

            # Step 3: Submit worker registration form
            step_three_data = {
                '3-company': company.pk,
                '3-firstname': 'John',
                '3-lastname': 'Doe',
            }
            step_three_data.update(self.get_wizard_management_data(STEP_FOUR))
            response = self.client.post(self.url, step_three_data)

            # Add logging to print form errors if the status code is 200
            if response.status_code == 200:
                print("Step 3 Errors: ", response.context['wizard']['form'].errors)
                print("Step 3 Form: ", response.context['wizard']['form'])

            self.assertEqual(response.status_code, 302)  # Should redirect after successful registration

            self.assertTrue(CustomUser.objects.filter(username='manageruser').exists())
            self.assertTrue(Worker.objects.filter(firstname='John', lastname='Doe').exists())

class AddWorktimeTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        company = Company.objects.create(user=CustomUser.objects.create(email='testcompany@example.test',username='company', password='QWERTYqwerty12345'), name='Test Company',address='Polna 13')
        worker = Worker.objects.create(user=CustomUser.objects.create(email='testworker@example.test',username='worker', password='QWERTYqwerty12345',is_worker=True), company_id =1,firstname='Test',lastname='Worker',kiosk_code='ABC123')
        self.user = CustomUser.objects.get(username='worker')
        self.client.force_login(self.user)
        self.url = '/add-worktime/'
    
    def test_add_worktime_existing_entry(self):
        existing_entry = Worktime.objects.create(worker=Worker.objects.get(user_id=self.user.id), punch_in='2024-05-20T09:00:00Z')
        response = self.client.post(self.url, {'user_id': self.user.id})
        print(response,response.content,response.context)
        self.assertEqual(response.status_code, 200)
        # Check that the existing entry's punch_out has been updated
        existing_entry.refresh_from_db()
        self.assertIsNotNone(existing_entry.punch_out)

    def test_add_worktime_new_entry(self):
        response = self.client.post(self.url, {'user_id': self.user.id})
        self.assertEqual(response.status_code, 200)
        # Check that a new Worktime entry has been created
        new_entry = Worktime.objects.filter(worker=Worker.objects.get(user_id=self.user.id)).latest('id')
        self.assertIsNotNone(new_entry)
class AddWorktimeWithKioskCodeTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        company = Company.objects.create(user=CustomUser.objects.create(email='testcompany@example.test',username='company', password='QWERTYqwerty12345'), name='Test Company',address='Polna 13')
        
        self.kiosk_code =generate_kiosk_codes(company)[0]
        self.worker = Worker.objects.create(user=CustomUser.objects.create(email='testworker@example.test',
                                                                      username='worker',
                                                                       password='QWERTYqwerty12345',
                                                                       is_worker=True),
                                                                         company_id =1,
                                                                         firstname='Test',
                                                                         lastname='Worker',
                                                                         kiosk_code=self.kiosk_code)
        self.user = CustomUser.objects.get(username='company')
        self.client.force_login(self.user)
        self.url = '/worktime-by-kiosk-code/'
    def test_add_worktime_with_kiosk_code(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        response_data = response.content.decode("UTF-8")
        #print(response_data)
        print(Worktime.objects.filter(worker = self.worker))
        #response = self.client.get('/get-worktime-details/1/')
        #self.assertEqual(response.status_code, 200)
class GetWorktimeDetailsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        company = Company.objects.create(user=CustomUser.objects.create(email='testcompany@example.test',username='company', password='QWERTYqwerty12345'), name='Test Company',address='Polna 13')
        worker = Worker.objects.create(user=CustomUser.objects.create(email='testworker@example.test',username='worker', password='QWERTYqwerty12345',is_worker=True), company_id =1,firstname='Test',lastname='Worker',kiosk_code='ABC123')
        
        self.worktime = Worktime.objects.create(
            worker=worker,
            date=timezone.now().date(),
            punch_in=timezone.now(),
            punch_out=timezone.now() + timezone.timedelta(hours=8),
            total_time=timezone.timedelta(hours=8)
        )
        
        self.url = f'/get-worktime-details/{self.worktime.id}/'

    def test_get_worktime_details_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # Round microsecond part to a certain precision
        response_data = response.json()
        response_data['punch_in'] = response_data['punch_in'][:6] + 'Z'
        response_data['punch_out'] = response_data['punch_out'][:6] + 'Z'

        expected_data = {
            'date': str(self.worktime.date),
            'punch_in': self.worktime.punch_in.isoformat()[:6] + 'Z',
            'punch_out': self.worktime.punch_out.isoformat()[:6] + 'Z',
            'total_time': 'P0DT08H00M00S'
        }

        self.assertEqual(response_data, expected_data)

    def test_get_worktime_details_not_found(self):
        url = '/get-worktime-details/999/'  # Assuming 999 does not exist
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class GenerateKioskCodesTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(user=CustomUser.objects.create(email='testcompany@example.test',username='company', password='QWERTYqwerty12345'), name='Test Company',address='Polna 13')
        self.worker = Worker.objects.create(user=CustomUser.objects.create(email='testworker@example.test',username='worker', password='QWERTYqwerty12345',is_worker=True), company_id =1,firstname='Test',lastname='Worker',kiosk_code='ABC123')
    def test_uniqueness(self):
        codes = generate_kiosk_codes(self.company,500)
        self.assertEquals(len(codes),len(set(codes)))
    def test_amount(self):
        amount = 500
        codes = generate_kiosk_codes(self.company,amount)
        self.assertEquals(amount,len(codes))

class ResetNewPasswordViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(email='test@example.com',username='testuser', password='oldpassword')
        self.url = '/change-password/'
    def test_post_valid_form(self):
        # Prepare valid form data
        data = {
            'email': 'test@example.com',
            'new_password1': 'QWERTYqwerty12345',
            'new_password2': 'QWERTYqwerty12345',
        }
        request = self.factory.post(self.url, data)
        request.user = self.user

        # Call the view function
        response = reset_new_password_view(request)

        # Check if the password is updated
        updated_user = CustomUser.objects.get(email='test@example.com')
        self.assertTrue(check_password('QWERTYqwerty12345', updated_user.password))

        # Check if the view redirects to the login page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('attendance:login'))

    def test_post_invalid_form(self):
        # Make a POST request with invalid form data
        data = {
            'email': 'test@example.com',
            'new_password1': 'short',
            'new_password2': 'short',
        }
        request = self.factory.post(self.url, data)
        request.user = self.user

        # Call the view function
        response = reset_new_password_view(request)
        self.assertContains(response, 'This password is too short.')

    def test_get_request(self):
        # Make a GET request
        response = self.client.get(self.url)
        
        # Check if the view renders the form
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], ChangePasswordForm)