"""Message model tests."""


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test2"


# Now we can import app
from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class UserModelTestCase(TestCase):
    """Test model for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.userid = 400
        user = User.signup(username='message_user', password='password',
                           email="message_user@gmail.com", image_url=None)
        user.id = self.userid
        db.session.commit()

        self.user = User.query.get_or_404(self.userid)

        
    def tearDown(self):
        td = super().tearDown()
        db.session.rollback()
        return td
    
    def test_message_model(self):
        """Does the basic message model work?"""
        
        msg = Message(text="Test message here.", user_id=self.userid)
        
        db.session.add(msg)
        db.session.commit()
        
        self.assertEqual(len(self.user.messages), 1)
        
    def test_message_likes(self):
        """Test that a message is able to be liked/unliked"""
        
        msg1 = Message(text="This is another message", user_id=self.userid)
        msg2 = Message(text="Did you mean warble?", user_id=self.userid)
        
        user2 = User.signup(
            username="message_user2", 
            password="password200", 
            email="message_404@gmail.com", 
            image_url=None)
        
        user2id = 500
        user2.id = user2id
        
        db.session.add_all([msg1, msg2, user2])
        db.session.commit()
        
        user2.likes.append(msg1)
        db.session.commit()
        
        like = Likes.query.filter_by(user_id=user2id).all()
        self.assertEqual(len(like), 1)
        
        # Dislike msg1, now.
        user2.likes.remove(msg1)
        db.session.commit()
        
        dislike = Likes.query.filter_by(user_id=user2id).all()
        self.assertEqual(len(dislike), 0)