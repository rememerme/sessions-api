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
from rememerme.sessions.sessions import util
from rememerme.sessions.rest.exceptions import SessionConflictException, SessionNotFoundException, SessionAuthorizationException
from rememerme.sessions.rest.serializers import SessionSerializer
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
        self.cleaned_data['date_created'] = datetime.date.today
        self.cleaned_data['last_modified'] = datetime.date.today

        return self.cleaned_data
    
    '''
        Submits this form to post a new session for the specified user. 
        
        @return: The session saved to the database in list format.
    '''
    def submit(self):
        user = User.getByUsername(self.cleaned_data['username'])
        if not user:
            raise SessionAuthorizationException()
        self.cleaned_data['user_id'] = user.user_id
        del self.cleaned_data['username']
        del self.cleaned_data['password']
        session = Session.fromMap(self.cleaned_data)
    
        session.save()
        return SessionSerializer(session).data
    
class SessionPutForm(forms.Form):
    session_id = forms.CharField(required=True)
    
    def clean(self):
        self.cleaned_data['last_modified'] = datetime.date.today

        return self.cleaned_data
    
    def submit(self):
        user_id = self.cleaned_data['user_id']
        del self.cleaned_data['user_id']
        
        # get the original user
        try:
            session = Session.get(user_id)
        except CassaNotFoundException:
            raise UserNotFoundException()
        
        if not self.cleaned_data: # no real changes made
            return UserSerializer(user).data
    
        # check to see username or email are being changed
        # if they are maintain the uniqueness
        if 'username' in self.cleaned_data:
            if user.username != self.cleaned_data['username'] and User.get(username=self.cleaned_data['username']):
                raise UserConflictException()
        
        if 'email' in self.cleaned_data:
            if user.email != self.cleaned_data['email'] and User.get(email=self.cleaned_data['email']):
                raise UserConflictException()
            
        if 'password' in self.cleaned_data:
            self.cleaned_data['password'] = util.hash_password(self.cleaned_data['password'], user.salt)
        
        session.update(self.cleaned_data)
        session.save()
        
        return SessionSerializer(user).data
    

    
        