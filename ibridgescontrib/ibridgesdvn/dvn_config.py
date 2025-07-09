"""Config functions."""

from pathlib import Path
import json
import argparse
import warnings
from urllib.parse import urlparse
from typing import Union

DVN_CONFIG_FP = Path.home() / ".dvn" / "dvn.json"
DEMO_DVN = "https://demo.dataverse.org"


class DVNConf:
    """Interface to the dataverse config file."""

    def __init__(self, parser: argparse.ArgumentParser,
                 config_path: Union[str, Path] = DVN_CONFIG_FP):
        """Read configuration file and validate it."""
        self.config_path = config_path
        self.parser = parser

        try:
            with open(self.config_path, "r", encoding="utf-8") as handle:
                dvn_conf = json.load(handle)
                self.dvns = dvn_conf["dvns"]
                self.cur_dvn = dvn_conf.get("cur_dvn", DEMO_DVN)
        except Exception as exc: # pylint: disable=W0718
            if isinstance(exc, FileNotFoundError):
                warnings.warn(
                    f"{self.config_path} not found. Use default {DVN_CONFIG_FP}."
                )
                self.reset(ask=False)
            else:
                print(repr(exc))
                warnings.warn(
                    f"{self.config_path} not found. Use default {DVN_CONFIG_FP}."
                )
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
                if url != DEMO_DVN and not self._is_valid_url(url):
                    warnings.warn(
                        f"Dataverse '{url}' is not a valid URL, " "removing the entry."
                    )
                    changed = True
                elif entry.get("alias", None) in cur_aliases:
                    warnings.warn(
                        f"Dataverse '{url}' has a duplicate alias, " "removing..."
                    )
                    changed = True
                else:
                    new_dvns[url] = entry
                    if "alias" in entry:
                        cur_aliases.add(entry["alias"])
            self.dvns = new_dvns
            if self.cur_dvn not in self.dvns:
                warnings.warn(
                    "Current Dataverse is not available, switching to first available."
                )
                self.cur_dvn = list(self.dvns)[0]
                changed = True
        except ValueError as exc:
            print(exc)
            self.reset()
            changed = True
        if changed:
            self.save()

    def reset(self, ask: bool = True):
        """Reset the configuration file to its defaults.

        Parameters
        ----------
        ask, optional
            Ask whether to overwrite the current configuration file, by default True

        """
        if ask:
            answer = input(
                f"The dataverse configuration file {self.config_path} cannot be read, "
                "reset? (Y/N)"
            )
            if answer != "Y":
                self.parser.error(
                    "Cannot continue without reading the dataverse configuration file."
                )
        self.dvns = {DEMO_DVN: {"alias": "demo"}}
        self.cur_dvn = DEMO_DVN
        self.save()

    def save(self):
        """Save the configuration back to the configuration file."""
        Path(self.config_path).parent.mkdir(exist_ok=True, parents=True)
        with open(self.config_path, "w", encoding="utf-8") as handle:
            json.dump(
                {"cur_dvn": self.cur_dvn,
                 "dvns": self.dvns},
                handle, indent=4)

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
        url_or_alias = DEMO_DVN if url_or_alias is None else url_or_alias
        try:
            url, _ = self.get_entry(url_or_alias)
        except KeyError as err:
            url = url_or_alias
            self.dvns[url] = {}
            if not self._is_valid_url(url):
                raise self.parser.error(f"Dataverse {url} is not a valid url.") # pylint:disable=raise-missing-from
        if self.cur_dvn != url:
            self.cur_dvn = url
        self.save()


    def set_alias(self, alias: str, url: str):
        """Set an alias for a Dataverse URL.

        Parameters
        ----------
        alias
            Alias to be created.
        ienv_path
            Path to the iRODS environment file for the new alias.

        """
        try:
            # Alias already exists change the path
            self.get_entry(alias)
            self.parser.error(f"Alias '{alias}' already exists. To rename, delete the alias first.")
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
        except KeyError:
            self.parser.error(f"Cannot delete alias '{alias}'; does not exist.")

        if url == DEMO_DVN:
            try:
                entry.pop("alias")
            except KeyError:
                self.parser.error("Cannot remove default irods path from configuration.")
        else:
            self.dvns.pop(url)
        self.save()


    def _is_valid_url(self, url):
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
    return
