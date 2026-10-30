
import re


SKILL_ALIASES = {
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript", "ts"],
    "C++": ["c++"],
    "C#": ["c#", "c sharp"],
    "Go": ["golang", "go programming"],
    "PHP": ["php"],
    "Swift": ["swift"],

    "React": ["react", "react.js", "reactjs"],
    "Next.js": ["next.js", "nextjs"],
    "Vue.js": ["vue.js", "vuejs"],
    "Node.js": ["node.js", "nodejs"],

    "Flask": ["flask"],
    "Django": ["django"],
    "Express": ["express.js", "express"],

    "SQL": ["sql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MySQL": ["mysql"],
    "MongoDB": ["mongodb"],
    "Redis": ["redis"],

    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services"],
    "Git": ["git"],
    "Linux": ["linux"],

    "REST APIs": [
        "rest api",
        "restful api",
        "rest apis"
    ],

    "Machine Learning": ["machine learning"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Scikit-learn": ["scikit-learn", "sklearn"],

    "Natural Language Processing": [
        "natural language processing",
        "nlp"
    ],

    "BERT": ["bert"],
    "Sentence-BERT": ["sentence-bert", "sentence bert"],

    "Cybersecurity": ["cybersecurity", "cyber security"],
    "Wireshark": ["wireshark"],
    "Burp Suite": ["burp suite"],
}


def contains_alias(text: str, alias: str) -> bool:
    """Check for an alias without matching unrelated words."""

    escaped = re.escape(alias.strip())
    pattern = rf"(?<!\w){escaped}(?!\w)"

    return re.search(
        pattern,
        text,
        flags=re.IGNORECASE
    ) is not None


def extract_skills(text: str) -> list[dict]:
    """
    Extract recognized skills and retain their supporting text.

    Evidence is preserved so later matching stages can
    assess where and how a skill was demonstrated.
    """

    results = []

    sentences = re.split(
        r"(?<=[.!?])\s+|\n+",
        text
    )

    for canonical_name, aliases in SKILL_ALIASES.items():

        evidence = []

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            found = any(
                contains_alias(sentence, alias)
                for alias in aliases
            )

            if found and sentence not in evidence:
                evidence.append(sentence)

        if evidence:
            results.append({
                "name": canonical_name,
                "evidence": evidence
            })

    return results
