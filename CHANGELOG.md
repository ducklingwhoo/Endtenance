# Changelog

All notable changes to this project are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/), versioning follows [SemVer](https://semver.org/).

## [0.1.0] - 2026-10-09

First public release.

### Added
- Maintenance mode toggle (`enabled`) in `config.toml`.
- Configurable kick screen `title` and `description`.
- Only operators, players with `maintenance.bypass`, or names in `bypass_players` can play during maintenance.
- Server list MOTD changes to "Under Maintenance" while maintenance is on (`change_motd`, `maintenance_motd`).
- `/maintenance true|false|status|reload` command (aliases: `/maintainence`, `/maint`, `/endtenance`). Operator only.
- Console message `Maintenance plugin enabled [true/false]` on start and on every toggle.
- Toggling with the command also saves the new value to `config.toml`.
- An invalid `config.toml` no longer breaks the plugin; previous settings are kept and an error is logged.
