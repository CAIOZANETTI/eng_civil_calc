"""Minimal stub of the pandas package used for tests."""
from __future__ import annotations
import csv
from pathlib import Path

class _ILoc:
    def __init__(self, column):
        self._col = column

    def __getitem__(self, idx):
        return self._col[idx]

class Column(list):
    @property
    def values(self):
        return self

    @property
    def iloc(self):
        return _ILoc(self)

    def __eq__(self, other):
        return Column([x == other for x in self])

    def __mul__(self, other):
        return Column([x * other for x in self])

    def __add__(self, other):
        if isinstance(other, Column):
            return Column([x + y for x, y in zip(self, other)])
        return Column([x + other for x in self])

class _Loc:
    def __init__(self, df):
        self._df = df

    def __getitem__(self, mask: Column):
        filtered = [row for row, cond in zip(self._df._rows, mask) if cond]
        return DataFrame(filtered)


class DataFrame:
    def __init__(self, rows):
        self._rows = list(rows)
        self.columns = list(self._rows[0].keys()) if self._rows else []

    def __getitem__(self, key):
        return Column([row.get(key) for row in self._rows])

    def __setitem__(self, key, values):
        if not isinstance(values, list) and not isinstance(values, Column):
            values = [values] * len(self._rows)
        for row, val in zip(self._rows, values):
            row[key] = val
        if key not in self.columns:
            self.columns.append(key)

    @property
    def loc(self):
        return _Loc(self)

    @property
    def empty(self):
        return len(self._rows) == 0

    def to_excel(self, path, index=False):
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.columns)
            writer.writeheader()
            for row in self._rows:
                writer.writerow(row)

    def __repr__(self):
        return f"DataFrame({self._rows})"


def read_csv(path: str | Path) -> DataFrame:
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            cleaned = {}
            for k, v in row.items():
                try:
                    cleaned[k] = float(v)
                except ValueError:
                    cleaned[k] = v
            rows.append(cleaned)
    return DataFrame(rows)
