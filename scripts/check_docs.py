"""Validate edialog's local adaptation of the wellmanifest compact docs profile.

This original checker does not claim upstream adoption, Git ownership, CI
deployment or execution of acceptance tests. It performs no network calls.
"""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys

SECTIONS = ('summary', 'details', 'validation', 'risks')
MARKER = re.compile(r'<!-- docs:section ([a-z_]+) -->')
LINK = re.compile(r'!?\[[^\]]*\]\(([^)]+)\)')


def source_snapshot(root):
    paths = [root/'pyproject.toml']
    for directory in ('src', 'tests', 'examples', 'scripts'):
        paths.extend(p for p in (root/directory).rglob('*')
                     if p.is_file() and p.suffix in {'.py', '.json', '.emo', '.png'}
                     and '__pycache__' not in p.parts and not any(x.endswith('.egg-info') for x in p.parts))
    entries = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted(set(paths))}
    value = hashlib.sha256(json.dumps(entries, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return value, entries


def metadata(value):
    if not value.startswith('---\n') or '\n---\n' not in value[4:]:
        raise ValueError('Missing JSON metadata block')
    head, body = value[4:].split('\n---\n', 1)
    data = json.loads(head)
    if not isinstance(data, dict):
        raise ValueError('Metadata must be a JSON object')
    return data, body


def local_target(root, base, reference):
    path = (base/reference.split('#', 1)[0]).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Reference leaves the project')
    if not path.is_file():
        raise ValueError('Reference is missing: '+reference)
    return path


def prose(value):
    return re.sub(r'```[^\n]*\n.*?```', '', value, flags=re.S)


def check(root):
    errors, documents, redirects, sizes = [], [], [], []
    links_checked = 0
    profile = json.loads((root/'docs/profile.json').read_text(encoding='utf-8'))
    snapshot, source_files = source_snapshot(root)
    if profile.get('source_digest') != snapshot:
        errors.append('Source changed: review docs and refresh their source_digest')
    if profile.get('adoption') != 'local-format-adaptation' or profile.get('owner') != 'edialog':
        errors.append('This checker validates only the declared local edialog adaptation')
    index = (root/'docs/README.md').read_text(encoding='utf-8')
    ids = set()
    required = {'schema', 'id', 'kind', 'version', 'title', 'status', 'owner', 'scope',
                'updated', 'source_digest', 'priority', 'evidence'}
    for path in sorted((root/'docs').rglob('*.md')):
        if path.name == 'README.md':
            continue
        name = path.relative_to(root).as_posix()
        try:
            value = path.read_text(encoding='utf-8')
            meta, body = metadata(value)
            if meta.get('schema') == profile['redirect_schema']:
                if set(meta) != {'schema', 'owner', 'version', 'updated', 'targets'}:
                    raise ValueError('Unexpected redirect fields')
                if meta['owner'] != profile['owner'] or not isinstance(meta['targets'], list) or not meta['targets']:
                    raise ValueError('Invalid redirect owner/targets')
                for target in meta['targets']:
                    local_target(root, root, target)
                remaining = LINK.sub('', body)
                if any(line.strip() and not line.lstrip().startswith('#') for line in remaining.splitlines()):
                    raise ValueError('Redirect may contain only preserved headings and links')
                redirects.append(name)
                continue
            if set(meta) != required or meta['schema'] != profile['document_schema']:
                raise ValueError('Wrong document fields/schema')
            slug = meta['id']
            if not isinstance(slug, str) or not re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*', slug) or slug in ids:
                raise ValueError('Invalid or duplicate stable id')
            ids.add(slug)
            expected = Path('docs')/profile['directories'][meta['kind']]/(slug.replace('-', '_').upper()+'.md')
            if path.relative_to(root) != expected:
                raise ValueError('Unexpected canonical path: '+str(expected))
            if meta['owner'] != profile['owner'] or meta['scope'] != 'project':
                raise ValueError('Local owner/scope mismatch')
            if meta['source_digest'] != snapshot:
                raise ValueError('Document references another source snapshot')
            if type(meta['version']) is not int or meta['version'] < 1:
                raise ValueError('Version must be a positive integer')
            date.fromisoformat(meta['updated'])
            if meta['priority'] not in ('P0', 'P1', 'P2', 'P3') or meta['status'] not in ('draft', 'proposed', 'accepted', 'implemented', 'superseded'):
                raise ValueError('Invalid status/priority')
            if not isinstance(meta['title'], str) or not meta['title'].strip():
                raise ValueError('Missing title')
            if not isinstance(meta['evidence'], list) or not meta['evidence']:
                raise ValueError('Missing evidence references')
            for reference in meta['evidence']:
                if not isinstance(reference, str):
                    raise ValueError('Evidence reference must be a string')
                if not reference.startswith('https://'):
                    local_target(root, root, reference)
            matches = list(MARKER.finditer(body))
            if [m[1] for m in matches] != list(SECTIONS):
                raise ValueError('Expected summary/details/validation/risks once, in order')
            for i, match in enumerate(matches):
                section = body[match.end():matches[i+1].start() if i+1 < len(matches) else len(body)]
                substantive = '\n'.join(l for l in section.splitlines() if not l.lstrip().startswith('#'))
                if not substantive.strip():
                    raise ValueError('Empty section: '+match[1])
            limits = profile['limits']
            size = {'path': name, 'lines': len(value.splitlines()), 'words': len(value.split()), 'bytes': len(value.encode())}
            if any(size[k] > limits['max_'+k] for k in ('lines', 'words', 'bytes')):
                raise ValueError('Compact size limit exceeded')
            sizes.append(size)
            if path.relative_to(root/'docs').as_posix() not in index:
                raise ValueError('Document absent from docs/README.md index')
            documents.append(name)
        except (ValueError, KeyError, TypeError, OSError) as exc:
            errors.append(f'{name}: {exc}')
    # Check root navigation, canonical pages, redirects and the example catalog.
    markdown = [root/'README.md', root/'CHANGELOG.md', root/'examples/README.md']
    markdown.extend((root/'docs').rglob('*.md'))
    for path in markdown:
        try:
            for match in LINK.finditer(prose(path.read_text(encoding='utf-8'))):
                target = match[1].strip('<>')
                if target.startswith(('https://', 'http://', 'mailto:', '#')):
                    continue
                local_target(root, path.parent, target)
                links_checked += 1
        except (ValueError, OSError) as exc:
            errors.append(f'{path.relative_to(root)}: {exc}')
    for name in redirects:
        meta, _ = metadata((root/name).read_text(encoding='utf-8'))
        if any(t not in documents for t in meta['targets']):
            errors.append(name+': redirect target must be a canonical document')
    return {'ok': not errors, 'profile': profile['adoption'], 'documents_checked': len(documents),
            'redirects_checked': len(redirects), 'local_links_checked': links_checked,
            'source_digest': snapshot, 'source_files': len(source_files),
            'sizes': sizes, 'errors': errors,
            'upstream_ci_adoption_verified': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--print-source-digest', action='store_true')
    args = parser.parse_args(argv)
    if args.print_source_digest:
        print(source_snapshot(args.root)[0])
        return 0
    try:
        result = check(args.root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {'ok': False, 'errors': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
