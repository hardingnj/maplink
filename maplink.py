import os
import re
import glob
import argparse
from typing import Iterable


def compile_regex_from_source(source_string_) -> re.Pattern:

    pattern = re.sub(r'\{(\w+):([^\}]+)\}', r'(?P<\1>\2)', source_string_)

    # Replace all {group} with the default regex pattern
    pattern = re.sub(r'\{(\w+)\}', r'(?P<\1>[A-Za-z0-9]+)', pattern)

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
            f'Invalid pattern in: {filepath}. '
            f'This can happen when a globbed character is not permitted by the specified regex; most likely [_.].'
            f'For example if a file is named /path/to_my_file,txt and the source pattern is /path/'
            f'See the documentation for more information. '
        )


def validate_targets(filepaths: Iterable[str], target_string: str, regex: re.Pattern) -> None:

    targets = dict()

    for filepath in filepaths:
        target_ = apply_regex(filepath, target_string, regex)
        if target_ in targets:
            raise RuntimeError(f"Duplicate target ({target_}) found. From {targets[target_]} and {filepath}. "
                               f"Other duplicate targets may exist: error thrown on first duplicate target ")

    return


def cli(source_string, target_string, create, skipvalidation, clobber):
    """Create symlinks based on MATCH_STRING and OUTPUT format."""

    # first transform source_string into a regex
    compiled_pattern = compile_regex_from_source(source_string)

    # then logic to translate the source string into a glob
    glob_pattern = create_glob_from_source(source_string)

    # then loop through the matched filepaths and apply logic to create new target for each, using the regex.
    # this step is skippable
    # internal: apply_regex
    # func(filepaths (iterator), compiled_regex). Validates the targets are unique. -> None

    # loop through matched filepaths again, compute source/target for each
    # each interation has a source and target
    # func(source, target, create=False, absolute=False, clobber=False) -> True


    # Define the regex pattern based on the match_string
    # Replace all {group:regex} with (?P<group>regex)
    validate_targets(glob.glob(glob_pattern), target_string, compiled_pattern)

    for source_path in glob.glob(glob_pattern):
        # Match the filepath against the regex
        target_ = apply_regex(source_path, target_string, compiled_pattern)

        if create:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(target_), exist_ok=True)

            # Create the symlink
            if clobber and os.path.islink(target_):
                os.unlink(target_)

            os.symlink(source_path, target_)

            print(f'Created symlink: {source_path} -> {target_}')
        else:
            print(f'Would link: {source_path} -> {target_}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create symlinks based on a match string and output format.')
    parser.add_argument('match_string', help='The pattern to match file paths, e.g., "/path/{group1:[A-Za-z0-9-]}_{group2}_{read}_L11.gz".')
    parser.add_argument('output', help='The format for the output symlink paths.')
    parser.add_argument('--create', action='store_true', help='Create directories and symlinks instead of just printing the message.')
    parser.add_argument('--skipvalidation', action='store_true', help='Skip validation that output symlinks are unique.', default=False)
    parser.add_argument('--clobber', action='store_true', help='Clobber existing symlinks.', default=False)
    args = parser.parse_args()

    cli(args.match_string, args.output, args.create, args.skipvalidation, args.clobber)
