from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .tasks import start_generator


class StartGenerate(APIView):
    #permission_classes = (IsAdminUser,)

    def get(self, request):
        start_generator.delay()
        return Response({'get': 'start generate...'})
