import random

from dgf_feedback.api_manager import APIManager
from dgf_feedback.prompt_mutator import PromptMutator
from dgf_feedback.sample_filter import SampleFilter


def test_sample_filter_thresholds():
    sample_filter = SampleFilter(min_api_coverage=0.5, min_success_ratio=0.5)
    mutated = ["a", "b", "c", "d"]
    coverage = {"a": 0.6, "b": 0.1, "c": 0.8, "d": 0.2}
    assert sample_filter.filter_sample(mutated, coverage) is True


def test_sample_filter_rejects_when_coverage_too_low():
    sample_filter = SampleFilter(min_api_coverage=0.6, min_success_ratio=0.75)
    mutated = ["a", "b", "c", "d"]
    coverage = {"a": 0.61, "b": 0.20, "c": 0.55, "d": 0.59}
    assert sample_filter.filter_sample(mutated, coverage) is False


def test_sample_filter_fallback_to_overall_coverage():
    sample_filter = SampleFilter(min_overall_coverage=0.2)
    mutated = ["a", "b"]
    assert sample_filter.filter_sample(mutated, {}, overall_coverage=0.1) is False
    assert sample_filter.filter_sample(mutated, {}, overall_coverage=0.25) is True
    assert sample_filter.filter_sample([], {}, overall_coverage=0.9) is False


def test_api_manager_energy_and_sampling():
    random.seed(0)
    manager = APIManager(["A", "B", "C"], exponent=1.0)
    manager.update_seed("A")
    manager.update_prompt("A")
    manager.update_coverage("A", 0.8)

    energy_a = manager.get_energy("A")
    energy_b = manager.get_energy("B")
    assert energy_b > energy_a

    selected = manager.sample_api_combination(2)
    assert 1 <= len(selected) <= 2
    assert set(selected).issubset({"A", "B", "C"})


def test_prompt_mutator_insert_replace_crossover():
    random.seed(0)
    manager = APIManager(["A", "B", "C", "D"])
    mutator = PromptMutator(manager)

    inserted = mutator.insert(["A"], num_insert=2)
    assert "A" in inserted
    assert len(set(inserted)) >= 1

    replaced = mutator.replace(["A", "B"], num_replace=1)
    assert len(replaced) >= 1
    assert set(replaced).issubset({"A", "B", "C", "D"})

    crossed = mutator.crossover(["A", "B"], ["B", "C"])
    assert set(crossed) == {"A", "B", "C"}
