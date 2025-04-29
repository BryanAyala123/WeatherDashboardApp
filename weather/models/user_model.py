import hashlib
import logging
import os

from flask_login import UserMixin
from sqlalchemy.exc import IntegrityError

from weather.db import db
from weather.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


class Users(db.Model, UserMixin):  
    """
    SQLAlchemy model for application users.
    Includes methods for secure password management.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    salt = db.Column(db.String(32), nullable=False)  # 16-byte salt in hex
    password = db.Column(db.String(64), nullable=False)  # SHA-256 hash in hex

    @staticmethod
    def _generate_hashed_password(password: str) -> tuple[str, str]:
        """
        Generate a random salt and hash the provided password.

        Args:
            password (str): Plain-text password to hash.

        Returns:
            tuple[str, str]: (salt, hashed_password)
        """
        salt = os.urandom(16).hex()
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return salt, hashed

    @classmethod
    def create_user(cls, username: str, password: str) -> None:
        """
        Create and persist a new user with a salted, hashed password.

        Args:
            username (str): Desired username (must be unique).
            password (str): Plain-text password.

        Raises:
            ValueError: If username already exists.
            Exception: On other database errors.
        """
        salt, hashed_pw = cls._generate_hashed_password(password)
        user = cls(username=username, salt=salt, password=hashed_pw)
        try:
            db.session.add(user)
            db.session.commit()
            logger.info("User created: %s", username)
        except IntegrityError:
            db.session.rollback()
            logger.error("Attempt to create duplicate user: %s", username)
            raise ValueError(f"User with username '{username}' already exists")
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating user %s: %s", username, e)
            raise

    @classmethod
    def check_password(cls, username: str, password: str) -> bool:
        """
        Verify a password against the stored hash for the given username.

        Args:
            username (str): Username to check.
            password (str): Plain-text password to verify.

        Returns:
            bool: True if password matches, False otherwise.

        Raises:
            ValueError: If user is not found.
        """
        user = cls.query.filter_by(username=username).first()
        if not user:
            logger.info("User not found: %s", username)
            raise ValueError(f"User {username} not found")
        hashed = hashlib.sha256((password + user.salt).encode()).hexdigest()
        return hashed == user.password

    @classmethod
    def delete_user(cls, username: str) -> None:
        """
        Remove a user from the database.

        Args:
            username (str): Username of user to delete.

        Raises:
            ValueError: If user does not exist.
        """
        user = cls.query.filter_by(username=username).first()
        if not user:
            logger.info("User %s not found for deletion", username)
            raise ValueError(f"User {username} not found")
        db.session.delete(user)
        db.session.commit()
        logger.info("User deleted: %s", username)

    def get_id(self) -> str:
        """
        Override UserMixin.get_id to use username as the identifier.

        Returns:
            str: The username.
        """
        return self.username

    @classmethod
    def get_id_by_username(cls, username: str) -> int:
        """
        Return the numeric ID for a given username.

        Args:
            username (str): Username to look up.

        Returns:
            int: Database primary key.

        Raises:
            ValueError: If user does not exist.
        """
        user = cls.query.filter_by(username=username).first()
        if not user:
            logger.info("User %s not found for ID lookup", username)
            raise ValueError(f"User {username} not found")
        return user.id

    @classmethod
    def update_password(cls, username: str, new_password: str) -> None:
        """
        Change the password for an existing user.

        Args:
            username (str): Username whose password to change.
            new_password (str): Plain-text new password.

        Raises:
            ValueError: If user does not exist.
        """
        user = cls.query.filter_by(username=username).first()
        if not user:
            logger.info("User %s not found for password update", username)
            raise ValueError(f"User {username} not found")
        salt, hashed_pw = cls._generate_hashed_password(new_password)
        user.salt = salt
        user.password = hashed_pw
        db.session.commit()
        logger.info("Password updated for user: %s", username)
