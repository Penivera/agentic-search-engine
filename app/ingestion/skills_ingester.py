import os
from app.ingestion.skills_parser import SkillParser
from app.embeddings.vectorizer import Vectorizer
from app import SessionLocal
from api.schemas.database import SkillEmbedding, Platform
import json

def ingest_skills_from_directory(directory: str):
    """
    Traverse a directory to find SKILL.md files, parse them, generate embeddings, and
    store the results in the database.

    Args:
        directory (str): The root directory to scan.
    """
    session = SessionLocal()
    skill_parser = SkillParser()
    vectorizer = Vectorizer()

    for root, _, files in os.walk(directory):
        for file in files:
            if file == "SKILL.md":
                file_path = os.path.join(root, file)

                # Parse the skill metadata
                try:
                    skill_data = skill_parser.parse(file_path)
                    skill_text = json.dumps(skill_data)  # Convert metadata to string for vectorizing

                    # Generate embeddings
                    embedding = vectorizer.generate_embeddings([skill_text])[0]

                    # Store to database
                    platform = session.query(Platform).filter_by(name=skill_data["platform"]).first()
                    if not platform:
                        platform = Platform(name=skill_data["platform"], url="", homepage_uri="")
                        session.add(platform)
                        session.commit()

                    skill_embedding = SkillEmbedding(
                        platform_id=platform.id,
                        dimension=json.dumps(embedding),
                        capabilities=skill_text,
                    )
                    session.add(skill_embedding)
                    session.commit()
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")

    session.close()

# Example usage:
# ingest_skills_from_directory("/path/to/skills")