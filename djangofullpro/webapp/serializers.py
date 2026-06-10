from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Question, Choice

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length = 8)

    class Meta:
        model = User
        fields = ['first_name','last_name','email','password']
        
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        data['status_code'] = 200
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        return data

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['option_number', 'choice_text', 'votes']
        read_only_fields = ["option_number",'votes']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)
    
    def validate_choices(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Minimum two choices required")
        return value
   
    def create(self, validated_data):
        choices_data = validated_data.pop('choices',[])
        question = Question.objects.create(**validated_data)

        for index, choice in enumerate(choices_data,start=1):
            Choice.objects.create(question=question,option_number=index,**choice)
        return question
    
class DashboardSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)
    total_votes = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id','question_text','created_at','total_votes','choices']
        
    def get_total_votes(self, obj):
        return getattr(obj,'total_votes',0)    