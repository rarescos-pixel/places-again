from scripts.run_evaluation import run_evaluation


def test_labeled_evaluation_corpus_meets_acceptance_targets():
    report = run_evaluation()
    assert report["case_count"] >= 40
    assert report["failed"] == 0
    assert report["acceptance_targets"] == {
        "unsafe_commits": 0,
        "unresolved_auto_commits": 0,
        "duplicate_side_effects": 0,
        "stale_plan_rejection_rate": 100.0,
        "accepted_plans_passing_verification_rate": 100.0,
    }
