from rest_framework import serializers
from .models import OrcamentoConfig, OrcamentoOpcao

class OrcamentoConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrcamentoConfig
        fields = '__all__'

class OrcamentoOpcaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrcamentoOpcao
        fields = '__all__'
