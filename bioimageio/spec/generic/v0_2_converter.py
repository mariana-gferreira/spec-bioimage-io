import collections.abc
from typing import Any, Dict, Mapping, Union

from bioimageio.spec._internal.types import BioimageioYamlContent


def convert_from_older_format(data: BioimageioYamlContent) -> None:
    """convert raw RDF data of an older format where possible"""
    # check if we have future format version
    fv = data.get("format_version", "0.2.0")
    if isinstance(fv, str) and tuple(map(int, fv.split(".")[:2])) > (0, 2):
        return

    # we unofficially accept strings as author entries
    authors = data.get("authors")
    if isinstance(authors, list):
        data["authors"] = [{"name": a} if isinstance(a, str) else a for a in authors]

    if data.get("format_version") in ("0.2.0", "0.2.1"):
        data["format_version"] = "0.2.2"

    if data.get("format_version") == "0.2.2":
        remove_slashes_from_names(data)
        data["format_version"] = "0.2.3"

    remove_doi_prefix(data)


def remove_slashes_from_names(data: Dict[Any, Any]) -> None:
    NAME = "name"
    if NAME in data and isinstance(data[NAME], str):
        data[NAME] = data[NAME].replace("/", "").replace("\\", "")

    # update authors and maintainers
    def rm_slashes_in_person_name(person: Union[Any, Mapping[Union[Any, str], Any]]) -> Any:
        if not isinstance(person, collections.abc.Mapping):
            return person

        new_person = dict(person)
        if isinstance(n := person.get(NAME), str):
            new_person[NAME] = n.replace("/", "").replace("\\", "")

        return new_person

    for group in ("authors", "maintainers"):
        persons = data.get(group)
        if isinstance(persons, collections.abc.Sequence):
            data[group] = [rm_slashes_in_person_name(p) for p in persons]  # type: ignore


DOI_PREFIXES = ("https://doi.org/", "http://dx.doi.org/")


def remove_doi_prefix(data: BioimageioYamlContent) -> None:
    """we unofficially accept DOIs starting with "https://doi.org/" here we remove this prefix"""
    cite = data.get("cite")
    if isinstance(cite, collections.abc.Sequence):
        new_cite = list(cite)
        for i in range(len(new_cite)):
            cite_entry = new_cite[i]
            if not isinstance(cite_entry, collections.abc.Mapping):
                continue

            doi = cite_entry.get("doi")
            if not isinstance(doi, str):
                continue

            for doi_prefix in DOI_PREFIXES:
                if doi.startswith(doi_prefix):
                    doi = doi[len(doi_prefix) :]
                    break
            else:
                continue

            new_cite_entry = dict(cite_entry)
            new_cite_entry["doi"] = doi
            new_cite[i] = new_cite_entry

        data["cite"] = new_cite
