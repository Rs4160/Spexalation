import json
from pathlib import Path

from services.spec_discovery import (
    get_spec_versions,
    decode_3gpp_version,
)


DATABASE_FILE = Path("data/spec_database.json")


def load_database():
    """
    Load Spexalation's local specification database.
    """

    if not DATABASE_FILE.exists():
        return {}

    with open(DATABASE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_database(database):
    """
    Save Spexalation's local specification database.
    """

    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(DATABASE_FILE, "w", encoding="utf-8") as file:
        json.dump(database, file, indent=4)


def get_remote_latest_version(spec_number):
    """
    Check 3GPP and determine the newest available
    version for a specification.
    """

    versions = get_spec_versions(spec_number)

    if not versions:
        return None

    latest_file = versions[-1]
    latest_version = decode_3gpp_version(latest_file)

    return {
        "spec": spec_number,
        "version": latest_version,
        "filename": latest_file,
    }


def check_spec_update(spec_number):
    """
    Compare the latest 3GPP version with our local database.
    """

    database = load_database()

    remote = get_remote_latest_version(spec_number)

    if remote is None:
        return {
            "status": "error",
            "message": "Could not determine remote version.",
        }

    local = database.get(spec_number)

    if local is None:
        return {
            "status": "missing",
            "remote": remote,
        }

    if local.get("version") == remote["version"]:
        return {
            "status": "current",
            "local": local,
            "remote": remote,
        }

    return {
        "status": "update_available",
        "local": local,
        "remote": remote,
    }
def register_spec(spec_number, version, filename, path):
    """
    Record a downloaded specification in the local database.
    """

    database = load_database()

    database[spec_number] = {
        "version": version,
        "filename": filename,
        "path": str(path),
    }

    save_database(database)