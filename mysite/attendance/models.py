from django.db import models

class Company(models.Model):
    def __str__(self) -> str:
        return self.email + " " + self.company_name 
    email = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    company_address = models.CharField(max_length=200)

class User(models.Model):
    def __str__(self) -> str:
        return self.email + " " + self.name + " " + self.surname
    email = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    employer  = models.ForeignKey(Company, on_delete=models.CASCADE)
    kiosk_code = models.CharField(max_length=10)





class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
# Create your models here.
