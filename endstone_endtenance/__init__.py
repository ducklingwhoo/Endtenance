# Copyright 2026 Duckyy
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Endtenance - a maintenance mode plugin for Endstone 0.11.x server owners.

When maintenance mode is on, only operators, players with the
`maintenance.bypass` permission, or names listed in `bypass_players`
in config.toml may stay on the server. Everyone else is kicked, and the
server list MOTD is changed to "Under Maintenance".

Project: https://github.com/ducklingwhoo/endtenance
"""

import json
import tomllib
from pathlib import Path

from endstone import Player
from endstone.command import Command, CommandSender
from endstone.event import PlayerJoinEvent, event_handler
from endstone.plugin import Plugin

# The MOTD hook is optional: if this Endstone build has no ServerListPingEvent,
# the plugin still works, it just can't change the MOTD.
try:
    from endstone.event import ServerListPingEvent
except ImportError:  # pragma: no cover
    ServerListPingEvent = None

DEFAULT_TITLE = "Server Under Maintenance!"
DEFAULT_DESCRIPTION = "Staffs are performing a maintainence, please try to join later."
DEFAULT_MOTD = "Under Maintenance"

CONFIG_TEMPLATE = """# Endtenance configuration
# After editing this file, run /maintenance reload (or restart the server).

# true  = maintenance mode ON  (only ops / maintenance.bypass can play)
# false = maintenance mode OFF (everyone can play)
enabled = {enabled}

# Text shown on the kick screen. Colour codes (the section sign + a code) work.
title = {title}
description = {description}

# Change the server list MOTD while maintenance is ON?
# The normal MOTD comes back by itself when maintenance is turned OFF.
change_motd = {change_motd}
maintenance_motd = {maintenance_motd}

