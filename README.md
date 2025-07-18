# maplink

Simple python utility for creating symbolic links. 

## Use

```
usage: maplink [-h] [--create] [--clobber] [--match-underscore] [--match-period] [--match-hyphen] source_template target_template

Create symlinks based on a match string and output format.

positional arguments:
  source_template     The pattern to match file paths, e.g., "/path/{group1:[A-Za-z0-9-]}_{group2}_{read}_L11.gz".
  target_template     The format for the output symlink paths. e.g. "/path/{group1}_{group2}_{read}_L11.gz".

options:
  -h, --help          show this help message and exit
  --create            Create directories and symlinks instead of just printing the message.
  --clobber           Clobber existing symlinks.
  --match-underscore  Match underscores (_) by default (in addition to alphanumerics).
  --match-period      Match periods (.) by default (in addition to alphanumerics).
  --match-hyphen      Match hyphens (-) by default (in addition to alphanumerics).

```

Notes:

- Any directories specified in the target template are automatically created.
- Links are **not** created by default, use `--create`. 
- Use `--clobber` to overwrite existing links; this will not clobber _files_ only _links_.

## Examples

We have a set of `fastq` files we wish to arrange by sample ID, and reformat the filename for consistency with expectations
of some tool. 

```
ls tests/fixtures
```
> S1_R1_001.fastq.gz 

> S1_R2_001.fastq.gz 

> S2_R1_001.fastq.gz 

> S2_R2_001.fastq.gz

```
maplink tests/fixtures/{sample}_{read}_{lane}.fastq.gz links/{sample}/{sample}_R{read}_L{lane}.fastq.gz --create
```

> Created symlink: tests/fixtures/S2_R2_001.fastq.gz -> links/S2/S2_RR2_L001.fastq.gz

> Created symlink: tests/fixtures/S1_R1_001.fastq.gz -> links/S1/S1_RR1_L001.fastq.gz

> Created symlink: tests/fixtures/S1_R2_001.fastq.gz -> links/S1/S1_RR2_L001.fastq.gz

> Created symlink: tests/fixtures/S2_R1_001.fastq.gz -> links/S2/S2_RR1_L001.fastq.gz

## Handling matching groups

By default, the regex used to match a group is **alphanumeric**. However, the format allows you to pass a custom regex;
Let's assume the sample ID contains a hyphen in some cases.

```
ls tests/fixtures
```
> S1_R1_001.fastq.gz
 
> S1_R2_001.fastq.gz 
 
> S2_R1_001.fastq.gz
 
> S2_R2_001.fastq.gz

> S2-A_R1_001.fastq.gz
 
> S2-A_R2_001.fastq.gz

```
maplink "tests/fixtures/{sample:[A-Za-z0-9-]+}_{read}_{lane}.fastq.gz" links/{sample}/{sample}_R{read}_L{lane}.fastq.gz
```

> Would link: tests/fixtures/S2-A_R1_001.fastq.gz -> links/S2-A/S2-A_RR1_L001.fastq.gz

> Would link: tests/fixtures/S2_R2_001.fastq.gz -> links/S2/S2_RR2_L001.fastq.gz

> Would link: tests/fixtures/S1_R1_001.fastq.gz -> links/S1/S1_RR1_L001.fastq.gz

> Would link: tests/fixtures/S1_R2_001.fastq.gz -> links/S1/S1_RR2_L001.fastq.gz

> Would link: tests/fixtures/S2-A_R2_001.fastq.gz -> links/S2-A/S2-A_RR2_L001.fastq.gz

> Would link: tests/fixtures/S2_R1_001.fastq.gz -> links/S2/S2_RR1_L001.fastq.gz

Important: 
  - if the target template is not put in quotes, your shell may attempt to expand the text resulting in a shell error
  - `maplink` does not support the use of `{}` within the regex currently.

Alternatively, use the `--match-hyphen` flag, for more convenience but less control (applies to all groups)

## installation

`maplink` is available at Pypi; and can be installed using `pip` or `pipx`. It is lightweight with only standard library
dependencies. 

```bash
python3 -m pipx install maplink
```

However, if you have `uv` installed; it is recommended to run directly using `uvx`:

```bash
uvx maplink source target
```