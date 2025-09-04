from sqlalchemy import create_engine, Column, String, Text, select, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite:///./yt_repurposer.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"
    # Only define columns needed for the query to avoid potential conflicts
    # if the actual schema has more columns or different definitions.
    id = Column(Integer, primary_key=True) 
    youtube_video_id = Column(String, nullable=False)
    repurposed_text = Column(Text, nullable=True)

def get_text_for_video(video_id_to_find: str):
    db = SessionLocal()
    try:
        # Using SQLAlchemy 2.0 style query
        stmt = select(Video.repurposed_text).where(Video.youtube_video_id == video_id_to_find)
        result = db.execute(stmt).scalar_one_or_none()
        if result:
            print(f"Raw repurposed_text for {video_id_to_find}:\n--START--\n{result}\n--END--")
        else:
            print(f"Video with youtube_video_id '{video_id_to_find}' not found.")
    finally:
        db.close()

if __name__ == "__main__":
    # Make sure this ID matches the one you're interested in.
    # This is the video ID mentioned in the problem description.
    target_video_id = "45QDaBOMFeQ" 
    get_text_for_video(target_video_id)