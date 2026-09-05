from juniper_router.data.expanded import build_expanded_records
from juniper_router.data.generate import build_records
from juniper_router.data.validate import validate_records


def test_seed_data_is_valid_and_reproducible():
    first = build_records()
    second = build_records()
    assert first == second
    result = validate_records(first)
    assert result["valid"], result["errors"]
    assert result["records"] >= 40


def test_expanded_corpus_has_strict_split_and_class_coverage():
    rows = build_expanded_records()
    result = validate_records(rows, strict_duplicates=True)
    assert result["valid"], result["errors"][:5]
    assert result["records"] == 2100
    assert {row["split"] for row in rows} == {"train", "dev", "test"}
    assert len(result["decision_counts"]) == 12
