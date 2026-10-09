# Endtenance

**A maintenance mode plugin for server owners** (Endstone / Minecraft Bedrock).

Turn maintenance on and only your staff can play. Everyone else is kicked with a message you wrote,
and your server list shows **"Under Maintenance"**. Turn it off and everything goes back to normal.

- Works with Endstone **0.11.x**, Python **3.11+** (including 3.14)
- Switch it on/off from a config file **or** with a command in game
- Custom kick title and description
- Changes the server list MOTD while maintenance is on
- Staff keep playing: operators and anyone with `maintenance.bypass`
- No extra dependencies, one small file of code

---

## 1. Install (2 minutes)

1. Go to the [Releases](../../releases) page and download the file ending in `.whl`
   (example: `endstone_endtenance-0.1.0-py3-none-any.whl`).
2. Put that file in your server's `plugins` folder.
   *Using Docker?* It is the folder you mounted as `plugins`.
3. Restart the server.
4. Look at the console. You should see: `Maintenance plugin enabled [false]`.

A config file is created automatically in the plugin's data folder, usually `plugins/endtenance/config.toml`.

## 2. Quick start

| I want to... | Do this |
|---|---|
| Turn maintenance **on** | Type `/maintenance true` in game (as op) or `maintenance true` in the console |
| Turn maintenance **off** | `/maintenance false` |
| Check if it is on | `/maintenance status` |
| Change the kick message | Edit `config.toml`, then run `/maintenance reload` |

## 3. Commands

Only operators can use these (the server console always can).

| Command | What it does |
|---|---|
| `/maintenance true` | Turns maintenance **on**, kicks everyone who is not staff, saves it in the config |
| `/maintenance false` | Turns maintenance **off**, saves it in the config |
| `/maintenance status` | Shows `Maintenance plugin enabled [true/false]` |
| `/maintenance reload` | Re-reads `config.toml` after you edited it |

You can also type `on` / `off` instead of `true` / `false`.
The same command is also available as `/maintainence`, `/maint` and `/endtenance`.

## 4. Config (`config.toml`)

```toml
enabled = false
title = "Server Under Maintenance!"
description = "Staffs are performing a maintainence, please try to join later."
change_motd = true
maintenance_motd = "Under Maintenance"
bypass_players = []
```

| Setting | What it means |
|---|---|
| `enabled` | `true` = maintenance ON, `false` = OFF |
| `title` | Big line on the kick screen |
| `description` | Smaller line under the title |
| `change_motd` | `true` = change the server list text while maintenance is on |
| `maintenance_motd` | The text shown in the server list during maintenance |
| `bypass_players` | Names that may join during maintenance, e.g. `["Steve", "Alex"]` |

Tips:
- Colour codes work, for example `title = "§cBack soon!"`.
- After editing, run `/maintenance reload`. No restart needed.
- When maintenance is off, your normal MOTD is untouched.

## 5. Letting staff join during maintenance

Operators always get in. For staff who are **not** op, pick one:

- **Easiest:** add their names to `bypass_players` in `config.toml`, then `/maintenance reload`.
- **Permissions plugin:** give them the permission `maintenance.bypass`.

| Permission | Default | Meaning |
|---|---|---|
| `maintenance.command` | op | Can use `/maintenance` |
| `maintenance.bypass` | op | Can stay on the server during maintenance |

## 6. Compatibility

- Built and written for **Endstone 0.11.x** (including 0.11.13), Python 3.11 or newer.
- Endstone is still a 0.x project, so a new Endstone version can change its plugin API. The plugin is written defensively
  (optional MOTD hook, fallbacks, nothing crashes the server), so it should keep working on newer versions,
  but this is not guaranteed. If a new Endstone version breaks it, please open an issue with your Endstone version and the console log.

## 7. Common questions

**If maintenance is `false`, does the plugin do anything?**
No. Everyone joins normally. The commands still work so you can turn it on later.

**Players are online when I turn it on. What happens?**
Everyone who is not staff is kicked right away. Staff stay.

**My MOTD did not change.**
The MOTD change needs an Endstone version that supports server list ping events.
If it does not, the console prints a warning when the plugin starts, and everything else still works.
Also check that `change_motd = true`, and refresh your server list.

**My staff got kicked.**
Make them op, give them `maintenance.bypass`, or add their name to `bypass_players`.

**I edited the config but nothing changed.**
Run `/maintenance reload`. If the file has a typo, the console shows an error and the old settings stay active.

**The plugin did not load.**
Check the file is a `.whl` inside `plugins/`, you are on Endstone 0.11.x, and read the console for errors.

## 8. Change it yourself

Everything is in one file: `endstone_endtenance/__init__.py`. You do not need to know much Python.

| Want to change... | Look for... |
|---|---|
| Default texts | `DEFAULT_TITLE`, `DEFAULT_DESCRIPTION`, `DEFAULT_MOTD` at the top |
| Colours / layout of the kick screen | `_kick_message` |
| Who may bypass | `_can_bypass` |
| The command and its name | `commands = {...}` and `on_command` |
| The default config file | `CONFIG_TEMPLATE` |

Example: make the kick message red and white. In `_kick_message` change it to
`return f"§c{self.title}§r\n§f{self.description_text}"`.

### Build it yourself

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/endtenance
cd endtenance
pip install build
python -m build --wheel
```

Your plugin file is now in `dist/`. Copy it to your server's `plugins/` folder and restart.

## 9. Contributing

Bug reports and pull requests are welcome, see [CONTRIBUTING.md](CONTRIBUTING.md).
Maintainers: see [RELEASING.md](RELEASING.md) for how to publish a new version.

## 10. License and credit

Licensed under the [Apache License 2.0](LICENSE). You can use, change and share this plugin, even commercially.
If you share it or a modified version, you must keep the [LICENSE](LICENSE) and [NOTICE](NOTICE) files,
which credit the original author, and mark files you changed.

Copyright 2026 YOUR NAME
