"""Config functions."""

import argparse
import json
import os
import warnings
from pathlib import Path
from typing import Union
from urllib.parse import urlparse

DVN_CONFIG_FP = Path.home() / ".dvn" / "dvn.json"
DEMO_DVN = "https://demo.dataverse.org"


class DVNConf:
    """Interface to the dataverse config file."""

    def __init__(
        self, parser: argparse.ArgumentParser, config_path: Union[str, Path] = DVN_CONFIG_FP
    ):
        """Read configuration file and validate it."""
        self.config_path = config_path
        self.parser = parser
        if not self.config_path.is_file():
            os.makedirs(self.config_path.parent)
            self.reset()

        try:
            with open(self.config_path, "r", encoding="utf-8") as handle:
                dvn_conf = json.load(handle)
                self.dvns = dvn_conf["dvns"]
                self.cur_dvn = dvn_conf.get("cur_dvn", DEMO_DVN)
        except Exception as exc:  # pylint: disable=W0718
            if isinstance(exc, FileNotFoundError):
                print("File not found")
                warnings.warn(f"{self.config_path} not found. Use default {DVN_CONFIG_FP}.")
                self.reset()
            else:
                print(repr(exc))
                warnings.warn(f"{self.config_path} not found. Use default {DVN_CONFIG_FP}.")
                self.reset()

        self.validate()

    def validate(self):
        """Validate the Dataverse configuration.

        Check whether the types are correct, the default Dataverse URL has not been removed,
        aliases are unique and more. If the assumptions are violated, try to reset the configuration
        to create a working configuration file.
        """
        changed = False
        try:
            if not isinstance(self.dvns, dict):
                raise ValueError("Dataverses list is not a dictionary.")
            if DEMO_DVN not in self.dvns:
                raise ValueError("Default Dataverse URL not in configuration file.")
            if not isinstance(self.cur_dvn, str):
                raise ValueError(
                    f"Current Dataverse URL should be a string not {type(self.cur_dvn)}"
                )
            cur_aliases = set()
            new_dvns = {}
            for url, entry in self.dvns.items():
                if url != DEMO_DVN and not self.is_valid_url(url):
                    warnings.warn(f"Dataverse '{url}' is not a valid URL, " "removing the entry.")
                    changed = True
                elif entry.get("alias", None) in cur_aliases:
                    warnings.warn(f"Dataverse '{url}' has a duplicate alias, " "removing...")
                    changed = True
                else:
                    new_dvns[url] = entry
                    if "alias" in entry:
                        cur_aliases.add(entry["alias"])
            self.dvns = new_dvns
            if self.cur_dvn not in self.dvns:
                warnings.warn("Current Dataverse is not available, switching to first available.")
                self.cur_dvn = list(self.dvns)[0]
                changed = True
        except ValueError as exc:
            print(exc)
            self.reset()
            changed = True
        if changed:
            self.save()

    def reset(self):
        """Reset the configuration file to its defaults."""
        self.dvns = {DEMO_DVN: {"alias": "demo"}}
        self.cur_dvn = DEMO_DVN
        print(self.dvns)
        self.save()

    def save(self):
        """Save the configuration back to the configuration file."""
        Path(self.config_path).parent.mkdir(exist_ok=True, parents=True)
        with open(self.config_path, "w", encoding="utf-8") as handle:
            json.dump({"cur_dvn": self.cur_dvn, "dvns": self.dvns}, handle, indent=4)

    def get_entry(self, url_or_alias: Union[str, None] = None) -> tuple[str, dict]:
        """Get the url and contents that belongs to a url or alias.

        Parameters
        ----------
        url_or_alias, optional
            Either an url or an alias, by default None in which
            case the currently selected dataverse setting is chosen.

        Returns
        -------
        url:
            The url to the dataverse server, e.g. https://demo.dataverse.org.
        entry:
            Entry for the dataverse server, its alias and API token.

        Raises
        ------
        KeyError
            If the entry can't be found.

        """
        url_or_alias = self.cur_dvn if url_or_alias is None else url_or_alias
        for url, entry in self.dvns.items():
            if url == str(url_or_alias):
                return url, entry

        for url, entry in self.dvns.items():
            if entry.get("alias", None) == str(url_or_alias):
                return url, entry

        raise KeyError(f"Cannot find entry with name/path '{url_or_alias}'")

    def set_dvn(self, url_or_alias: Union[str, Path, None] = None):
        """Change the currently selected dataverse setting.

        Parameters
        ----------
        url_or_alias, optional
            Either an url or an alias, by default None
            in which case the default dataverse will be chosen.

        """
        # Qt sends the url twice, once with value, once empty.
        if url_or_alias == "":
            return
        url_or_alias = DEMO_DVN if url_or_alias is None else url_or_alias
        try:
            url, _ = self.get_entry(url_or_alias)
        except KeyError as exc:
            url = url_or_alias
            self.dvns[url] = {}
            if not self.is_valid_url(url):
                if self.parser:
                    raise self.parser.error(f"Dataverse {url} is not a valid url.")  # pylint:disable=raise-missing-from
                raise TypeError(f"Dataverse {url} is not a valid url.") from exc
        if self.cur_dvn != url:
            self.cur_dvn = url
        self.save()

    def set_alias(self, alias: str, url: str):
        """Set an alias for a Dataverse URL.

        Parameters
        ----------
        alias
            Alias to be created.
        url
            Url to the Dataverse instance.

        """
        try:
            # Alias already exists change the path
            self.get_entry(alias)
            if self.parser:
                self.parser.error(
                    f"Alias '{alias}' already exists. To rename, delete the alias first."
                )
            raise ValueError(f"Alias '{alias}' already exists. To rename, delete the alias first.")
        except KeyError:
            try:
                # Path already exists change the alias
                url, entry = self.get_entry(url)
                if entry.get("alias", None) == alias:
                    return
                entry["alias"] = alias
                print("Change alias for URL")
            except KeyError:
                # Neither exists, create a new entry
                self.dvns[url] = {"alias": alias}
                print(f"Created alias '{alias}'")
        self.save()

    def delete_alias(self, alias):
        """Delete the alias and the entry."""
        try:
            url, entry = self.get_entry(alias)
        except KeyError as exc:
            if self.parser:
                self.parser.error(f"Cannot delete alias '{alias}'; does not exist.")
            raise KeyError(f"Cannot delete alias '{alias}'; does not exist.") from exc

        if url == DEMO_DVN:
            try:
                entry.pop("alias")
            except KeyError as exc:
                if self.parser:
                    self.parser.error("Cannot remove default Dataverse from configuration.")
                raise KeyError("Cannot remove default Dataverse from configuration.") from exc
        else:
            self.dvns.pop(url)
        self.save()

    def is_valid_url(self, url):
        """Check Url format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False


def show_available(dvn_conf):
    """Print available Dataverse configurations and highlight active one."""
    for url, entry in dvn_conf.dvns.items():
        prefix = " "
        if dvn_conf.cur_dvn in (entry.get("alias", None), url):
            prefix = "*"
        cur_alias = entry.get("alias", "[no alias]")
        print(f"{prefix} {cur_alias} -> {url}")
