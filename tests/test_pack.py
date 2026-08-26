from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_required_skill_files_exist():
    required = [
        ROOT / 'skills/get-things-done/SKILL.md',
        ROOT / 'skills/building-gtd-domain-packs/SKILL.md',
        ROOT / 'skills/get-things-done/references/core-contract.md',
        ROOT / 'skills/get-things-done/references/domain-pack-spec.md',
        ROOT / 'skills/get-things-done/references/execution-brief.schema.json',
        ROOT / 'skills/get-things-done/domains/software.md',
        ROOT / 'skills/get-things-done/domains/marketing.md',
        ROOT / 'skills/get-things-done/domains/product.md',
        ROOT / 'skills/get-things-done/domains/research.md',
        ROOT / 'scripts/gtd.py',
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    assert not missing, f'missing: {missing}'


def test_skill_frontmatter_is_discoverable_and_not_workflow_summary():
    text = (ROOT / 'skills/get-things-done/SKILL.md').read_text()
    assert text.startswith('---\nname: get-things-done\n')
    assert 'description: Use when' in text.split('---', 2)[1]
    assert 'messy' in text.split('---', 2)[1].lower() or 'unclear' in text.split('---', 2)[1].lower()


def test_core_contract_contains_execution_invariants():
    text = (ROOT / 'skills/get-things-done/references/core-contract.md').read_text().lower()
    for phrase in [
        'fact', 'assumption', 'decision', 'unknown',
        'definition of ready', 'definition of done',
        'evidence', 'next executable action', 'handoff'
    ]:
        assert phrase in text


def test_domain_pack_spec_requires_inheritance_and_not_core_override():
    text = (ROOT / 'skills/get-things-done/references/domain-pack-spec.md').read_text().lower()
    assert 'inherit' in text
    assert 'must not override' in text
    assert 'completion checks' in text
    assert 'domain vocabulary' in text


def test_execution_brief_schema_is_valid_json_and_has_core_fields():
    schema_path = ROOT / 'skills/get-things-done/references/execution-brief.schema.json'
    schema = json.loads(schema_path.read_text())
    assert schema['type'] == 'object'
    required = set(schema['required'])
    for field in ['version', 'title', 'intent', 'status', 'scope', 'knowledge', 'decisions', 'workstreams', 'verification', 'next_action']:
        assert field in required


def test_cli_doctor_and_domain_listing():
    cmd = [sys.executable, str(ROOT / 'scripts/gtd.py'), 'doctor', '--root', str(ROOT)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PASS' in result.stdout

    cmd = [sys.executable, str(ROOT / 'scripts/gtd.py'), 'list-domains', '--root', str(ROOT)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    for name in ['software', 'marketing', 'product', 'research']:
        assert name in result.stdout


def test_cli_scaffolds_domain_pack(tmp_path):
    out = tmp_path / 'analytics.md'
    cmd = [
        sys.executable, str(ROOT / 'scripts/gtd.py'), 'new-domain',
        'analytics', '--name', 'Analytics', '--output', str(out)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    text = out.read_text()
    assert '# GTD Domain Pack: Analytics' in text
    assert '## Domain vocabulary' in text
    assert '## Completion checks' in text


def test_cli_scaffolds_and_validates_execution_brief(tmp_path):
    out = tmp_path / 'brief.json'
    cmd = [
        sys.executable, str(ROOT / 'scripts/gtd.py'), 'new-brief',
        '--title', 'Campaign measurement cleanup',
        '--domain', 'marketing',
        '--out', str(out)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(out.read_text())
    assert payload['title'] == 'Campaign measurement cleanup'
    assert payload['domain'] == 'marketing'

    cmd = [sys.executable, str(ROOT / 'scripts/gtd.py'), 'validate-brief', str(out), '--root', str(ROOT)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'VALID' in result.stdout


def test_domain_packs_follow_required_contract():
    headings = [
        '## Selection signals', '## Domain vocabulary', '## Diagnostic questions',
        '## Extra brief fields', '## Readiness additions', '## Workstream patterns',
        '## Review additions', '## Completion checks', '## Common traps'
    ]
    for path in sorted((ROOT / 'skills/get-things-done/domains').glob('*.md')):
        text = path.read_text()
        for heading in headings:
            assert text.count(heading) == 1, f'{path.name}: {heading}'
        assert 'extends: gtd-core-v1' in text


def test_examples_validate():
    for name in ['software-brief.json', 'marketing-brief.json']:
        path = ROOT / 'examples' / name
        assert path.exists()
        cmd = [sys.executable, str(ROOT / 'scripts/gtd.py'), 'validate-brief', str(path), '--root', str(ROOT)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr


def test_behavioral_evals_cover_pressure_classes():
    path = ROOT / 'evals/cases.jsonl'
    assert path.exists()
    cases = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    assert len(cases) >= 8
    joined = json.dumps(cases).lower()
    for phrase in ['fake-done', 'best-effort-no-questions', 'wrong-domain', 'messy-marketing', 'messy-software']:
        assert phrase in joined


def test_install_script_and_readme_exist():
    assert (ROOT / 'install.sh').exists()
    assert (ROOT / 'README.md').exists()
    result = subprocess.run(['bash', '-n', str(ROOT / 'install.sh')], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_individual_skill_folders_are_self_contained():
    main = ROOT / 'skills/get-things-done'
    builder = ROOT / 'skills/building-gtd-domain-packs'
    assert (main / 'scripts/gtd.py').exists()
    assert (builder / 'references/core-contract.md').exists()
    assert (builder / 'references/domain-pack-spec.md').exists()
    assert (builder / 'references/core-contract.md').read_text() == (main / 'references/core-contract.md').read_text()
    assert (builder / 'references/domain-pack-spec.md').read_text() == (main / 'references/domain-pack-spec.md').read_text()


def test_pack_cli_wrapper_executes_canonical_skill_cli():
    wrapper = ROOT / 'scripts/gtd.py'
    canonical = ROOT / 'skills/get-things-done/scripts/gtd.py'
    assert wrapper.exists() and canonical.exists()
    result = subprocess.run([sys.executable, str(wrapper), 'doctor', '--root', str(ROOT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_package_skills_creates_valid_archives(tmp_path):
    out_dir = tmp_path / 'dist'
    cmd = [sys.executable, str(ROOT / 'scripts/gtd.py'), 'package', '--out', str(out_dir), '--root', str(ROOT)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PASS' in result.stdout

    import zipfile
    for name in ['get-things-done.zip', 'building-gtd-domain-packs.zip']:
        zip_path = out_dir / name
        assert zip_path.exists()
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert 'SKILL.md' in names
            assert 'assets/small-logo.svg' in names
            assert 'assets/large-logo.svg' in names
            assert 'agents/openai.yaml' in names

