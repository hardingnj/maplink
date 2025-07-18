import os
import re
import glob
import argparse
from typing import Iterable
from pathlib import Path


DEFAULT_REGEX = "A-Za-z0-9"

def compile_regex_from_source(source_string_: str, match_underscore: bool = False, match_period: bool = False, match_hyphen: bool = False) -> re.Pattern:

    # TODO: fix nested brackets

    # Replace patterns with specified regex
    pattern = re.sub(r'\{(\w+):([^\}]+)\}', r'(?P<\1>\2)', source_string_)

    char_set = DEFAULT_REGEX
    if match_underscore:
        char_set += "_"
    if match_period:
        char_set += "."
    if match_hyphen:
        char_set += "-"

    # Replace all {group} with the default regex pattern
    pattern = re.sub(r'\{(\w+)\}', rf'(?P<\1>[{char_set}]+)', pattern)

    print(pattern)
    if ("{" in pattern) or ("}" in pattern):
        raise ValueError("Regex {n} are not supported currently")

    # Compile the regex
    return re.compile(pattern)

def create_glob_from_source(source_string_) -> str:

    glob_pattern = re.sub(
        r"\{(\w+):([^\}]+)\}", r"*", source_string_
    )  # Replace group placeholders with wildcards
    glob_pattern = re.sub(
        r"\{(\w+)\}", r"*", glob_pattern
    )  # Replace default group placeholders with wildcards

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
        else:
            targets[filepath] = target_

    return targets

def create_symlink(source_path: Path, target_path: Path, clobber=False, absolute_path=True):

    source_path = Path(source_path)
    target_path = Path(target_path)

    target_dirname = os.path.dirname(target_path)
    if target_dirname:
        os.makedirs(target_dirname, exist_ok=True)

    if clobber and os.path.islink(target_path):
        os.unlink(target_path)

    if absolute_path:
        os.symlink(source_path.absolute(), target_path.absolute())
    else:
        raise NotImplementedError('Only absolute paths are supported currently')

    print(f'Created symlink: {source_path} -> {target_path}')

    return


def cli(source_template, target_template, create, clobber, match_underscore, match_period, match_hyphen):
    """Create symlinks based on MATCH_STRING and OUTPUT format."""

    # first transform source_string into a regex
    compiled_pattern = compile_regex_from_source(
        source_template, match_underscore, match_period, match_hyphen
    )

    # then logic to translate the source string into a glob
    glob_pattern = create_glob_from_source(source_template)

    # Create the actual file: link mapping
    target_dict = determine_and_validate_targets(
        glob.glob(glob_pattern),
        target_template,
        compiled_pattern
    )

    for source_path, target_path in target_dict.items():

        if create:
            create_symlink(source_path, target_path)
        else:
            print(f'Would link: {source_path} -> {target_path}')

def main():

    parser = argparse.ArgumentParser(description='Create symlinks based on a match string and output format.')
    parser.add_argument('source_template', help='The pattern to match file paths, e.g., "/path/{group1:[A-Za-z0-9-]}_{group2}_{read}_L11.gz".')
    parser.add_argument('target_template', help='The format for the output symlink paths. e.g. "/path/{group1}_{group2}_{read}_L11.gz".')
    parser.add_argument('--create', action='store_true', help='Create directories and symlinks instead of just printing the message.')
    parser.add_argument('--clobber', action='store_true', help='Clobber existing symlinks.', default=False)
    parser.add_argument('--match-underscore', action='store_true',
                        help='Match underscores (_) by default (in addition to alphanumerics).', default=False)
    parser.add_argument('--match-period', action='store_true',
                        help='Match periods (.) by default (in addition to alphanumerics).', default=False)
    parser.add_argument('--match-hyphen', action='store_true',
                        help='Match hyphens (-) by default (in addition to alphanumerics).', default=False
                        )
    args = parser.parse_args()

    cli(
        args.source_template,
        args.target_template,
        args.create,
        args.clobber,
        args.match_underscore,
        args.match_period,
        args.match_hyphen
    )
