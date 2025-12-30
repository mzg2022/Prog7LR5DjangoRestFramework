from rest_framework import serializers
from polls.models import Question

class ChoiceStatSerializer(serializers.Serializer):
    choice_text = serializers.CharField()
    votes = serializers.IntegerField()
    percentage = serializers.FloatField()

class PollStatSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    question_text = serializers.CharField()
    total_votes = serializers.IntegerField()
    choices = ChoiceStatSerializer(many=True)
    pub_date = serializers.DateTimeField()

class PollSearchSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    question_text = serializers.CharField()
    pub_date = serializers.DateTimeField()
    total_votes = serializers.IntegerField()