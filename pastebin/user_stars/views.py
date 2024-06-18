from accounts.models import User
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from notes.models import Note, UserStars
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .doc_decorators import users_stars_doc


@extend_schema(tags=['User stars'])
@users_stars_doc
class UserStarsView(mixins.RetrieveModelMixin,
                mixins.DestroyModelMixin,
                mixins.CreateModelMixin,
                GenericViewSet):
    queryset = UserStars.objects.all()
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        stars = {str(star): star.hash_link for star in user.starred_notes.all()}
        return Response({'my_stars': stars})

    def create(self, request, *args, **kwargs):
        item = get_object_or_404(Note.objects.all(), hash_link=kwargs['hash_link'])

        try:
            self.queryset.create(user_id=request.user.id, note_id=item.id)
        except IntegrityError as error:
            return Response({'detail': 'This note is already in your collection'},
                            status=status.HTTP_400_BAD_REQUEST)

        item.meta_data.stars += 1
        item.meta_data.save()

        return Response({'save_to_stars': str(item)}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        note = get_object_or_404(Note.objects.all(), hash_link=kwargs['hash_link'])
        item = get_object_or_404(self.get_queryset(),
                                 user_id=request.user.id,
                                 note_id=note.id)
        item.delete()

        note.meta_data.stars -= 1
        note.meta_data.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
