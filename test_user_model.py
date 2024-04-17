"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        # User.query.delete()
        # Message.query.delete()
        # Follows.query.delete()
        db.drop_all()
        db.create_all()
        
        user1 = User.signup(username='user1', password='password', email='user1@gmail.com', image_url=None)
        user1id = 20
        user1.id = user1id
        
        user2 = User.signup(username='user2', password='password2', email='user2@gmail.com', image_url=None)
        user2id = 30
        user2.id = user2id
        
        db.session.commit()
        
        user1 = User.query.get_or_404(user1id)
        user2 = User.query.get_or_404(user2id)

        self.user1 = user1
        self.user1id = user1id

        self.user2 = user2
        self.user2id = user2id

        self.client = app.test_client()
    
    def tearDown(self):
        """Clean up any fouled transaction"""
        td = super().tearDown()
        db.session.rollback()
        return td

    def test_user_model(self):
        """Test basic functionality of the User model.

        This test verifies that a new user can be created and added to the
        database. It checks that the user has no messages and no followers
        upon creation."""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test_repr(self):
        """Test the __repr__ method of the User model.

        This test verifies that the string representation of a User object
        matches the expected format."""
        user12 = User(username="testuser12", email="test@example.com")
        expected_repr = f"<User #{user12.id}: {user12.username}, {user12.email}>"
        self.assertEqual(repr(user12), expected_repr)
    
    
    def test_user_follows(self):
        """Test that a user can successfully follow another user.

        This test verifies that a user can follow another user by appending the
        second user to the 'following' list of the first user. It checks that
        after the follow action:
        
        - The followed user's 'following' list is empty.
        - The followed user's 'followers' list contains the follower.
        - The follower's 'followers' list is empty.
        - The follower's 'following' list contains the followed user.
        - The IDs of the followers and following users match correctly.
        - The 'is_following' method correctly detects the follow relationship.

        This ensures that the follow relationship between users is correctly
        established and reflected in their respective 'followers' and 'following'
        lists."""
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 1)
        self.assertEqual(len(self.user1.followers), 0)
        self.assertEqual(len(self.user1.following), 1)

        self.assertEqual(self.user2.followers[0].id, self.user1.id)
        self.assertEqual(self.user1.following[0].id, self.user2.id)
        
        self.assertEqual(self.user1.is_following(self.user2), True)
    
    def test_is_following(self):
        """Test the is_following method of the User model.

        This test verifies that the is_following method correctly detects
        whether a user is following another user."""
        
        self.user1.following.append(self.user2)
        db.session.commit()
        
        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))
    
    def test_is_followed_by(self):
        """Test the is_followed_by method of the User model.

        This test verifies that the is_followed_by method correctly detects
        whether a user is followed by another user."""
        
        self.user1.following.append(self.user2)
        db.session.commit()
        
        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))
        
    def test_user_signup(self):
        """Test that 'signup' can successfully create a new user given valid credentials.

        This test verifies that the 'signup' method successfully creates a new user
        with the provided username, password, email, and default image URL. It checks
        that the user object returned from the 'signup' method is not None and is an
        instance of the User class. It also verifies that the user object has the correct
        attributes set with the provided values.

        After signing up a new user, this test also attempts to sign up a new user with
        the same username as an existing user (user1). It asserts that an IntegrityError
        is raised, indicating that the database constraint on the username uniqueness is
        enforced properly."""
        
        user3 = User.signup(username='user3', password='password3', email='user3@gmail.com', image_url=None)
        user3id = 40
        user3.id = user3id
        
        db.session.commit()
        
        # Assert that user3 object is not None
        self.assertIsNotNone(user3)
        
        # Assert that user3 object is an instance of the User class
        self.assertIsInstance(user3, User)
        
        # Assert that user3 object has the correct attributes set:
        self.assertEqual(user3.username, 'user3')
        self.assertEqual(user3.email, 'user3@gmail.com')
        self.assertEqual(user3.image_url, '/static/images/default-pic.png')
        
        # Attempt to sign up a new user with the same username as user1
        with self.assertRaises(exc.IntegrityError):
            User.signup(username='user1', password='password', email='user1@example.com', image_url=None)
            db.session.commit()
    
    def test_authentication(self):
        """Test user authentication functionality
        
        - Test that User.authenticate successfully return a user when given a valid username and password
        - Test that User.authenticate fails to return a user when the username is invalid
        - Test that User.authenticate fails to return a user when the password is invalid
        """
        
        user = User.authenticate(username=self.user1.username, password="password")
        
        self.assertIsNotNone(user)
        self.assertTrue(user)
        self.assertEqual(user.id, self.user1id)
        
        invalid_user = User.signup(username='new_member1', password='password', email='jared@gmail.com', image_url=None)
        self.assertFalse(User.authenticate(username='new_member10', password='password'))
        self.assertNotEqual(invalid_user.id, 'new_member10')
        
        self.assertFalse(User.authenticate(username=invalid_user.username, password='password100'))
        self.assertNotEqual(invalid_user.password, 'password100')
        
        