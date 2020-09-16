from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.execution_engine import PandasExecutionEngine

from ...core.batch import Batch
from ...data_asset.util import parse_result_format
from ..expectation import (
    ColumnMapDatasetExpectation,
    Expectation,
    InvalidExpectationConfigurationError,
    _format_map_output,
)
from ..registry import extract_metrics, get_metric_kwargs


class ExpectColumnValuesToMatchRegex(ColumnMapDatasetExpectation):
    map_metric = "map.matches_regex"
    metric_dependencies = ("map.matches_regex.count", "map.nonnull.count")
    success_keys = ("regex", "mostly")

    default_kwarg_values = {
        "row_condition": None,
        "condition_parser": None,  # we expect this to be explicitly set whenever a row_condition is passed
        "mostly": 1,
        "result_format": "BASIC",
        "include_config": True,
        "catch_exceptions": False,
    }

    def validate_configuration(self, configuration: Optional[ExpectationConfiguration]):
        super().validate_configuration(configuration)
        if configuration is None:
            configuration = self.configuration
        try:
            assert "regex" in configuration.kwargs, "regex is required"
            assert isinstance(
                configuration.kwargs["regex"], str
            ), "regex must be a string"
        except AssertionError as e:
            raise InvalidExpectationConfigurationError(str(e))
        return True

    @PandasExecutionEngine.column_map_metric(
        metric_name="map.matches_regex",
        metric_domain_keys=ColumnMapDatasetExpectation.domain_keys,
        metric_value_keys=("regex",),
        metric_dependencies=tuple(),
    )
    def _pandas_map_matches_regex(
        self, series: pd.Series, regex: str, runtime_configuration: dict = None,
    ):
        return series.astype(str).str.contains(regex)

    @Expectation.validates(metric_dependencies=metric_dependencies)
    def _validates(
        self,
        configuration: ExpectationConfiguration,
        metrics: dict,
        runtime_configuration: dict = None,
    ):
        validation_dependencies = self.get_validation_dependencies(configuration)[
            "metrics"
        ]
        metric_vals = extract_metrics(validation_dependencies, metrics, configuration)
        mostly = configuration.get_success_kwargs().get(
            "mostly", self.default_kwarg_values.get("mostly")
        )
        if runtime_configuration:
            result_format = runtime_configuration.get(
                "result_format", self.default_kwarg_values.get("result_format")
            )
        else:
            result_format = self.default_kwarg_values.get("result_format")
        return _format_map_output(
            result_format=parse_result_format(result_format),
            success=(
                metric_vals.get("map.matches_regex.count")
                / metric_vals.get("map.nonnull.count")
            )
            >= mostly,
            element_count=metric_vals.get("map.count"),
            nonnull_count=metric_vals.get("map.nonnull.count"),
            unexpected_count=metric_vals.get("map.nonnull.count")
            - metric_vals.get("map.matches_regex.count"),
            unexpected_list=metric_vals.get("map.matches_regex.unexpected_values"),
            unexpected_index_list=metric_vals.get("map.matches_regex.unexpected_index"),
        )
