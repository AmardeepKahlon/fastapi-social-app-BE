from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from config.database import Base

class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  email = Column(String)
  password = Column(String)
  posts = relationship("Post", back_populates="owner")
  comments = relationship("Comment", back_populates="owner")
  likes = relationship("Like", back_populates="owner")
  
class Post(Base):
  __tablename__ = 'posts'
  id = Column(Integer, primary_key=True, index=True)
  title = Column(String)
  content = Column(String)
  user_id = Column(Integer, ForeignKey("users.id"))
  owner = relationship("User", back_populates="posts")
  comments = relationship("Comment", back_populates="comment_post")
  likes = relationship("Like", back_populates="like_post")
  
class Comment(Base):
  __tablename__ = 'comments'
  id = Column(Integer, primary_key=True, index=True)
  content = Column(String)
  user_id = Column(Integer, ForeignKey("users.id"))
  post_id = Column(Integer, ForeignKey("posts.id"))
  owner = relationship("User", back_populates="comments")
  comment_post = relationship("Post", back_populates="comments")
  
  
class Like(Base):
  __tablename__ = 'likes'
  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id"))
  post_id = Column(Integer, ForeignKey("posts.id"))
  owner = relationship("User", back_populates="likes")
  like_post = relationship("Post", back_populates="likes")