# Optional: player names allowed to join during maintenance even without the
# maintenance.bypass permission. Example: ["Steve", "Alex"]
bypass_players = {bypass_players}
"""


class EndtenancePlugin(Plugin):
    name = "endtenance"
    prefix = "Endtenance"
    version = "0.1.0"
    api_version = "0.11"
    description = "Endtenance - A maintenance mode plugin for server owners"
    authors = ["YOUR NAME"]
    website = "https://github.com/YOUR_GITHUB_USERNAME/endtenance"

    commands = {
        "maintenance": {
            "description": "Toggle or check maintenance mode",
            "usages": ["/maintenance <action: message>"],
            "aliases": ["maintainence", "maint", "endtenance"],
            "permissions": ["maintenance.command"],
        }
    }

    permissions = {
        "maintenance.command": {
            "description": "Allows use of /maintenance",
            "default": "op",
        },
        "maintenance.bypass": {
            "description": "Allows joining while maintenance mode is on",
            "default": "op",
        },
    }

    # ---------------------------------------------------------------- state
    def __init__(self):
        super().__init__()
        self.enabled = False
        self.title = DEFAULT_TITLE
        self.description_text = DEFAULT_DESCRIPTION
        self.change_motd = True
        self.maintenance_motd = DEFAULT_MOTD
        self.bypass_players: list[str] = []

    @property
    def _config_path(self) -> Path:
        return Path(self.data_folder) / "config.toml"

    # -------------------------------------------------------------- config
    def _write_config(self) -> None:
        path = self._config_path
        path.parent.mkdir(parents=True, exist_ok=True)
        text = CONFIG_TEMPLATE.format(
            enabled="true" if self.enabled else "false",
            title=json.dumps(self.title, ensure_ascii=False),
            description=json.dumps(self.description_text, ensure_ascii=False),
            change_motd="true" if self.change_motd else "false",
            maintenance_motd=json.dumps(self.maintenance_motd, ensure_ascii=False),
            bypass_players=json.dumps(self.bypass_players, ensure_ascii=False),
        )
        path.write_text(text, encoding="utf-8")

    def _load_config(self) -> bool:
        """Read config.toml. Returns False (keeping old values) if it is invalid."""
        path = self._config_path
        if not path.exists():
            self._write_config()
            return True
        try:
            with path.open("rb") as f:
                data = tomllib.load(f)
        except Exception as e:  # broken TOML, unreadable file, ...
            self.logger.error(f"Could not read config.toml, keeping previous settings: {e}")
            return False

        enabled = data.get("enabled", False)
        if not isinstance(enabled, bool):
            self.logger.warning("'enabled' must be true or false; using false.")
            enabled = False
        change_motd = data.get("change_motd", True)
        if not isinstance(change_motd, bool):
            self.logger.warning("'change_motd' must be true or false; using true.")
            change_motd = True
        bypass = data.get("bypass_players", [])
        if not isinstance(bypass, list):
            bypass = []

        self.enabled = enabled
        self.title = str(data.get("title", DEFAULT_TITLE))
        self.description_text = str(data.get("description", DEFAULT_DESCRIPTION))
        self.change_motd = change_motd
        self.maintenance_motd = str(data.get("maintenance_motd", DEFAULT_MOTD))
        self.bypass_players = [str(n).lower() for n in bypass]
        return True

    # ----------------------------------------------------------- lifecycle
    def on_enable(self) -> None:
        self._load_config()
        self.register_events(self)
        self.logger.info(f"Maintenance plugin enabled [{str(self.enabled).lower()}]")
        if ServerListPingEvent is None:
            self.logger.warning(
                "This Endstone version has no ServerListPingEvent; the MOTD will not be changed."
            )
        if self.enabled:
            self._kick_non_staff()

    def on_disable(self) -> None:
        self.logger.info("Endtenance disabled")

    # -------------------------------------------------------------- helpers
    def _can_bypass(self, player: Player) -> bool:
        try:
            return (
                player.is_op
                or player.has_permission("maintenance.bypass")
                or player.name.lower() in self.bypass_players
            )
        except Exception:
            return False

    def _kick_message(self) -> str:
        return f"§c{self.title}§r\n§7{self.description_text}"

    def _kick(self, player: Player) -> None:
        try:
            if self.enabled and not self._can_bypass(player):
                player.kick(self._kick_message())
        except Exception as e:  # player may already have left
            self.logger.debug(f"Kick skipped: {e}")

    def _kick_non_staff(self) -> None:
        for player in list(self.server.online_players):
            self._kick(player)

    def _set_enabled(self, value: bool) -> None:
        self.enabled = value
        self._write_config()  # keep config.toml in sync with the command
        self.logger.info(f"Maintenance plugin enabled [{str(value).lower()}]")
        if value:
            self._kick_non_staff()

    # --------------------------------------------------------------- events
    @event_handler
    def on_player_join(self, event: PlayerJoinEvent) -> None:
        if not self.enabled:
            return
        player = event.player
        if self._can_bypass(player):
            return
        # Kick one tick later so the player is fully in the world first.
        # If the scheduler API ever changes, fall back to kicking right away.
        try:
            self.server.scheduler.run_task(self, lambda: self._kick(player), delay=1)
        except Exception as e:
            self.logger.debug(f"Scheduler unavailable, kicking immediately: {e}")
            self._kick(player)

    if ServerListPingEvent is not None:

        @event_handler
        def on_server_list_ping(self, event: ServerListPingEvent) -> None:
            # Runs every time the server list pings us, so the MOTD goes back
            # to normal automatically as soon as maintenance is turned off.
            if self.enabled and self.change_motd:
                try:
                    event.motd = self.maintenance_motd
                except Exception as e:
                    self.logger.debug(f"Could not change MOTD: {e}")

    # ------------------------------------------------------------- commands
    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if command.name != "maintenance":
            return False

        action = " ".join(args).strip().lower()

        if action in ("true", "on"):
            self._set_enabled(True)
            sender.send_message("§aMaintenance mode enabled [true]")
        elif action in ("false", "off"):
            self._set_enabled(False)
            sender.send_message("§aMaintenance mode disabled [false]")
        elif action == "status":
            sender.send_message(f"Maintenance plugin enabled [{str(self.enabled).lower()}]")
        elif action == "reload":
            if self._load_config():
                sender.send_message(
                    f"§aConfig reloaded. Maintenance plugin enabled [{str(self.enabled).lower()}]"
                )
                if self.enabled:
                    self._kick_non_staff()
            else:
                sender.send_message("§cConfig is invalid; kept previous settings. See console.")
        else:
            sender.send_message("§eUsage: /maintenance <true|false|status|reload>")
        return True
￼Enter# Copyright 2026 YOUR NAME
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Endtenance - a maintenance mode plugin for Endstone 0.11.x server owners.

When maintenance mode is on, only operators, players with the
`maintenance.bypass` permission, or names listed in `bypass_players`
in config.toml may stay on the server. Everyone else is kicked, and the
server list MOTD is changed to "Under Maintenance".

Project: https://github.com/YOUR_GITHUB_USERNAME/endtenance
"""

