"""Configuration Handler."""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

DEMO_DVN = "https://demo.dataverse.org"  # adjust if needed
# Default location for the Dataverse configuration file
DVN_CONFIG_FP = Path.home() / ".ibridges" / "dataverse.json"


class DVNConf:
    """Manage Dataverse configuration entries."""

    def __init__(self, config_fp: Path, parser=None):
        """Init."""
        self.config_fp = Path(config_fp)
        self.parser = parser
        self.dvns: Dict[str, dict] = {}
        self.cur_dvn: Optional[str] = None
        self._load()
        # Ensure default Dataverse entry always exists
        if DEMO_DVN not in self.dvns:
            self.dvns[DEMO_DVN] = {}
            self.cur_dvn = DEMO_DVN
            self.save()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self):
        if self.config_fp.exists():
            try:
                data = json.loads(self.config_fp.read_text(encoding="utf-8"))
                self.dvns = data.get("dvns", {})
                self.cur_dvn = data.get("cur_dvn")
            except Exception:
                self.dvns = {}
                self.cur_dvn = None
        else:
            self.dvns = {}
            self.cur_dvn = None

    def save(self):
        """Save current settings."""
        data = {"dvns": self.dvns, "cur_dvn": self.cur_dvn}
        self.config_fp.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # ------------------------------------------------------------------
    # URL / alias resolution
    # ------------------------------------------------------------------

    def get_entry(self, url_or_alias: str) -> Tuple[str, dict]:
        """Resolve alias or URL → (url, entry)."""
        # Direct URL match
        if url_or_alias in self.dvns:
            return url_or_alias, self.dvns[url_or_alias]

        # Alias match
        for url, entry in self.dvns.items():
            if entry.get("alias") == url_or_alias:
                return url, entry

        raise KeyError(f"No Dataverse entry found for '{url_or_alias}'.")

    def is_valid_url(self, url: str) -> bool:
        """Test URL."""
        return url.startswith("http://") or url.startswith("https://")

    # ------------------------------------------------------------------
    # Public setters (NEW)
    # ------------------------------------------------------------------

    def set_token(self, url_or_alias: str, token: str) -> None:
        """Set or update the token for a Dataverse entry."""
        url, entry = self.get_entry(url_or_alias)
        entry["token"] = token
        self.dvns[url] = entry
        self.save()

    def update_alias(self, url_or_alias: str, alias: str) -> None:
        """Assign or update an alias for a Dataverse entry."""
        # Ensure alias is not already used
        try:
            self.get_entry(alias)
            raise ValueError(f"Alias '{alias}' already exists.")
        except KeyError:
            pass  # alias is free

        url, entry = self.get_entry(url_or_alias)
        entry["alias"] = alias
        self.dvns[url] = entry
        self.save()

    def add_dataverse(
        self, url: str, alias: Optional[str] = None, token: Optional[str] = None
    ) -> None:
        """Create a new Dataverse configuration entry."""
        if not self.is_valid_url(url):
            raise ValueError(f"Invalid Dataverse URL: {url}")

        if url in self.dvns:
            raise ValueError(f"Dataverse '{url}' already exists.")

        entry = {}
        if alias:
            # Ensure alias is unique
            try:
                self.get_entry(alias)
                raise ValueError(f"Alias '{alias}' already exists.")
            except KeyError:
                entry["alias"] = alias

        if token:
            entry["token"] = token

        self.dvns[url] = entry
        self.save()

    def delete_entry(self, url_or_alias: str) -> None:
        """Delete a Dataverse entry entirely (except default)."""
        url, _ = self.get_entry(url_or_alias)

        if url == DEMO_DVN:
            raise KeyError("Cannot delete the default Dataverse configuration.")

        self.dvns.pop(url, None)
        self.save()

    # ------------------------------------------------------------------
    # Alias deletion (your required behavior)
    # ------------------------------------------------------------------

    def delete_alias(self, alias_or_url: str) -> None:
        """Delete the alias or full entry depending on whether it's the default DVN.

        Rules:
        - If alias_or_url refers to the default Dataverse:
            → Only remove the alias (if present).
        - Otherwise:
            → Delete the entire configuration entry.
        """
        url, entry = self.get_entry(alias_or_url)

        # Default DVN → only remove alias
        if url == DEMO_DVN:
            if "alias" in entry:
                entry.pop("alias")
                self.dvns[url] = entry
                self.save()
                return
            raise KeyError("Default Dataverse has no alias to remove.")

        # Non-default DVN → delete full entry
        self.dvns.pop(url, None)
        self.save()

    # ------------------------------------------------------------------
    # Active Dataverse
    # ------------------------------------------------------------------

    def set_dvn(self, url_or_alias: str) -> None:
        """Set the active Dataverse."""
        url, _ = self.get_entry(url_or_alias)
        self.cur_dvn = url
        self.save()

    def get_token(self, url_or_alias: str) -> Optional[str]:
        """Get token."""
        _, entry = self.get_entry(url_or_alias)
        return entry.get("token")


def show_available(dvn_conf) -> None:
    """Print all configured Dataverse entries in a readable table."""
    print("\nConfigured Dataverse instances:\n")

    if not dvn_conf.dvns:
        print("  (none configured)")
        return

    rows = []

    for url, entry in dvn_conf.dvns.items():
        alias = entry.get("alias")
        alias_display = alias if alias else "[no alias]"

        # URL validity
        url_valid = "✓" if dvn_conf.is_valid_url(url) else "✗"

        # Token validity
        token = entry.get("token")
        token_valid = "✓" if token else "✗"

        # Minimal current marker
        marker = "*" if dvn_conf.cur_dvn == url else " "

        rows.append((marker, alias_display, url, url_valid, token_valid))

    # Determine column widths
    alias_w = max(len(r[1]) for r in rows)
    url_w = max(len(r[2]) for r in rows)

    # Header
    print(f"{' '.ljust(1)} {'Alias'.ljust(alias_w)}   {'URL'.ljust(url_w)}   URL   Token")
    print("-" * (alias_w + url_w + 25))

    # Rows
    for marker, alias_display, url, url_valid, token_valid in rows:
        print(
            f"{marker} {alias_display.ljust(alias_w)}   "
            f"{url.ljust(url_w)}   "
            f"{url_valid}        {token_valid}"
        )

    print()
