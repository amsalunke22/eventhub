from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Event, Reservation
from .serializers import EventSerializer, ReservationSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = Event.objects.all()

        event_status = self.request.query_params.get('status')
        venue = self.request.query_params.get('venue')

        if event_status:
            queryset = queryset.filter(status=event_status)

        if venue:
            queryset = queryset.filter(venue__icontains=venue)

        return queryset


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_queryset(self):
        queryset = Reservation.objects.all()

        event_id = self.request.query_params.get('event_id')

        if event_id:
            queryset = queryset.filter(event_id=event_id)

        return queryset

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()

        if reservation.status == 'cancelled':
            return Response(
                {"detail": "Reservation is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        event = reservation.event

        event.available_seats += reservation.seats_reserved
        event.save()

        reservation.status = 'cancelled'
        reservation.save()

        return Response(
            ReservationSerializer(reservation).data,
            status=status.HTTP_200_OK
        )