import json
import tomllib
from pathlib import Path

from endstone import Player
from endstone.command import Command, CommandSender
from endstone.event import PlayerJoinEvent, event_handler
from endstone.plugin import Plugin

# The MOTD hook is optional: if this Endstone build has no ServerListPingEvent,
# the plugin still works, it just can't change the MOTD.
try:
    from endstone.event import ServerListPingEvent
except ImportError:  # pragma: no cover
    ServerListPingEvent = None

DEFAULT_TITLE = "Server Under Maintenance!"
DEFAULT_DESCRIPTION = "Staffs are performing a maintainence, please try to join later."
DEFAULT_MOTD = "Under Maintenance"

_TEMPLATE = """# Endtenance configuration
# After editing this file, run /maintenance reload (or restart the server).

# true  = maintenance mode ON  (only ops / maintenance.bypass can play)
# false = maintenance mode OFF (everyone can play)
enabled = {enabled}

# Text shown on the kick screen. Colour codes (the section sign + a code) work.
title = {title}
description = {description}

# Change the server list MOTD while maintenance is ON?
# The normal MOTD comes back by itself when maintenance is turned OFF.
change_motd = {change_motd}
maintenance_motd = {maintenance_motd}

# Optional: player names allowed to join during maintenance even without the
# maintenance.bypass permission. Example: ["Steve", "Alex"]
bypass_players = {bypass_players}
"""


class EndtenancePlugin(Plugin):
    name = "endtenance"
    prefix = "Endtenance"
    version = "0.1.0"
    api_version = "0.11"
    description = "Endtenance - A maintenance mode plugin for server owners"
    authors = ["YOUR NAME"]
    website = "https://github.com/YOUR_GITHUB_USERNAME/endtenance"

    commands = {
        "maintenance": {
            "description": "Toggle or check maintenance mode",
            "usages": ["/maintenance <action: message>"],
            "aliases": ["maintainence", "maint", "endtenance"],
            "permissions": ["maintenance.command"],
        }
    }

    permissions = {
        "maintenance.command": {
            "description": "Allows use of /maintenance",
            "default": "op",
        },
        "maintenance.bypass": {
            "description": "Allows joining while maintenance mode is on",
            "default": "op",
        },
    }

    # ---------------------------------------------------------------- state
    def __init__(self):
        super().__init__()
        self.enabled = False
        self.title = DEFAULT_TITLE
        self.description_text = DEFAULT_DESCRIPTION
        self.change_motd = True
        self.maintenance_motd = DEFAULT_MOTD
        self.bypass_players: list[str] = []

    @property
    def _config_path(self) -> Path:
        return Path(self.data_folder) / "config.toml"

    # -------------------------------------------------------------- config
    def _write_config(self) -> None:
        path = self._config_path
        path.parent.mkdir(parents=True, exist_ok=True)
        text = CONFIG_TEMPLATE.format(
            enabled="true" if self.enabled else "false",
            title=json.dumps(self.title, ensure_ascii=False),
            description=json.dumps(self.description_text, ensure_ascii=False),
            change_motd="true" if self.change_motd else "false",
            maintenance_motd=json.dumps(self.maintenance_motd, ensure_ascii=False),
            bypass_players=json.dumps(self.bypass_players, ensure_ascii=False),
        )
        path.write_text(text, encoding="utf-8")

    def _load_config(self) -> bool:
        """Read config.toml. Returns False (keeping old values) if it is invalid."""
        path = self._config_path
        if not path.exists():
            self._write_config()
            return True
        try:
            with path.open("rb") as f:
                data = tomllib.load(f)
        except Exception as e:  # broken TOML, unreadable file, ...
            self.logger.error(f"Could not read config.toml, keeping previous settings: {e}")
            return False

        enabled = data.get("enabled", False)
        if not isinstance(enabled, bool):
            self.logger.warning("'enabled' must be true or false; using false.")
            enabled = False
        change_motd = data.get("change_motd", True)
        if not isinstance(change_motd, bool):
            self.logger.warning("'change_motd' must be true or false; using true.")
            change_motd = True
        bypass = data.get("bypass_players", [])
        if not isinstance(bypass, list):
            bypass = []

        self.enabled = enabled
        self.title = str(data.get("title", DEFAULT_TITLE))
        self.description_text = str(data.get("description", DEFAULT_DESCRIPTION))
