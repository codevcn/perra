"""Perra command-line arguments parsing tests"""

import copy
import logging
import sys
from argparse import Namespace
from typing import Dict, Any
from unittest import mock

import pytest

from perra import perra as perra_module
from perra.perra import setup_arguments_parser
from perra.settings import SETTINGS_FILES_PATHS, Settings

DEFAULT_ARGS: Dict[str, Any] = {
    'all_sites': False,
    'auto_disable': False,
    'connections': 100,
    'cookie_file': None,
    'csv': False,
    'db_file': 'resources/data.json',
    'debug': False,
    'dns_resolver': 'async',
    'diagnose': False,
    'disable_extracting': False,
    'disable_recursive_search': False,
    'enrich': False,
    'folderoutput': 'reports',
    'html': True,
    'open_html': False,
    'graph': False,
    'neo4j': False,
    'id_type': 'username',
    'input_file': None,
    'ignore_ids_list': [],
    'info': False,
    'json': '',
    'new_site_to_submit': False,
    'no_color': False,
    'no_progressbar': False,
    'parse_url': '',
    'pdf': False,
    'permute': False,
    'print_check_errors': False,
    'print_not_found': False,
    'proxy': None,
    'reports_sorting': 'default',
    'retries': 0,
    'self_check': False,
    'site_list': [],
    'stats': False,
    'tags': '',
    'exclude_tags': '',
    'timeout': 30,
    'tor_proxy': 'socks5://127.0.0.1:9050',
    'i2p_proxy': 'http://127.0.0.1:4444',
    'top_sites': 500,
    'txt': False,
    'use_disabled_sites': False,
    'username': [],
    'verbose': False,
    'web': None,
    'with_domains': False,
    'xmind': False,
    'md': False,
    'ai': False,
    'ai_model': 'gpt-5.4',
    'no_autoupdate': False,
    'force_update': False,
    'no_update_check': False,
    'update': False,
    '_bg_update_check': False,
    '_bg_update_repo': None,
    '_bg_update_proxy': None,
    'cloudflare_bypass': False,
    'keywords': [],
}


def test_args_search_mode(argparser):
    args = argparser.parse_args('username'.split())

    assert args.username == ['username']

    want_args = dict(DEFAULT_ARGS)
    want_args.update({'username': ['username']})

    for arg in vars(args):
        assert getattr(args, arg) == want_args[arg]


def test_args_search_mode_several_usernames(argparser):
    args = argparser.parse_args('username1 username2'.split())

    assert args.username == ['username1', 'username2']

    want_args = dict(DEFAULT_ARGS)
    want_args.update({'username': ['username1', 'username2']})

    for arg in vars(args):
        assert getattr(args, arg) == want_args[arg]


def test_args_input_file(argparser):
    args = argparser.parse_args('--input-file ids.txt'.split())

    assert args.username == []
    assert args.input_file == 'ids.txt'

    want_args = dict(DEFAULT_ARGS)
    want_args.update({'input_file': 'ids.txt'})

    for arg in vars(args):
        assert getattr(args, arg) == want_args[arg]


def test_args_self_check_mode(argparser):
    args = argparser.parse_args('--self-check --site GitHub'.split())

    want_args = dict(DEFAULT_ARGS)
    want_args.update(
        {
            'self_check': True,
            'site_list': ['GitHub'],
            'username': [],
        }
    )

    for arg in vars(args):
        assert getattr(args, arg) == want_args[arg]


def test_args_multiple_sites(argparser):
    args = argparser.parse_args(
        '--site GitHub VK --site PornHub --site Taringa,Steam'.split()
    )

    want_args = dict(DEFAULT_ARGS)
    want_args.update(
        {
            'site_list': ['GitHub', 'PornHub', 'Taringa,Steam'],
            'username': ['VK'],
        }
    )

    for arg in vars(args):
        assert getattr(args, arg) == want_args[arg]


def test_args_exclude_tags(argparser):
    args = argparser.parse_args('--exclude-tags porn,dating username'.split())

    want_args = dict(DEFAULT_ARGS)
    want_args.update(
        {
            'exclude_tags': 'porn,dating',
            'username': ['username'],
        }
    )

    for arg in vars(args):
        assert getattr(args, arg) == want_args[arg]


def test_args_tags_with_exclude_tags(argparser):
    args = argparser.parse_args('--tags coding --exclude-tags porn username'.split())

    want_args = dict(DEFAULT_ARGS)
    want_args.update(
        {
            'tags': 'coding',
            'exclude_tags': 'porn',
            'username': ['username'],
        }
    )

    for arg in vars(args):
        assert getattr(args, arg) == want_args[arg]


def test_args_web_port(argparser):
    assert argparser.parse_args(['--web', '6000']).web == 6000


def test_args_web_without_port_uses_settings(settings):
    custom = copy.copy(settings)
    custom.web_interface_port = 8080

    assert setup_arguments_parser(custom).parse_args(['--web']).web == 8080


