from juniper_router.data.generate import build_records
from juniper_router.data.validate import validate_records


def test_seed_data_is_valid_and_reproducible():
    first = build_records()
    second = build_records()
    assert first == second
    result = validate_records(first)
    assert result["valid"], result["errors"]
    assert result["records"] >= 40
