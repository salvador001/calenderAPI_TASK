from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from google.oauth2 import credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from rest_framework.views import APIView
from rest_framework.response import Response

class GoogleCalendarInitView(APIView):
    def get(self, request):
        flow = Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=request.build_absolute_uri(reverse('google-calendar-redirect'))
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        request.session['google_auth_state'] = state
        return redirect(authorization_url)


class GoogleCalendarRedirectView(APIView):
    def get(self, request):
        state = request.session.pop('google_auth_state', None)
        flow = Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            state=state,
            redirect_uri=request.build_absolute_uri(reverse('google-calendar-redirect'))
        )
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)

        # Get the access token
        credentials = flow.credentials
        access_token = credentials.token

        # Use the access token to fetch list of events
        service = build('calendar', 'v3', credentials=credentials)
        events_result = service.events().list(calendarId='primary', maxResults=10).execute()
        events = events_result.get('items', [])

        return Response(events)
