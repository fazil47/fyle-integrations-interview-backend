from pkg_resources import require
from rest_framework import generics, status
from rest_framework.response import Response

from apps.students.models import Assignment

from .models import Teacher
from .serializers import TeacherAssignmentSerializer


class AssignmentsView(generics.RetrieveUpdateAPIView):
    serializer_class = TeacherAssignmentSerializer

    def get(self, request, *args, **kwargs):
        assignments = Assignment.objects.filter(teacher__user=request.user)

        return Response(
            data=self.serializer_class(assignments, many=True).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, *args, **kwargs):
        teacher = Teacher.objects.get(user=request.user)

        try:
            assignment = Assignment.objects.get(pk=request.data["id"])
        except Assignment.DoesNotExist:
            return Response(
                data={"error": "Assignment does not exist/permission denied"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assignment.grade = request.data["grade"] if "grade" in request.data else assignment.grade
        serializer = self.serializer_class(assignment, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if assignment.teacher != None and assignment.teacher.id != teacher.id:
            return Response(
                data={
                    "non_field_errors": ['Teacher cannot grade for other teacher''s assignment']
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if assignment.state == "SUBMITTED":
            assignment.state = "GRADED"
        else:
            if assignment.state == "GRADED":
                msg = "GRADED assignments cannot be graded again"
            elif assignment.state == "DRAFT":
                msg = "SUBMITTED assignments can only be graded"
            else:
                msg = "Unknown error"
                
            return Response(
                data={"non_field_errors": [msg]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_200_OK)
