import pytest
import os
from pathlib import Path

from maplink import create_symlink

def test_create_symlink_should_work_in_current_directory(tmp_path):

    file_a = tmp_path / 'a.txt'
    file_a.write_text('a')

    target_path = tmp_path / 'b.txt'

    create_symlink(source_path=file_a, target_path=target_path)

def test_create_symlink_should_clobber_existing_link_if_specified(tmp_path):

    file_a = tmp_path / 'a.txt'
    file_a.write_text('a')

    target_path = tmp_path / 'b.txt'

    create_symlink(source_path=file_a, target_path=target_path)
    create_symlink(source_path=file_a, target_path=target_path, clobber=True)

    with pytest.raises(FileExistsError):
        create_symlink(source_path=file_a, target_path=target_path)

def test_create_symlink_should_work_if_target_not_in_wd(tmp_path):

    os.chdir(tmp_path)
    os.makedirs('foo')
    file_a = Path('foo') / 'a.txt'
    file_a.write_text('a')

    target_path = Path('bar') / 'b.txt'

    create_symlink(source_path=file_a, target_path=target_path)

    assert target_path.resolve() == file_a.absolute()
