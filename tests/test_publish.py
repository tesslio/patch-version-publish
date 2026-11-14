import json
import os
import pathlib
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.remote = self.root / 'remote.git'
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.gh_log = self.root / 'gh.jsonl'
        self.git('init', '--bare', '--initial-branch=main', str(self.remote), cwd=self.root)
        self.seed = self.root / 'seed'
        self.git('init', '--initial-branch=main', str(self.seed), cwd=self.root)
        self.identity(self.seed)
        for name in ['a', 'b']:
            manifest = self.seed / 'plugins' / name / '.tessl-plugin' / 'plugin.json'
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({'name': 'example/' + name, 'version': '1.0.0'}))
        (self.seed / 'README.md').write_text('original\n')
        self.git('add', '.', cwd=self.seed)
        self.git('commit', '-m', 'initial', cwd=self.seed)
        self.git('remote', 'add', 'origin', str(self.remote), cwd=self.seed)
        self.git('push', '-u', 'origin', 'main', cwd=self.seed)
        self.tool('jq', '''import json, sys
data = json.load(open(sys.argv[-1]))
print(data.get(sys.argv[-2].lstrip('.'), 'null'))
''')
        self.tool('tessl', '''import json, os, pathlib, sys
if sys.argv[1:3] == ['plugin', 'info']:
    print('Plugin exists')
elif sys.argv[1:3] == ['plugin', 'publish']:
    manifest = pathlib.Path(sys.argv[-1]) / '.tessl-plugin' / 'plugin.json'
    data = json.loads(manifest.read_text())
    if os.environ.get('TEST_BUMP', 'true') == 'true':
        data['version'] = '1.0.1'
        manifest.write_text(json.dumps(data) + '\\n')
else:
    raise SystemExit('unexpected Tessl command')
''')
        self.tool('gh', '''import json, os, sys
with open(os.environ['TEST_GH_LOG'], 'a') as stream:
    stream.write(json.dumps(sys.argv[1:]) + '\\n')
''')

    def tool(self, name, code):
        path = self.bin / name
        path.write_text('#!/usr/bin/env python3\n' + code)
        path.chmod(0o755)

    def git(self, *args, cwd):
        result = subprocess.run(['git', *args], cwd=cwd, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def identity(self, repo):
        self.git('config', 'user.name', 'Fixture User', cwd=repo)
        self.git('config', 'user.email', 'fixture@example.test', cwd=repo)

    def clone(self, name):
        repo = self.root / name
        self.git('clone', str(self.remote), str(repo), cwd=self.root)
        self.identity(repo)
        return repo

    def protect_main(self):
        hook = self.remote / 'hooks' / 'pre-receive'
        hook.write_text('#!/bin/sh\nwhile read old new ref; do\n  if [ "$ref" = refs/heads/main ]; then exit 1; fi\ndone\n')
        hook.chmod(0o755)

    def run_publish(self, repo, plugin='a', bump=True):
        lines = (ROOT / 'action.yml').read_text().splitlines()
        start = next(i for i, line in enumerate(lines) if line.strip() == 'run: |') + 1
        indent = len(lines[start]) - len(lines[start].lstrip())
        script = '\n'.join(line[indent:] for line in lines[start:])
        script = script.replace('${{ inputs.path }}', 'plugins/' + plugin)
        script_path = self.root / (repo.name + '-publish.sh')
        script_path.write_text(script + '\n')
        env = dict(os.environ,
            PATH=str(self.bin) + os.pathsep + os.environ['PATH'],
            ACTIONS_ID_TOKEN_REQUEST_URL='https://example.test/oidc',
            GITHUB_OUTPUT=str(self.root / 'output'),
            GITHUB_STEP_SUMMARY=str(self.root / 'summary'),
            GITHUB_REPOSITORY='owner/repo',
            GH_REPO='other/repository',
            GH_TOKEN='fixture-token',
            TEST_GH_LOG=str(self.gh_log),
            TEST_BUMP='true' if bump else 'false',
        )
        result = subprocess.run(['bash', '-eo', 'pipefail', str(script_path)], cwd=repo, env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unchanged_manifest_does_not_commit_other_staged_files(self):
        repo = self.clone('job')
        before = self.git('rev-parse', 'HEAD', cwd=repo)
        (repo / 'README.md').write_text('staged work\n')
        self.git('add', 'README.md', cwd=repo)
        self.run_publish(repo, bump=False)
        self.assertEqual(self.git('rev-parse', 'HEAD', cwd=repo), before)
        self.assertEqual(self.git('diff', '--cached', '--name-only', cwd=repo), 'README.md')

    def test_bump_commit_contains_only_the_manifest(self):
        repo = self.clone('job')
        (repo / 'README.md').write_text('staged work\n')
        self.git('add', 'README.md', cwd=repo)
        self.run_publish(repo)
        changed = self.git('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD', cwd=repo)
        self.assertEqual(changed, 'plugins/a/.tessl-plugin/plugin.json')
        self.assertEqual(self.git('diff', '--cached', '--name-only', cwd=repo), 'README.md')

    def test_same_version_in_two_plugins_uses_distinct_fallback_branches(self):
        self.protect_main()
        for plugin in ['a', 'b']:
            self.run_publish(self.clone('job-' + plugin), plugin=plugin)
        refs = self.git('for-each-ref', '--format=%(refname)', 'refs/heads', cwd=self.remote).splitlines()
        self.assertEqual(len([ref for ref in refs if ref.startswith('refs/heads/tessl-bump')]), 2)

    def test_fallback_pr_explicitly_targets_the_workflow_repository(self):
        self.protect_main()
        self.run_publish(self.clone('job'))
        args = json.loads(self.gh_log.read_text().splitlines()[-1])
        self.assertIn('--repo', args)
        self.assertEqual(args[args.index('--repo') + 1], 'owner/repo')


if __name__ == '__main__':
    unittest.main()
