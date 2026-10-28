"""Generate or check the small catalog read by the agent routing entrypoint."""
import argparse
import json
from pathlib import Path
import re


def build_catalog(repo):
    repo = Path(repo)
    entries = []
    for path in sorted((repo / 'skills').glob('*/SKILL.md')):
        text = path.read_text()
        header = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
        if not header:
            raise ValueError(f'missing skill frontmatter: {path.parent.name}')
        fields = dict(re.findall(r'^(name|description):\s*(.+)$', header[1], re.M))
        if fields.get('name') != path.parent.name or not fields.get('description', '').strip():
            raise ValueError(f'invalid skill metadata: {path.parent.name}')
        compatibility = path.parent / 'COMPATIBILITY.md'
        if not compatibility.is_file():
            raise ValueError(f'missing compatibility evidence: {path.parent.name}')
        entries.append({'id': fields['name'], 'description': fields['description'],
                        'input_modality': 'image' if (path.parent / 'image.json').is_file() else 'text',
                        'skill_path': path.relative_to(repo).as_posix(),
                        'compatibility_path': compatibility.relative_to(repo).as_posix()})
    if not entries:
        raise ValueError('no skills available for routing')
    return {'schema_version': 1, 'skills': entries}


def verify_catalog(repo):
    path = Path(repo) / 'skills/catalog.json'
    if json.loads(path.read_text()) != build_catalog(repo):
        raise ValueError('stale routing catalog; run python scripts/skill_catalog.py --write')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write', action='store_true', help='regenerate from the installed skill frontmatter')
    args = parser.parse_args()
    if args.write:
        (args.repo / 'skills/catalog.json').write_text(json.dumps(build_catalog(args.repo), indent=2) + '\n')
    else:
        verify_catalog(args.repo)
    print('Routing catalog matches the available skill instructions.')


if __name__ == '__main__':
    main()
