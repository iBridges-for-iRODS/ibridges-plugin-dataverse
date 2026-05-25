"""Cleaned-up Dataverse configuration manager."""

from __future__ import annotations

import argparse
import httpx
import json
import warnings
from pathlib import Path
from typing import Dict, Tuple, Union
from urllib.parse import urlparse

DVN_CONFIG_FP = Path.home() / ".dvn" / "dvn.json"
DEMO_DVN = "https://demo.dataverse.org"


class DVNConf:
    """Manage multiple Dataverse configurations stored in ~/.dvn/dvn.json."""

    def __init__(
        self,
        parser: argparse.ArgumentParser | None = None,
        config_path: Union[str, Path] = DVN_CONFIG_FP,
    ) -> None:
        self.parser = parser
        self.config_path = Path(config_path)

        if not self.config_path.exists():
            self._ensure_parent()
            self.reset()
        else:
            self._load()

        self.validate()

    def _ensure_parent(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> None:
        try:
            with self.config_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            warnings.warn(f"Invalid config at {self.config_path}, resetting.")
            self.reset()
            return

        self.dvns: Dict[str, dict] = data.get("dvns", {})
        self.cur_dvn: str = data.get("cur_dvn", DEMO_DVN)

    def save(self) -> None:
        self._ensure_parent()
        with self.config_path.open("w", encoding="utf-8") as f:
            json.dump(
                {"cur_dvn": self.cur_dvn, "dvns": self.dvns},
                f,
                indent=4,
            )

    def validate(self) -> None:
        """Validate structure, URLs, aliases, and current selection."""
        changed = False

        # Ensure dvns is a dict
        if not isinstance(self.dvns, dict):
            warnings.warn("Dataverse config corrupted; resetting.")
            self.reset()
            return

        # Ensure default exists
        if DEMO_DVN not in self.dvns:
            warnings.warn("Default Dataverse missing; restoring.")
            self.dvns[DEMO_DVN] = {"alias": "demo"}
            changed = True

        # Validate entries
        aliases = set()
        cleaned = {}

        for url, entry in self.dvns.items():
            alias = entry.get("alias")

            if not self.is_valid_url(url):
                warnings.warn(f"Invalid Dataverse URL '{url}', removing.")
                changed = True
                continue

            if alias and alias in aliases:
                warnings.warn(f"Duplicate alias '{alias}', removing entry '{url}'.")
                changed = True
                continue

            cleaned[url] = entry
            if alias:
                aliases.add(alias)

        self.dvns = cleaned

        # Ensure current DVN is valid
        if self.cur_dvn not in self.dvns:
            warnings.warn("Current Dataverse invalid; switching to first available.")
            self.cur_dvn = next(iter(self.dvns))
            changed = True

        if changed:
            self.save()

    def reset(self) -> None:
        """Reset to default configuration."""
        self.dvns = {DEMO_DVN: {"alias": "demo"}}
        self.cur_dvn = DEMO_DVN
        self.save()

    def get_entry(self, url_or_alias: Union[str, None] = None) -> Tuple[str, dict]:
        """Return (url, entry) for a URL or alias."""
        key = self.cur_dvn if url_or_alias is None else str(url_or_alias)

        # Direct URL match
        if key in self.dvns:
            return key, self.dvns[key]

        # Alias match
        for url, entry in self.dvns.items():
            if entry.get("alias") == key:
                return url, entry

        raise KeyError(f"Cannot find entry '{key}'")

    def set_dvn(self, url_or_alias: Union[str, None]) -> None:
        """Set the current Dataverse by URL or alias."""
        if url_or_alias == "":
            return

        key = DEMO_DVN if url_or_alias is None else str(url_or_alias)

        try:
            url, _ = self.get_entry(key)
        except KeyError:
            # New URL
            if not self.is_valid_url(key):
                if self.parser:
                    self.parser.error(f"Dataverse {key} is not a valid URL.")
                raise TypeError(f"Dataverse {key} is not a valid URL.")
            self.dvns[key] = {}
            url = key

        if self.cur_dvn != url:
            self.cur_dvn = url
            self.save()

    def set_alias(self, alias: str, url: str) -> None:
        """Assign an alias to a Dataverse URL."""
        # Alias already exists
        try:
            self.get_entry(alias)
            if self.parser:
                self.parser.error(f"Alias '{alias}' already exists.")
            raise ValueError(f"Alias '{alias}' already exists.")
        except KeyError:
            pass

        # URL exists → update alias
        try:
            url, entry = self.get_entry(url)
            entry["alias"] = alias
        except KeyError:
            # New entry
            self.dvns[url] = {"alias": alias}

        self.save()

    def delete_alias(self, alias: str) -> None:
        """Remove alias or entire entry."""
        try:
            url, entry = self.get_entry(alias)
        except KeyError:
            if self.parser:
                self.parser.error(f"Alias '{alias}' does not exist.")
            raise

        if url == DEMO_DVN:
            # Cannot delete default
            if "alias" not in entry:
                if self.parser:
                    self.parser.error("Cannot remove default Dataverse.")
                raise KeyError("Cannot remove default Dataverse.")
            entry.pop("alias")
        else:
            self.dvns.pop(url)

        self.save()

    @staticmethod
    def is_valid_url(url: str) -> bool:
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except ValueError:
            return False

def show_available(dvn_conf):
    """Print available Dataverse configurations and highlight active one."""

    for url, entry in dvn_conf.dvns.items():
        is_active = dvn_conf.cur_dvn in (url, entry.get("alias"))
        prefix = "*" if is_active else " "

        alias = entry.get("alias", "[no alias]")
        token = entry.get("token")

        # Default status
        token_status = "[no token]" if not token else "[token set]"

        # Check if URL is a Dataverse instance
        try:
            resp = httpx.get(f"{url}/api/info/version", timeout=3.0)
            if resp.status_code == 200:
                url_status = "[dataverse OK]"
            else:
                url_status = "[invalid dataverse]"
        except Exception:
            url_status = "[unreachable]"

        # If URL is valid AND token exists → validate token
        if token and url_status == "[dataverse OK]":
            try:
                resp = httpx.get(
                    f"{url}/api/users/:me",
                    headers={"X-Dataverse-key": token},
                    timeout=3.0,
                )
                if resp.status_code == 200:
                    token_status = "[token OK]"
                else:
                    token_status = "[token invalid]"
            except Exception:
                token_status = "[token invalid]"

        print(f"{prefix} {alias: <15} -> {url: <35} {url_status} {token_status}")

