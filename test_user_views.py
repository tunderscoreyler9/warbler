"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py



import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup

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


class UserViewsTestCase(TestCase):
    """Test views for users."""
    
    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.testuser = User.signup(username="test",
                                    email="test@gmail.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 300
        self.testuser.id = self.testuser_id

        self.user1 = User.signup("user1", "test1@test.com", "password", None)
        self.user1_id = 100
        self.user1.id = self.user1_id

        self.user2 = User.signup("user2", "test2@test.com", "password", None)
        self.user2_id = 200
        self.user2.id = self.user2_id
        

        db.session.commit()

        self.client = app.test_client()
        
    def tearDown(self):
        """Clean up all transactions after each test"""
        td = super().tearDown()
        db.session.rollback()
        return td
    
    def test_users_index(self):
        """Test that the users index page displays all users"""
        
        with self.client as c:
            resp = c.get("/users")
            
            self.assertIn("@test", str(resp.data))
            self.assertIn("@user1", str(resp.data))
            self.assertIn("@user2", str(resp.data))
    
    def test_users_search(self):
        """Test that searching for users returns the expected results."""
        
        with self.client as c:
            resp = c.get("/users?q=test")
            
            self.assertIn("@test", str(resp.data))
            self.assertNotIn("@user1", str(resp.data))
            self.assertNotIn("@user2", str(resp.data))
    
    def test_user_show(self):
        """Test that the user profile page displays the correct user information"""
        
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@test", str(resp.data))
        
        with self.client as d:
            resp = d.get(f"/users/{self.user1_id}")
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@user1", str(resp.data))
    
    def setup_likes(self):
        """Create test data for message likes."""
        
        msg1 = Message(id=4, text="I am message 1", user_id=self.testuser_id)
        msg2 = Message(id=5, text="I am message 2", user_id=self.user1_id)
        msg3 = Message(id=6, text="I am message 3", user_id=self.user2_id)
        
        db.session.add_all([msg1, msg2, msg3])
        db.session.commit()
        
        like = Likes(user_id=self.testuser_id, message_id=5)
        like2 = Likes(user_id=self.testuser_id, message_id=6)
        db.session.add_all([like, like2])
        db.session.commit()
    
    def test_user_show_with_likes(self):
        """Test that the user profile page displays correct user information along with likes count"""
        
        self.setup_likes()
        
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@test", str(resp.data))
            
            # print(str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            # test for a count of 1 message:
            self.assertIn("1", found[0].text)
            
            # test for a count of 0 followers:
            self.assertIn("0", found[1].text)
            
            # test for a count of 0 following:
            self.assertIn("0", found[2].text)
            
            # test for a count of two likes:
            self.assertIn("2", found[3].text)
    
    def test_add_like(self):
        """Test adding a like to a message"""
        
        msg = Message(text="Testing 1,2,3", user_id=self.user1_id)
        db.session.add(msg)
        db.session.commit()
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            resp = c.post(f"/messages/add_like/{msg.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            
            likes = Likes.query.filter(Likes.message_id== msg.id).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.testuser_id)
    
    def test_remove_like(self):
        """Test removing a like from a message"""
        
        self.setup_likes()
        
        msg1 = Message.query.filter(Message.text=="I am message 2").first()
        msg2 = Message.query.filter(Message.text=="I am message 3").first()
        self.assertIsNotNone([msg1, msg2])
        self.assertNotEqual(msg1.user_id, self.testuser_id)
        self.assertNotEqual(msg2.user_id, self.testuser_id)
        
        like = Likes.query.filter(
            Likes.user_id==self.testuser_id and Likes.message_id==msg1.id
        ).first()
        
        like2 = Likes.query.filter(
            Likes.user_id==self.testuser_id and Likes.message_id==msg2.id
        ).first()
        
        self.assertIsNotNone([like, like2])
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            resp = c.post(f"/messages/add_like/{msg1.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            
            # deleting the like:
            likes = Likes.query.filter(Likes.message_id==msg1.id).all()
            self.assertEqual(len(likes), 0)
    
    def test_unauthenticated_like(self):
        """Test attempting to like a message without authentication"""
        
        self.setup_likes()
        msg = Message.query.filter(Message.text=="I am message 1").one()
        self.assertIsNotNone(msg)
        
        like_count = Likes.query.count()
        # print(like_count)
        
        with self.client as c:
            resp = c.post(f"/messages/add_like/{msg.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            
            # Test that the num of likes hasn't changed after the POST request
            self.assertEqual(like_count, Likes.query.count())
    
    def setup_followers(self):
        """Add test follower(s) data"""
        
        f1 = Follows(user_being_followed_id=self.user1_id, user_following_id=self.testuser_id)
        f2 = Follows(user_being_followed_id=self.user2_id, user_following_id=self.testuser_id)
        f3 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.user1_id)
        db.session.add_all([f1,f2,f3])
        db.session.commit()
    
    def test_user_show_with_likes(self):
        """Test"""
        
        self.setup_followers()
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")
            
            self.assertEqual(resp.status_code, 200)
            
            self.assertIn("@test", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)
            
            # test for a count of 0 messages:
            self.assertIn("0", found[0].text)
            
            # Test for a count of 2 following:
            self.assertIn("2", found[1].text)
            
            # Test for a count of 1 follower:
            self.assertIn("1", found[2].text)
            
            # Test for a count of 0 likes:
            self.assertIn("0", found[3].text)
    
    def test_show_following(self):
        """Test"""
        
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            resp = c.get(f"/users/{self.testuser_id}/following")
            self.assertEqual(resp.status_code, 200)
            
            self.assertIn("@user1", str(resp.data))
            self.assertIn("@user2", str(resp.data))
    
    def test_show_followers(self):
        """Test"""
        
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/followers")

            self.assertIn("@user1", str(resp.data))
            self.assertNotIn("@user2", str(resp.data))
    
    def test_unauthorized_following_page_access(self):
        """Test"""
        
        self.setup_followers()
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}/following", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@user1", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))
    
    def test_unauthorized_followers_page_access(self):
        """Test"""
        
        self.setup_followers()
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}/followers", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@user1", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))