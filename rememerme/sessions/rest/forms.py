'''
    This file holds all of the forms for the cleaning and validation of
    the parameters being used for sessions.
    
    Created on Dec 20, 2013

    @author: Andrew Oberlin, Jake Gregg
'''
from django import forms
from rememerme.sessions.models import Session
from rememerme.users.models import User
import datetime
from rememerme.sessions.rest.exceptions import SessionNotFoundException, SessionAuthorizationException
from rememerme.sessions.serializers import SessionSerializer
from uuid import UUID
from pycassa.cassandra.ttypes import NotFoundException as CassaNotFoundException

class SessionPostForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True)
    '''
        Overriding the clean method to add the default offset and limiting information.
        It will only change date_created if the field is empty.
    '''
    def clean(self):
        now = datetime.datetime.now()
        self.cleaned_data['date_created'] = now
        self.cleaned_data['last_modified'] = now

        return self.cleaned_data
    
    '''
        Submits this form to post a new session for the specified user. 
        
        @return: The session saved to the database in list format.
    '''
    def submit(self):
        user = User.getByUsername(self.cleaned_data['username'])
        if not user:
            raise SessionAuthorizationException()
        
        if not user.authenticate(self.cleaned_data['password']):
            raise SessionAuthorizationException()
        
        self.cleaned_data['user_id'] = UUID(user.user_id)
        del self.cleaned_data['username']
        del self.cleaned_data['password']
        session = Session.fromMap(self.cleaned_data)
    
        session.save()
        return SessionSerializer(session).data
    
class SessionPutForm(forms.Form):
    session_id = forms.CharField(required=True)
    
    def clean(self):
        self.cleaned_data['last_modified'] = datetime.datetime.now() #gm_timestamp() 
        try:
            UUID(self.cleaned_data['session_id'])
        except ValueError:
            raise SessionNotFoundException()
        
        return self.cleaned_data
    
    def submit(self):
        
        # get the original session
        try:
            session = Session.getByID(self.cleaned_data['session_id'])
        except CassaNotFoundException:
            raise SessionNotFoundException()
        session.update(self.cleaned_data)
        session.save()
        
        return SessionSerializer(session).data
    
class SessionDeleteForm(forms.Form):
    session_id = forms.CharField(required=True)
    
    def clean(self):
        try:
            UUID(self.cleaned_data['session_id'])
        except ValueError:
            raise SessionNotFoundException()
        return self.cleaned_data

    def submit(self):
        try:
            session = Session.getByID(self.cleaned_data['session_id'])
        except CassaNotFoundException:
            raise SessionNotFoundException()

        session.delete()
        return SessionSerializer(session).data
