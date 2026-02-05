from __future__ import annotations

from typing import Sequence

from app.collectors.base import BaseCollector
from app.collectors.example_api import ExampleCollector


def get_enabled_collectors() -> Sequence[BaseCollector]:
    return [ExampleCollector()]
