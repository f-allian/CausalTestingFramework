"""
This module contains code to measure various aspects of causal test adequacy.
"""
from itertools import combinations
from copy import deepcopy
import pandas as pd

from causal_testing.testing.causal_test_suite import CausalTestSuite
from causal_testing.data_collection.data_collector import DataCollector
from causal_testing.specification.causal_specification import CausalSpecification
from causal_testing.testing.estimators import Estimator
from causal_testing.testing.causal_test_case import CausalTestCase


class DAGAdequacy:
    """
    Measures the adequacy of a given DAG by hos many edges and independences are tested.
    """

    def __init__(
        self,
        causal_specification: CausalSpecification,
        test_suite: CausalTestSuite,
    ):
        self.causal_dag = causal_specification.causal_dag
        self.test_suite = test_suite
        self.tested_pairs = None
        self.pairs_to_test = None
        self.untested_edges = None
        self.dag_adequacy = None

    def measure_adequacy(self):
        """
        Calculate the adequacy measurement, and populate the `dat_adequacy` field.
        """
        self.tested_pairs = {
            (t.base_test_case.treatment_variable, t.base_test_case.outcome_variable) for t in self.test_suite
        }
        self.pairs_to_test = set(combinations(self.causal_dag.graph.nodes, 2))
        self.untested_edges = self.pairs_to_test.difference(self.tested_pairs)
        self.dag_adequacy = len(self.tested_pairs) / len(self.pairs_to_test)

    def to_dict(self):
        "Returns the adequacy object as a dictionary."
        return {
            "causal_dag": self.causal_dag,
            "test_suite": self.test_suite,
            "tested_pairs": self.tested_pairs,
            "pairs_to_test": self.pairs_to_test,
            "untested_edges": self.untested_edges,
            "dag_adequacy": self.dag_adequacy,
        }


class DataAdequacy:
    """
    Measures the adequacy of a given test according to the Fisher kurtosis of the bootstrapped result.
    - Positive kurtoses indicate the model doesn't have enough data so is unstable.
    - Negative kurtoses indicate the model doesn't have enough data, but is too stable, indicating that the spread of
      inputs is insufficient.
    - Zero kurtosis is optimal.
    """

    def __init__(
        self, test_case: CausalTestCase, estimator: Estimator, data_collector: DataCollector, bootstrap_size: int = 100
    ):
        self.test_case = test_case
        self.estimator = estimator
        self.data_collector = data_collector
        self.kurtosis = None
        self.outcomes = None
        self.bootstrap_size = bootstrap_size

    def measure_adequacy(self):
        """
        Calculate the adequacy measurement, and populate the data_adequacy field.
        """
        results = []
        for i in range(self.bootstrap_size):
            estimator = deepcopy(self.estimator)
            estimator.df = estimator.df.sample(len(estimator.df), replace=True, random_state=i)
            # try:
            results.append(self.test_case.execute_test(estimator, self.data_collector))
            # except np.LinAlgError:
            # continue
        outcomes = [self.test_case.expected_causal_effect.apply(c) for c in results]
        results = pd.DataFrame(c.to_dict() for c in results)[["effect_estimate", "ci_low", "ci_high"]]

        def convert_to_df(field):
            converted = []
            for r in results[field]:
                if isinstance(r, float):
                    converted.append(
                        pd.DataFrame({self.test_case.base_test_case.treatment_variable.name: [r]}).transpose()
                    )
                else:
                    converted.append(r)
            return converted

        for field in ["effect_estimate", "ci_low", "ci_high"]:
            results[field] = convert_to_df(field)

        effect_estimate = pd.concat(results["effect_estimate"].tolist(), axis=1).transpose().reset_index(drop=True)
        self.kurtosis = effect_estimate.kurtosis()
        self.outcomes = sum(outcomes)

    def to_dict(self):
        "Returns the adequacy object as a dictionary."
        return {"kurtosis": self.kurtosis.to_dict(), "bootstrap_size": self.bootstrap_size, "passing": self.outcomes}
