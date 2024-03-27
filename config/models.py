from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import URLType, EmailType

from config.database import Base

class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  email = Column(EmailType)
  password = Column(String)
  posts = relationship("Post", back_populates="owner")
  comments = relationship("Comment", back_populates="owner")
  likes = relationship("Like", back_populates="owner")
  chats = relationship("Chat", back_populates="sender", foreign_keys="Chat.sender_id",)
  
class Post(Base):
  __tablename__ = 'posts'
  id = Column(Integer, primary_key=True, index=True)
  content = Column(String)
  url = Column(URLType)
  user_id = Column(Integer, ForeignKey("users.id"))
  user_name = Column(String)
  allow_comments = Column(Boolean, default=True)
  post_time = Column(DateTime)
  owner = relationship("User", back_populates="posts")
  comments = relationship("Comment", back_populates="comment_post")
  likes = relationship("Like", back_populates="like_post")
  chats = relationship("Chat", back_populates="chat_post")
  
class Comment(Base):
  __tablename__ = 'comments'
  id = Column(Integer, primary_key=True, index=True)
  content = Column(String)
  user_id = Column(Integer, ForeignKey("users.id"))
  post_id = Column(Integer, ForeignKey("posts.id"))
  user_name = Column(String)
  approved_comment = Column(Boolean, default=True)
  time_posted = Column(DateTime)
  parent_comment_id = Column(Integer)
  owner = relationship("User", back_populates="comments")
  comment_post = relationship("Post", back_populates="comments")
  chats = relationship("Chat", back_populates="chat_comment", lazy="joined")
  
class Like(Base):
  __tablename__ = 'likes'
  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id"))
  post_id = Column(Integer, ForeignKey("posts.id"))
  owner = relationship("User", back_populates="likes", lazy="joined")
  like_post = relationship("Post", back_populates="likes", lazy="joined")
  
class Chat(Base):
  __tablename__ = 'chats'
  id = Column(Integer, primary_key=True, index=True)
  sender_id = Column(Integer, ForeignKey("users.id"))
  receiver_id = Column(Integer, ForeignKey("users.id"))
  post_id = Column(Integer, ForeignKey("posts.id"))
  comment_id = Column(Integer, ForeignKey("comments.id"))
  timestamp = Column(DateTime)
  sender = relationship("User", foreign_keys=[sender_id], back_populates="chats", lazy="joined")
  receiver = relationship("User", foreign_keys=[receiver_id], back_populates="chats", lazy="joined")
  chat_post = relationship("Post", back_populates="chats", lazy="joined")
  chat_comment = relationship("Comment", back_populates="chats", lazy="joined")
  