@pytest.fixture
def restore_perra_log_level():
    # main() sets the 'perra' logger level; later caplog-based tests depend on it.
    logger = logging.getLogger('perra')
    level = logger.level
    yield
    logger.setLevel(level)


@pytest.mark.parametrize('cli_args', [['--web'], ['--web', '0']])
async def test_web_mode_runs_on_settings_port(cli_args, restore_perra_log_level):
    real_load = Settings.load

    def load_with_custom_port(self, paths=None):
        # Only the bundled settings, so a developer's ~/.perra/settings.json cannot interfere.
        result = real_load(self, SETTINGS_FILES_PATHS[:1])
        self.web_interface_port = 8080
        return result

    with mock.patch.object(Settings, 'load', load_with_custom_port), mock.patch.object(
        sys, 'argv', ['perra', '--no-autoupdate', '--no-update-check', *cli_args]
    ), mock.patch('perra.web.app.app.run') as run:
        await perra_module.main()

    assert run.call_args.kwargs['port'] == 8080


def test_args_html_default_and_flags(argparser):
    default_parsed = argparser.parse_args(['username'])
    assert default_parsed.html is True
    assert default_parsed.open_html is False

    disabled = argparser.parse_args(['--no-html', 'username'])
    assert disabled.html is False
    assert disabled.open_html is False

    explicit_open = argparser.parse_args(['-H', '--open-html', 'username'])
    assert explicit_open.html is True
    assert explicit_open.open_html is True

    reenabled = argparser.parse_args(['--no-html', '--html', 'username'])
    assert reenabled.html is True


async def test_standalone_open_html_opens_latest_report(tmp_path, monkeypatch, restore_perra_log_level):
    """`perra --open-html` without targets opens the latest HTML report without loading DB."""
    import os

    monkeypatch.chdir(tmp_path)
    reports_dir = tmp_path / 'reports'
    reports_dir.mkdir()
    older = reports_dir / 'report_old_plain.html'
    newest = reports_dir / 'report_new_plain.html'
    older.write_text('<html>old</html>', encoding='utf-8')
    newest.write_text('<html>new</html>', encoding='utf-8')
    os.utime(older, ns=(1_000_000_000, 1_000_000_000))
    os.utime(newest, ns=(5_000_000_000, 5_000_000_000))

    isolated_state = tmp_path / '.perra' / 'last_html_report.json'
    real_load = Settings.load
    monkeypatch.delenv('CI', raising=False)
    monkeypatch.delenv('PERRA_NO_OPEN', raising=False)

    with mock.patch.object(
        Settings, 'load', lambda self, paths=None: real_load(self, SETTINGS_FILES_PATHS[:1])
    ), mock.patch.object(
        perra_module, '_get_last_html_state_path', return_value=isolated_state
    ), mock.patch.object(
        sys, 'argv', ['perra', '--open-html', '--no-update-check']
    ), mock.patch('perra.perra.PerraDatabase') as db_cls, mock.patch(
        'perra.perra.webbrowser.open', return_value=True
    ) as open_browser:
        await perra_module.main()

    assert db_cls.called is False
    open_browser.assert_called_once_with(newest.resolve().as_uri())


async def test_standalone_open_html_respects_env_and_exits_when_missing(
    tmp_path, monkeypatch, restore_perra_log_level
):
    monkeypatch.chdir(tmp_path)
    isolated_state = tmp_path / '.perra' / 'last_html_report.json'
    real_load = Settings.load

    # Missing reports -> exits cleanly with code 1
    with mock.patch.object(
        Settings, 'load', lambda self, paths=None: real_load(self, SETTINGS_FILES_PATHS[:1])
    ), mock.patch.object(
        perra_module, '_get_last_html_state_path', return_value=isolated_state
    ), mock.patch.object(
        sys, 'argv', ['perra', '--open-html', '--no-update-check']
    ), pytest.raises(SystemExit) as exc:
        await perra_module.main()
    assert exc.value.code == 1

    # With PERRA_NO_OPEN=1 and an existing report in -fo dir -> skips browser open, exits cleanly
    custom_dir = tmp_path / 'out'
    custom_dir.mkdir()
    report_file = custom_dir / 'report_alice_plain.html'
    report_file.write_text('<html>alice</html>', encoding='utf-8')
    monkeypatch.setenv('PERRA_NO_OPEN', '1')

    with mock.patch.object(
        Settings, 'load', lambda self, paths=None: real_load(self, SETTINGS_FILES_PATHS[:1])
    ), mock.patch.object(
        perra_module, '_get_last_html_state_path', return_value=isolated_state
    ), mock.patch.object(
        sys, 'argv', ['perra', '--open-html', '-fo', str(custom_dir), '--no-update-check']
    ), mock.patch('perra.perra.webbrowser.open') as open_browser:
        await perra_module.main()

    open_browser.assert_not_called()
