from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, DateTime, Text, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base


# ============ ТАБЛИЦА СВЯЗИ MANY-TO-MANY ============
user_skill_association = Table(
    "user_skill",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
    Column("is_favorite", Boolean, default=False),
)

project_skill_association = Table(
    "project_skill",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)


# ============ ТАБЛИЦА USERS ============
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100))
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    
    # Relationships
    skills: Mapped[list["Skill"]] = relationship(
        "Skill",
        secondary=user_skill_association,
        backref="users",
    )
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="owner")
    applications: Mapped[list["Application"]] = relationship("Application", back_populates="applicant")


# ============ ТАБЛИЦА SKILLS ============
class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(50), default="backend")


# ============ ТАБЛИЦА PROJECTS ============
class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), default="open")
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    applications: Mapped[list["Application"]] = relationship("Application", back_populates="project")
    
    # Many-to-many с Skills
    skills: Mapped[list["Skill"]] = relationship(
        "Skill",
        secondary=project_skill_association,
        backref="projects",
    )


# ============ ТАБЛИЦА APPLICATIONS ============
class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    applicant_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    
    compatibility_score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="applications")
    applicant: Mapped["User"] = relationship("User", back_populates="applications")
