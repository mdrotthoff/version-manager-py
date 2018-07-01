from typing import Dict
import yaml
import sys
from os import path

from .matcher_builder import matcher_builder
from .matchers.pattern import TrackedVersionSet, TrackedVersion
from version_manager.styling import red


def read_settings_file(settings_file: str,
                       override_settings: Dict[str, str]) -> TrackedVersionSet:
    if not path.exists(settings_file):
        settings_file = path.join(path.dirname(settings_file), 'versions.yml')

        if not path.exists(settings_file):
            report_missing_settings_file(settings_file)
            sys.exit(1)

    with open(settings_file, 'r', encoding='utf-8') as stream:
        settings = list(yaml.safe_load_all(stream))[0]

    result = list()

    for name, tracked_entry in settings.items():
        try:
            tracked_version: TrackedVersion = TrackedVersion(name)
            tracked_version.version = override_settings[name] if \
                name in override_settings else \
                parse_version(tracked_entry['version'], override_settings)

            tracked_files = tracked_entry['files'] if 'files' in tracked_entry else {}

            for file_name in tracked_files.keys():
                tracked_file = matcher_builder(tracked_version,
                                               tracked_files[file_name])
                tracked_version.files[file_name] = tracked_file

            result.append(tracked_version)
        except Exception as e:
            raise Exception("Unable to read value: %s" % name, e)

    return result


def report_missing_settings_file(settings_file: str) -> None:
    print(red("%s configuration file is missing." % settings_file))


from .parse_version import parse_version
