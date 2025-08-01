"""Fetch information and build Dataverse dataset metadata."""

import json
import re

DATAVERSE_SUBJECTS = [
    "Agricultural Sciences",
    "Arts and Humanities",
    "Astronomy and Astrophysics",
    "Business and Management",
    "Chemistry",
    "Computer and Information Science",
    "Earth and Environmental Sciences",
    "Engineering",
    "Law",
    "Mathematical Sciences",
    "Medicine, Health and Life Sciences",
    "Physics",
    "Social Sciences",
    "Other",
]


# CLI functions
def get_non_empty_input(prompt):
    """Prompt to screen and check if answer is not empty."""
    while True:
        value = input(prompt).strip()
        if value:
            return value


def collect_authors():
    """Collect authors."""
    authors = []
    while True:
        print("\nEnter author details:")
        # Validate name
        while True:
            name = input("  Contact name (Last, First): ").strip()
            if is_valid_name(name):
                break
            print("  ❌ Invalid format. Use 'Last, First'.")
        affiliation = get_non_empty_input("  Author affiliation: ")
        authors.append(
            {
                "authorName": {
                    "value": name,
                    "typeClass": "primitive",
                    "multiple": False,
                    "typeName": "authorName",
                },
                "authorAffiliation": {
                    "value": affiliation,
                    "typeClass": "primitive",
                    "multiple": False,
                    "typeName": "authorAffiliation",
                },
            }
        )
        more = input("  Add another author? (y/n): ").strip().lower()
        if more != "y":
            break
    return authors


def collect_contacts():
    """Collect dataset contacts."""
    contacts = []
    while True:
        print("\nEnter dataset contact details:")
        # Validate name
        while True:
            name = input("  Contact name (Last, First): ").strip()
            if is_valid_name(name):
                break
            print("  ❌ Invalid format. Use 'Last, First'.")

        # Validate email
        while True:
            email = input("  Contact email: ").strip()
            if is_valid_email(email):
                break
            print("  ❌ Invalid email format. Try again.")

        contacts.append(
            {
                "datasetContactName": {
                    "value": name,
                    "typeClass": "primitive",
                    "multiple": False,
                    "typeName": "datasetContactName",
                },
                "datasetContactEmail": {
                    "value": email,
                    "typeClass": "primitive",
                    "multiple": False,
                    "typeName": "datasetContactEmail",
                },
            }
        )
        more = input("  Add another contact? (y/n): ").strip().lower()
        if more != "y":
            break
    return contacts


def collect_descriptions():
    """Collect descriptions."""
    descriptions = []
    while True:
        print("\nEnter dataset description:")
        desc = get_non_empty_input("  Description: ")
        descriptions.append(
            {
                "dsDescriptionValue": {
                    "value": desc,
                    "multiple": False,
                    "typeClass": "primitive",
                    "typeName": "dsDescriptionValue",
                }
            }
        )
        more = input("  Add another description? (y/n): ").strip().lower()
        if more != "y":
            break
    return descriptions


def collect_subjects():
    """Collect subjects."""
    subjects = []
    print("\nEnter subject(s). Type '?' to list valid subjects.")
    while True:
        subject = input("  Subject: ").strip()
        if subject == "?":
            print("  Valid Dataverse subjects:")
            for s in DATAVERSE_SUBJECTS:
                print(f"    - {s}")
            continue
        if subject in DATAVERSE_SUBJECTS:
            if subject not in subjects:
                subjects.append(subject)
            else:
                print("  Already added.")
        else:
            print("  ❌ Invalid subject. Type '?' to see the list of valid subjects.")
        more = input("  Add another subject? (y/n): ").strip().lower()
        if more != "y":
            break
    return subjects


def gather_metadata_inputs():
    """Gather metadata inputs."""
    print("=== Dataset Metadata Entry Tool ===\n")

    inputs = {
        "title": get_non_empty_input("Enter dataset title: "),
        "authors": collect_authors(),
        "contacts": collect_contacts(),
        "descriptions": collect_descriptions(),
        "subjects": collect_subjects(),
    }
    return inputs


# General functions
def is_valid_email(email):
    """Check if email is valid using regex."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)


def is_valid_name(name):
    """Check if name is in 'Last, First' format."""
    parts = [p.strip() for p in name.split(",")]
    return len(parts) == 2 and all(parts)


def build_metadata(inputs):
    """Build metadata dictionary from collected inputs."""
    meta = {
        "datasetVersion": {
            "metadataBlocks": {
                "citation": {
                    "displayName": "Citation Metadata",
                    "fields": [
                        {
                            "typeName": "title",
                            "typeClass": "primitive",
                            "multiple": False,
                            "value": inputs["title"],
                        },
                        {
                            "typeName": "author",
                            "typeClass": "compound",
                            "multiple": True,
                            "value": inputs["authors"],
                        },
                        {
                            "typeName": "datasetContact",
                            "typeClass": "compound",
                            "multiple": True,
                            "value": inputs["contacts"],
                        },
                        {
                            "typeName": "dsDescription",
                            "typeClass": "compound",
                            "multiple": True,
                            "value": inputs["descriptions"],
                        },
                        {
                            "typeName": "subject",
                            "typeClass": "controlledVocabulary",
                            "multiple": True,
                            "value": inputs["subjects"],
                        },
                    ],
                }
            }
        }
    }

    json_string = json.dumps(meta, indent=2)
    return json_string
