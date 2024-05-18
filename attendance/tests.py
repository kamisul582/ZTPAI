from django.test import TestCase, Client
from .models import CustomUser,Company,Worker
from .views import RegistrationWizardView
from .forms import CustomLoginForm,RegistrationChoiceForm,CustomUserCreationForm,RegisterCompanyForm,RegisterWorkerForm
from django.urls import reverse
class userTestCase(TestCase):
    def setUp(self):
        #CustomUser.objects.create(username="bsmith",email="bsmith@alasfc.ca",password="asdasqweqwe")
        wizard = RegistrationWizardView()
        company_data = {'registration_choice':'company','username':'compuser','email':'compmail@alasfc.ca','password1':'asdasqwaaeqwe','name':'BigCompany','address':'Polna 142'}
        wizard.create_user(company_data)
        company = Company.objects.get(id=1)
        worker_data = {'registration_choice':'worker','username':'bsmith1','email':'bsmith@alasfc.ca','password1':'asdasqweqwe','firstname':'bob','lastname':'smith','company':company}
        wizard.create_user(worker_data)
        #response = self.client.get('/')
        #request = response.wsgi_request
        #print(request,response)
    def test_user_data(self):
        
        user = CustomUser.objects.get(username="bsmith1")
        #response = self.client.post("/login/", {'something':'something'})
        self.assertEqual(user.is_company,False)
        self.assertEqual(user.email,"bsmith@alasfc.ca")
    def test_worker_data(self):
        user = CustomUser.objects.get(username="bsmith1")
        worker = Worker.objects.get(user_id=user.id)
        self.assertEqual(worker.firstname,"bob")
        self.assertEqual(len(worker.kiosk_code),6)

class CustomLoginFormTest(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = CustomUser.objects.create_user(username='testuser', email='testuser@example.com', password='password123')

    def test_clean_username_or_email_with_username(self):
        form = CustomLoginForm(data={'username_or_email': 'testuser', 'password': 'password123'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username_or_email'], 'testuser')

    def test_clean_username_or_email_with_email(self):
        form = CustomLoginForm(data={'username_or_email': 'testuser@example.com', 'password': 'password123'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username_or_email'], 'testuser@example.com')

    def test_clean_username_or_email_invalid(self):
        form = CustomLoginForm(data={'username_or_email': 'nonexistentuser', 'password': 'password123'})
        self.assertFalse(form.is_valid())
        self.assertIn('username_or_email', form.errors)
        print(form.errors)
        self.assertEqual(form.errors['username_or_email'], ['This username does not exist'])

    def test_clean_username_or_email_invalid_email(self):
        form = CustomLoginForm(data={'username_or_email': 'nonexistentuser@example.com', 'password': 'password123'})
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
        self.url = '/register/'  # Update this URL to the actual path of your registration wizard

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
            '1-password1': 'password123',
            '1-password2': 'password123',
        }
        step_two_data.update(self.get_wizard_management_data(STEP_TWO))
        response = self.client.post(self.url, step_two_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context['wizard'])
        self.assertIsInstance(response.context['wizard']['form'], RegisterCompanyForm)

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
            '1-password1': 'password123',
            '1-password2': 'password123',
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
        self.assertEqual(response.status_code, 200)  # Should redirect after successful registration
        self.assertTrue(CustomUser.objects.filter(username='companyuser').exists())
        self.assertTrue(Company.objects.filter(name='Test Company').exists())

    def test_step_three_worker_registration(self):
        # Create a company for the worker to register under
        company = Company.objects.create(user=CustomUser.objects.create_user(username='company', password='password123'), name='Test Company')

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
            '1-password1': 'password123',
            '1-password2': 'password123',
        }
        step_two_data.update(self.get_wizard_management_data(STEP_TWO))
        response = self.client.post(self.url, step_two_data)
        self.assertEqual(response.status_code, 200)

        # Step 3: Submit worker registration form
        step_three_data = {
            '2-company': company.id,
            '2-firstname': 'John',
            '2-lastname': 'Doe',
        }
        step_three_data.update(self.get_wizard_management_data(STEP_THREE))
        response = self.client.post(self.url, step_three_data)
        self.assertEqual(response.status_code, 200)  # Should redirect after successful registration
        self.assertTrue(CustomUser.objects.filter(username='workeruser').exists())
        self.assertTrue(Worker.objects.filter(firstname='John', lastname='Doe').exists())