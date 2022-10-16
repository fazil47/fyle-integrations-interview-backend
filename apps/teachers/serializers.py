from rest_framework import serializers
from apps.students.models import Assignment
from apps.students.models import GRADE_CHOICES

class TeacherAssignmentSerializer(serializers.ModelSerializer):
    """
    Teacher Assignment serializer
    """
    class Meta:
        model = Assignment
        fields = '__all__'
    
    def validate(self, attrs, *args, **kwargs):
        if 'content' in attrs and attrs['content']:
            raise serializers.ValidationError('Teacher cannot change the content of the assignment')

        if 'student' in attrs and attrs['student']:
            raise serializers.ValidationError('Teacher cannot change the student who submitted the assignment')

        if 'grade' not in attrs or not attrs['grade']:
            raise serializers.ValidationError('Teacher has to set a grade for the assignment')
        
        grade_choices_list = [choice[0] for choice in GRADE_CHOICES]
        if attrs['grade'] not in grade_choices_list:
            raise serializers.ValidationError('Invalid grade')

        if self.partial:
            return attrs

        return super().validate(attrs)