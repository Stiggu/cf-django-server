from rest_framework import serializers
from .models import Contracts, Rates


class SaveSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    date = serializers.DateField()
    # file = serializers.Field


class RatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rates
        fields = '__all__'


class ContractSerializer(serializers.ModelSerializer):
    rates = RatesSerializer(many=True)

    class Meta:
        model = Contracts
        fields = '__all__'
