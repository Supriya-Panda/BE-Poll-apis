from django.db import models
from django.contrib.auth.models import User
class Question(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    created_at=models.DateTimeField(auto_now_add=True,db_index=True)
    updated_at=models.DateTimeField(auto_now=True)    
    
    def __str__(self):
        return self.question_text
    
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE,related_name='choices')
    option_number = models.PositiveIntegerField(default=1)
    choice_text = models.CharField(max_length=200)
    votes = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = (('question', 'option_number'),)

    def __str__(self):
        return self.choice_text

class Vote(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    question = models.ForeignKey(Question,on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user","question")
        indexes=[
          models.Index(
          fields=['question']
          )
        ]
    