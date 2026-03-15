from pathlib import Path
from typing import Dict, Any

import yaml

class SkillParser:
    """
    A parser to handle SKILL.md ingestion and parsing.
    """
    @staticmethod
    def parse_skill_md(file_path: str) -> Dict[str, Any]:
        """
        Parse the SKILL.md file and return the extracted metadata.

        Args:
            file_path (str): Path to the SKILL.md file to parse.

        Returns:
            dict: Parsed metadata.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Skill file not found at {file_path}")

        with open(file_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        return data

# Example usage (will modify for dynamic detection later):
# skill = SkillParser.parse_skill_md("fastapi/.agents/skills/fastapi/SKILL.md")
# print(skill)