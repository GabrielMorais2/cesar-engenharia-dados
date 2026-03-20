from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Country(Base):
    __tablename__ = "country"

    id = Column(Integer, primary_key=True, autoincrement=True)
    iso2 = Column(String(2), nullable=False, unique=True)
    name = Column(String(120), nullable=False)

    universities = relationship("University", back_populates="country")


class University(Base):
    __tablename__ = "university"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country_id = Column(Integer, ForeignKey("country.id"), nullable=False)
    name = Column(String(300), nullable=False)
    state_province = Column(String(120), nullable=True)

    country = relationship("Country", back_populates="universities")
    domains = relationship("UniversityDomain", back_populates="university", cascade="all, delete-orphan")
    web_pages = relationship("UniversityWebPage", back_populates="university", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("country_id", "name", "state_province", name="uk_university"),
        Index("ix_university_country", "country_id"),
        Index("ix_university_name", "name"),
    )


class UniversityDomain(Base):
    __tablename__ = "university_domain"

    id = Column(Integer, primary_key=True, autoincrement=True)
    university_id = Column(Integer, ForeignKey("university.id"), nullable=False)
    domain = Column(String(253), nullable=False)

    university = relationship("University", back_populates="domains")

    __table_args__ = (
        UniqueConstraint("university_id", "domain", name="uk_university_domain"),
        Index("ix_domain_domain", "domain"),
    )


class UniversityWebPage(Base):
    __tablename__ = "university_webpage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    university_id = Column(Integer, ForeignKey("university.id"), nullable=False)
    url = Column(String(2048), nullable=False)

    university = relationship("University", back_populates="web_pages")

    __table_args__ = (
        UniqueConstraint("university_id", "url", name="uk_university_webpage"),
        Index("ix_webpage_url", "url"),
    )


engine = create_engine("sqlite:///unis.db")
Base.metadata.create_all(engine)