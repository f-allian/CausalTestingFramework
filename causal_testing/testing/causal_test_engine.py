import pandas as pd

from causal_testing.testing.causal_test_case import CausalTestCase, CausalTestResult
from causal_testing.specification.causal_specification import CausalSpecification


class CausalTestEngine:

    def __init__(self, causal_test_case: CausalTestCase, causal_specification: CausalSpecification,
                 observational_data: pd.DataFrame = None):
        self.causal_test_case = causal_test_case
        self.casual_dag, self.scenario = causal_specification.causal_dag, causal_specification.scenario
        if observational_data:
            self.observational_df = observational_data

    def execute_test(self):
        """
        Execute the causal test
        :return: A CausalTestResult if data is sufficient, otherwise inform user of missing data.
        """
        causal_estimand = self._compute_causal_estimand()
        if not self._data_is_sufficient(causal_estimand):
            data_to_collect = self._compute_data_to_collect(causal_estimand)
            # TODO: Replace with custom exception
            raise Exception(f'Data is insufficient for estimating the estimand. User should collect {data_to_collect}.')
        causal_estimate = self._compute_causal_estimate(causal_estimand)
        confidence_intervals = self._compute_confidence_intervals(confidence_level=.05)
        return CausalTestResult(causal_estimand, causal_estimate, confidence_intervals, confidence_level=.05)

    def _data_is_sufficient(self, causal_estimand):
        """
        If using observational data, check whether the data contains necessary data to compute the casual estimand.
        :return:
        :param causal_estimand: The causal estimand to be estimated.
        :return: True or False depending on whether the data is sufficient to compute the causal estimand.
        """
        pass

    def _compute_causal_estimand(self):
        """
        Compute the causal estimand for the current causal test case. This step checks the structure of the causal DAG
        and identifies any open back-door paths between the treatment and outcome variable. If any back-door paths
        exist, this method will attempt to find a set of variables which block (d-separate) these paths, yielding the
        causal estimand. If no variables can block the back-door path, an exception is raised to alert the user that
        it is not possible to compute this causal effect from observational data given the current causal assumptions
        and data.
        :return causal_estimand: The causal estimand to be estimated.
        """
        pass

    def _compute_data_to_collect(self, causal_estimand):
        """
        If the current data is insufficient to estimate the causal estimand, this method will compute the set of
        variables that are currently missing data and preventing estimation. This can be used to guide execution of
        the system-under-test.
        :param causal_estimand: The causal estimand to be estimated.
        :return data_to_collect: The data to be collected that would permit causal inference for this casual test case.
        """
        pass

    def _compute_causal_estimate(self, causal_estimand):
        """
        Given a causal estimand, compute the causal estimate from the available data.
        :param causal_estimand: The casual estimand to be estimated.
        :return causal_estimate: The causal estimate corresponding to the causal test case. That is, the causal effect
        of applying the intervention to the input configuration on the output(s) of interest.
        """
        pass

    def _compute_confidence_intervals(self, confidence_level):
        """
        Compute the confidence intervals at the specified confidence level for the causal estimate. This gives the user
        and indication of the precision/reliability of the causal estimate. If this is too low, it indicates that more
        data or better estimators are necessary.
        :param confidence_level: The specified confidence level at which to compute the confidence intervals e.g. .05
        corresponds to 95% confidence intervals.
        :return: confidence intervals of the form [lower, upper] at the specified confidence level.
        """
        pass
