from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Developer(Base):
    __tablename__ = "developers"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, index=True, nullable=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    languages = Column(String(500), default="")  # comma-separated languages, e.g. "Python,TypeScript,Rust"
    repos_summary = Column(Text, default="")     # description of past projects/experience
    is_persona = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    interactions = relationship("Interaction", back_populates="developer", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="developer", cascade="all, delete-orphan")

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, index=True, nullable=True)
    owner = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    full_name = Column(String(200), unique=True, index=True, nullable=False)
    description = Column(Text, default="")
    language = Column(String(100), default="Unknown")
    topics = Column(String(500), default="")     # comma-separated topics
    stars_count = Column(Integer, default=0)
    forks_count = Column(Integer, default=0)
    open_issues_count = Column(Integer, default=0)
    url = Column(String(500), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    issues = relationship("Issue", back_populates="repository", cascade="all, delete-orphan")

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, index=True, nullable=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    body = Column(Text, default="")
    state = Column(String(50), default="open")
    labels = Column(String(500), default="")      # comma-separated labels
    comments_count = Column(Integer, default=0)
    is_beginner_friendly = Column(Boolean, default=False)  # has 'good first issue' or 'help wanted'
    created_at = Column(DateTime, default=datetime.utcnow)
    html_url = Column(String(500), default="")

    repository = relationship("Repository", back_populates="issues")
    interactions = relationship("Interaction", back_populates="issue", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="issue", cascade="all, delete-orphan")

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("developers.id"), nullable=False)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)
    # Types: 'star', 'comment', 'commit', 'pr_merge', 'view', 'like'
    interaction_type = Column(String(50), nullable=False)
    weight = Column(Float, default=1.0)          # Implicit feedback weight
    created_at = Column(DateTime, default=datetime.utcnow)

    developer = relationship("Developer", back_populates="interactions")
    issue = relationship("Issue", back_populates="interactions")

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("developers.id"), nullable=False)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)
    # 'like', 'dislike', 'saved', 'applied'
    action = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    developer = relationship("Developer", back_populates="feedbacks")
    issue = relationship("Issue", back_populates="feedbacks")
