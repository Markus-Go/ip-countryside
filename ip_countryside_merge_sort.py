from ast import keyword
import heapq
import os
from contextlib import contextmanager
from tempfile import TemporaryDirectory, mktemp
from typing import IO, Callable, List


def large_sort(input_file: IO, output_file: IO, key: Callable=None, reverse: bool=False, limit_chars: int=1024*1024*64):
    with TemporaryDirectory() as tmp_dir:
        for lines in _read_parts(input_file, limit_chars):
            lines = sorted(lines, key=key, reverse=reverse)
            _write_part(lines, tmp_dir)
        with _open_tmp_files(tmp_dir) as tmp_files:
            for row in heapq.merge(*tmp_files, key=key, reverse=False):
                output_file.write(row)


def _read_parts(input_file, limit_chars):
    lines = input_file.readlines(limit_chars)
    while lines:
        yield lines
        lines = input_file.readlines(limit_chars)


def _write_part(lines, tmp_dir):
    tmp_filename = mktemp(dir=tmp_dir)
    with open(tmp_filename, "w", encoding='utf-8', errors='ignore') as tmp_file:
        tmp_file.writelines(lines)
    return tmp_filename


@contextmanager
def _open_tmp_files(tmp_dir):
    filenames = os.listdir(tmp_dir)
    files = [open(os.path.join(tmp_dir, filename), "r", encoding='utf-8', errors='ignore') for filename in filenames]
    try:
        yield files
    finally:
        for file in files:
            file.close()