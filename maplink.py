import os
import re
import glob
import argparse
from typing import Iterable

DEFAULT_REGEX = "A-Za-z0-9"



def compile_regex_from_source(source_string_) -> re.Pattern:

    # TODO: fix nested brackets

    # Replace patterns with specified regex
    pattern = re.sub(r'\{(\w+):([^\}]+)\}', r'(?P<\1>\2)', source_string_)

    # Replace all {group} with the default regex pattern
    pattern = re.sub(r'\{(\w+)\}', rf'(?P<\1>[{DEFAULT_REGEX}]+)', pattern)

    if ("{" in pattern) or ("}" in pattern):
        raise ValueError("Regex {n} are not supported currently")

    # Compile the regex
    return re.compile(pattern)

def create_glob_from_source(source_string_) -> str:
    glob_pattern = re.sub(r'\{(\w+):([^\}]+)\}', r'*', source_string_)  # Replace group placeholders with wildcards
    glob_pattern = re.sub(r'\{(\w+)\}', r'*', glob_pattern)  # Replace default group placeholders with wildcards
    return glob_pattern

def apply_regex(filepath: str, target_pattern: str, regex: re.Pattern) -> str:

    match = regex.match(filepath)

    if match:
        # Extract groups
        groups = match.groupdict()

        # Create the output path using the extracted groups
        target_path = target_pattern.format(**groups)

        return target_path

    else:
        # TODO: better information on why this can happen.
        raise ValueError(
            f'Invalid pattern in: {filepath} given pattern: {regex}.'
            f'This can happen when a globbed string is not matched by the specified regex; most likely [_.]. '
            'For example if a file is named /path/to_my_file,txt and the source pattern is /path/{name}.txt '
            f'Recall that the default regex is [A-Za-z0-9]+ and does not include any special characters. '
            f'See the documentation for more information. '
        )


def determine_and_validate_targets(filepaths: Iterable[str], target_string: str, regex: re.Pattern) -> dict[str, str]:

    targets = dict()

    for filepath in filepaths:
        target_ = apply_regex(filepath, target_string, regex)
        if target_ in targets:
            raise RuntimeError(f"Duplicate target ({target_}) found. From {targets[target_]} and {filepath}. "
                               f"Other duplicate targets may exist: error thrown on first duplicate target ")

    return targets


def cli(source_string, target_string, create, skipvalidation, clobber):
    """Create symlinks based on MATCH_STRING and OUTPUT format."""

    # first transform source_string into a regex
    compiled_pattern = compile_regex_from_source(source_string)

    # then logic to translate the source string into a glob
    glob_pattern = create_glob_from_source(source_string)

    # Create the actual file: link mapping
    target_dict = determine_and_validate_targets(
        glob.glob(glob_pattern),
        target_string,
        compiled_pattern
    )

    for source_path, target_path in target_dict.items():

        if create:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            if clobber and os.path.islink(target_path):
                os.unlink(target_path)

            os.symlink(source_path, target_path)

            print(f'Created symlink: {source_path} -> {target_path}')
        else:
            print(f'Would link: {source_path} -> {target_path}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create symlinks based on a match string and output format.')
    parser.add_argument('match_string', help='The pattern to match file paths, e.g., "/path/{group1:[A-Za-z0-9-]}_{group2}_{read}_L11.gz".')
    parser.add_argument('output', help='The format for the output symlink paths.')
    parser.add_argument('--create', action='store_true', help='Create directories and symlinks instead of just printing the message.')
    parser.add_argument('--skipvalidation', action='store_true', help='Skip validation that output symlinks are unique.', default=False)
    parser.add_argument('--clobber', action='store_true', help='Clobber existing symlinks.', default=False)
    args = parser.parse_args()

    cli(args.match_string, args.output, args.create, args.skipvalidation, args.clobber)
