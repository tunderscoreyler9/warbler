"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test2"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
    
    # def test_add_no_session(self):
    #     """Test"""
        
    #     with self.client as c:
    #         resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn("Access unauthorized", str(resp.data))
    
    # def test_add_invalid_user(self):
    #     """Test"""
        
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = 8989865 # This user doesn't exist
            
    #         resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            
    #         self.assertEqual(resp.status_code, 200)
    
    # def test_message_show(self):
    #     """Test"""
        
    #     msg = Message(
    #         id=100,
    #         text="this is a test message",
    #         user_id=self.testuserid
    #     )

    #     db.session.add(msg)
    #     db.session.commit()

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id

    #         msg = Message.query.get(100)

    #         resp = c.get(f'/messages/{msg.id}')

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn(msg.text, str(resp.data))
