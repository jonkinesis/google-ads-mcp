from app.removals import enrich_removal_result, extract_remove_resource_names


def test_extract_remove_resource_names():
    ops = [{"remove": "customers/1/campaigns/2"}, {"update": {"resource_name": "x"}}]
    assert extract_remove_resource_names(ops) == ["customers/1/campaigns/2"]


def test_enrich_removal_result_adds_before_and_after():
    base = {"success": True, "dry_run": False}
    enriched = enrich_removal_result(
        base,
        customer_id="1234567890",
        resource_names=["customers/1234567890/campaigns/1"],
        dry_run=False,
    )
    assert "before_execution" in enriched
    assert "after_execution" in enriched
    assert enriched["before_execution"]["removals"][0]["customer_id"] == "1234567890"
