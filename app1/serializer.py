from rest_framework.serializers import ModelSerializer
from app1.models import *


class LogSerializer(ModelSerializer):

    class Meta:
        model = Punch
        fields = '__all__'

class UserSerializer(ModelSerializer):
    class Meta:

        model = User
        fields = ['id' , 'username', 'email','empid','emptype','status','department','role']
        