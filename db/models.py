# db/models.py
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True)
    query = Column(String(500))
    title = Column(String(500))
    summary_json = Column(Text)
    sources_json = Column(Text)
    full_text = Column(Text)
    status = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "query": self.query,
            "title": self.title,
            "summary": json.loads(self.summary_json) if self.summary_json else None,
            "sources": json.loads(self.sources_json) if self.sources_json else None,
            "full_text": self.full_text,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }

def get_session(db_url="sqlite:///reports.db"):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
