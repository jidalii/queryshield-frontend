from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, TIMESTAMP, Text, JSON, text
from sqlalchemy.orm import relationship, Session, aliased
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.sql import func, select
import streamlit as st

from models.analysis import *

Base = declarative_base()

# Define user_role and analysis_status ENUM types
user_role_enum = ENUM('analyst', 'data_owner', name='user_role', create_type=False)
analysis_status_enum = ENUM('Created', 'Ready', 'Running', 'Failed', 'Completed', name='analysis_status', create_type=False)

class User(Base):
    __tablename__ = 'users'
    uid = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    pin = Column(String(50), nullable=False)
    role = Column(user_role_enum)

class Analysis(Base):
    __tablename__ = 'analysis'
    aid = Column(Integer, primary_key=True)
    analysis_name = Column(Text, nullable=False)
    analyst_id = Column(Integer, ForeignKey('users.uid', ondelete='CASCADE'))
    time_created = Column(TIMESTAMP, server_default=func.now())
    details = Column(JSON, nullable=False)
    status = Column(analysis_status_enum)

    analyst = relationship('User', backref='analyses')

class AnalysisOwners(Base):
    __tablename__ = 'analysis_owners'
    
    analysis_id = Column(Integer, ForeignKey('analysis.aid', ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.uid', ondelete="CASCADE"), primary_key=True)

    # Define relationships
    analysis = relationship("Analysis", backref="owners")
    user = relationship("User", backref="owned_analyses")


def insert_new_analysis(engine, analysis: AnalysisCreation):
    with engine.connect() as conn:
        insert_sql = text(
            """
                INSERT INTO analysis (analysis_name, analyst_id, details, status)
                VALUES (:analysis_name, :analyst_id, :details, :status)
            """
        )
        try:
            conn.execute(
                insert_sql,
                {
                    "analysis_name": analysis.analysis_name,
                    "analyst_id": analysis.analyst_id,
                    "details": analysis.details,
                    "status": analysis.status,
                },
            )
            return True, None
        except Exception as e:
            return False, e
        
def fetch_all_analysis_catalog(engine):
    with Session(engine) as session:
        owner_count_subquery = (
            session.query(func.count(AnalysisOwners.user_id))
            .filter(AnalysisOwners.analysis_id == Analysis.aid)
            .correlate(Analysis)
            .label("owners_count")
        )
        query = (
            session.query(
                Analysis.aid,
                Analysis.analysis_name,
                Analysis.analyst_id,
                Analysis.time_created,
                Analysis.details,
                Analysis.status,
                (User.first_name + ' ' + User.last_name).label('analyst_name'),
                owner_count_subquery
            )
            .join(User, Analysis.analyst_id == User.uid)
        )
        return query.all()
    
def fetch_analyst_analysis_history(engine, analyst_id):
    with Session(engine) as session:
        owner_count_subquery = (
            session.query(func.count(AnalysisOwners.user_id))
            .filter(AnalysisOwners.analysis_id == Analysis.aid)
            .correlate(Analysis)
            .label("owners_count")
        )
        query = (
            session.query(
                Analysis.aid,
                Analysis.analysis_name,
                Analysis.time_created,
                Analysis.details,
                owner_count_subquery,
                Analysis.status,
            )
            .join(User, Analysis.analyst_id == User.uid)
            .filter(User.uid == analyst_id)
        )
        return query.all()
    
def fetch_single_analysis(engine, aid):
    with Session(engine) as session:
        query = (
            session.query(
                Analysis.aid,
                Analysis.analysis_name,
                Analysis.time_created,
                Analysis.details,
                Analysis.status,
            )
            .filter(Analysis.aid == aid)
        )
        return query.first()