#!/usr/bin/env python3
"""Add the optional Jev tools to an existing brain without reinitializing it."""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import shutil
import sys
from pathlib import Path

BEGIN = '<!-- bsb-jev:start -->'
END = '<!-- bsb-jev:end -->'


def reject_links(path, root):
    for item in [path, *path.parents]:
        if item == root:
            break
        if item.is_symlink() or (hasattr(item,'is_junction') and item.is_junction()):
            raise ValueError('Linked installation directories are not supported')


def install(target: Path, *, enabled=False, hooks=False, roots=None, dry_run=False, enforce_reads=True):
    target = target.resolve(strict=True)
    source = Path(__file__).resolve().parents[1]
    if not target.is_dir():
        raise ValueError('Target must be an existing directory')
    if not ((target/'wiki').is_dir() or roots):
        raise ValueError('Existing wiki/ required, or supply explicit read-only search roots')
    roots = roots or ['wiki']
    if not enabled:
        enforce_reads = False
    for name in roots:
        p = target / name
        if Path(name).is_absolute() or '..' in Path(name).parts or not p.is_dir() or not p.resolve().is_relative_to(target):
            raise ValueError('Search roots must be existing directories inside target')
    files = ['scripts/bsb_jev.py','scripts/bsb_jev_hook.py','scripts/bsb_jev_focus.py',
             'scripts/bsb_jev_navigation.py','scripts/install_jev.py','docs/jev.md',
             'benchmark/JEV-2026-09-19.md','benchmark/JEV-LUNA-MAX-2026-09-19.md',
             'benchmark/JEV-NAVIGATION-LUNA-MAX-2026-09-19.md']
    for name in files:
        if not (source/name).is_file():
            raise ValueError(f'Missing installation source: {name}')
        dst = target/name
        reject_links(dst,target)
        if dst.is_symlink() or not dst.resolve().is_relative_to(target):
            raise ValueError('Installation target cannot escape via a link')
    instructions = 'CLAUDE.md' if (target/'CLAUDE.md').is_file() else 'AGENTS.md'
    for name in [instructions,'.gitignore','.bsb-jev/config.json','.agents/hooks.json','.claude/settings.json','.codex/hooks.json','bsb.config.md']:
        reject_links(target/name,target)
        if (target/name).is_symlink() or not (target/name).resolve().is_relative_to(target):
            raise ValueError('Linked configuration targets are not supported')
    if dry_run:
        return {'status':'dry_run','target':str(target),'files':files,'instructions':instructions,'enabled':enabled,'hooks':hooks,'roots':roots}
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backups=target/'.bsb-jev/install-backups'/stamp
    reject_links(backups,target)
    managed=files+[instructions,'.gitignore','.bsb-jev/config.json','.agents/hooks.json','.claude/settings.json','.codex/hooks.json','bsb.config.md']
    before={name:(target/name).read_bytes() if (target/name).is_file() else None for name in managed}
    backups.mkdir(parents=True)
    for name,content in before.items():
        if content is not None:
            p=backups/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
    try:
        for name in files:
            dst=target/name;dst.parent.mkdir(parents=True,exist_ok=True)
            if dst.resolve() != (source/name).resolve():shutil.copyfile(source/name,dst)
        rule=(f'{BEGIN}\n## Optional Jev assistance\n'
              'Read `docs/jev.md` when using the optional gateway. Check `python scripts/bsb_jev.py configure --status`.\n'
              'When enabled, use `python scripts/bsb_jev.py navigate "<question>" --need "<subquestion>"` for knowledge search,\n'
              'and `advise` / `plan` for placement or changes. Read the shortlisted pages fully; preserve source,\n'
              'domain and linking rules above. Jev ranks candidates; it cannot establish truth or global absence.\n'
              'Use `read <session> <path>` for offered full pages, `next <session>` for missing evidence/links, and\n'
              '`source "<literal>"` for exact local lookup. Deferred candidates remain reachable; no hard top-K pruning.\n'
              'Strict hooks gate supported native reads and shell calls. Do not bypass them via other tools.\n'
              f'{END}')
        if not (target/'wiki').is_dir():
            rule=rule.replace('and `advise` / `plan` for placement or changes.',
                              'This adapter is lookup-only; maintain append-only records through the existing harness workflow.')
        p=target/instructions;old_bytes=p.read_bytes() if p.exists() else b''
        old=old_bytes.decode('utf-8-sig')
        eol='\r\n' if b'\r\n' in old_bytes else '\n'
        rule=rule.replace('\n',eol)
        if BEGIN in old:
            start=old.index(BEGIN);end=old.index(END,start)+len(END)
            new=old[:start]+rule+old[end:]
        else:new=old.rstrip()+eol+eol+rule+eol
        p.write_text(new,encoding='utf-8-sig' if old_bytes.startswith(b'\xef\xbb\xbf') else 'utf-8',newline='')
        p=target/'.gitignore';old=p.read_text(encoding='utf-8') if p.exists() else ''
        ignore_lines=old.splitlines()
        for entry in ['.bsb-jev/','.agents/hooks.json','.codex/hooks.json']:
            if entry not in ignore_lines:ignore_lines.append(entry)
        p.write_text('\n'.join(ignore_lines)+'\n',encoding='utf-8',newline='')
        try:
            from .bsb_jev import configure_gateway
        except ImportError:
            from bsb_jev import configure_gateway
        configure_gateway(target,enabled=enabled,roots=roots,install_hooks=hooks,enforce_reads=enforce_reads)
        after={name:hashlib.sha256((target/name).read_bytes()).hexdigest() for name in managed if (target/name).is_file()}
        manifest={'status':'installed','target':str(target),'enabled':enabled,'hooks':hooks,'roots':roots,'backups':str(backups),'hashes':after,'previous_files':{name:hashlib.sha256(data).hexdigest() if data is not None else None for name,data in before.items()}}
        (backups/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
        return manifest
    except Exception:
        for name,data in before.items():
            p=target/name
            if data is None:p.unlink(missing_ok=True)
            else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target',type=Path,required=True)
    p.add_argument('--enabled',choices=['on','off'],default='off')
    p.add_argument('--hooks',action='store_true')
    p.add_argument('--enforce-reads',choices=['on','off'],default='on')
    p.add_argument('--roots',help='Comma-separated explicit read-only search directories (default wiki)')
    p.add_argument('--dry-run',action='store_true')
    a=p.parse_args()
    print(json.dumps(install(a.target,enabled=a.enabled=='on',hooks=a.hooks,roots=a.roots.split(',') if a.roots else None,dry_run=a.dry_run,enforce_reads=a.enforce_reads=='on'),indent=2))


if __name__=='__main__':main()
