"""Validate instruction folders using only the Python standard library."""
from pathlib import Path
import re


def verify_folder(folder):
    folder = Path(folder).resolve()
    text = (folder / "SKILL.md").read_text()
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.S)
    assert frontmatter, f"missing frontmatter: {folder.name}"
    fields = dict(re.findall(r"^(name|description):\s*(.+)$", frontmatter[1], flags=re.M))
    assert fields.get("name") == folder.name, "skill name differs from folder"
    assert fields.get("description", "").strip(), "missing description"
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", folder.name) and len(folder.name) < 64
    assert text[frontmatter.end():].strip(), "empty instructions"
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
        if target.startswith(("https://", "http://", "mailto:", "#")):
            continue
        reference = (folder / target.split("#", 1)[0]).resolve()
        assert reference.is_relative_to(folder) and reference.is_file(), f"nonportable reference: {target}"
    return folder.name


def verify_skills(repo):
    folders = sorted(p.parent for kind in ("skills", "recipes")
                     for p in (Path(repo) / kind).glob("*/SKILL.md"))
    assert folders, "no skills found"
    return [verify_folder(folder) for folder in folders]


if __name__ == "__main__":
    names = verify_skills(Path(__file__).resolve().parents[1])
    print(f"Validated {len(names)} self-contained instruction folders without the reference package.")
