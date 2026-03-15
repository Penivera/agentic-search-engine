import os
from app.ingestion.skills_parser import SkillParser
from app.services.vectorizer import Vectorizer
from app.db.session import SessionLocal
from app.models.database import SkillEmbedding, Platform
import json

async def ingest_skills_from_directory(directory: str):
    """
    Traverse a directory to find SKILL.md files, parse them, generate embeddings, and
    store the results in the database.

    Args:
        directory (str): The root directory to scan.
    """
    from sqlalchemy import select
    async with SessionLocal() as session:
        skill_parser = SkillParser()
        vectorizer = Vectorizer()

        for root, _, files in os.walk(directory):
            for file in files:
                if file == "SKILL.md":
                    file_path = os.path.join(root, file)

                    # Parse the skill metadata
                    try:
                        skill_data = skill_parser.parse_skill_md(file_path)
                        skill_text = json.dumps(skill_data)  # Convert metadata to string for vectorizing

                        # Generate embeddings
                        embedding = vectorizer.generate_embeddings([skill_text])[0]

                        # Store to database
                        result = await session.execute(select(Platform).filter_by(name=skill_data["platform"]))
                        platform = result.scalars().first()
                        if not platform:
                            platform = Platform(name=skill_data["platform"], url="", homepage_uri="")
                            session.add(platform)
                            await session.commit()
                            await session.refresh(platform)

                        skill_embedding = SkillEmbedding(
                            platform_id=platform.id,
                            dimension=embedding,
                            capabilities=skill_text,
                        )
                        session.add(skill_embedding)
                        await session.commit()
                    except Exception as e:
                        print(f"Failed to process {file_path}: {e}")

# Example usage:
# ingest_skills_from_directory("/path/to/skills")