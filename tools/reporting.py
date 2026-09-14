"""Reporting convenience tools (GAQL-backed)."""
from __future__ import annotations
from typing import Any
from tools._helpers import gaql_tool

def register(mcp) -> None:
    @mcp.tool(name="get_account_summary")
    def get_account_summary(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Account-level summary metrics."""
        q = """SELECT customer.id, customer.descriptive_name, customer.currency_code, customer.time_zone, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM customer"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="get_customer_details")
    def get_customer_details(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Customer account metadata."""
        q = """SELECT customer.id, customer.descriptive_name, customer.currency_code, customer.time_zone, customer.manager, customer.test_account, customer.optimization_score FROM customer"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="list_campaigns")
    def list_campaigns(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """List campaigns."""
        q = """SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type, campaign.start_date_time, campaign.end_date_time, customer.time_zone FROM campaign ORDER BY campaign.id"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_campaign")
    def get_campaign(campaign_id: int, customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Get one campaign by ID."""
        q = """SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type, campaign.start_date_time, campaign.end_date_time, campaign.campaign_budget, customer.time_zone FROM campaign WHERE campaign.id = {campaign_id}"""
        q = q.format(campaign_id=campaign_id)
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_campaign_performance")
    def get_campaign_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Campaign performance metrics."""
        q = """SELECT campaign.id, campaign.name, campaign.status, campaign.start_date_time, campaign.end_date_time, customer.time_zone, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.conversions_value FROM campaign"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="get_campaign_statuses")
    def get_campaign_statuses(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Campaign status counts."""
        q = """SELECT campaign.id, campaign.name, campaign.status, campaign.start_date_time, campaign.end_date_time, metrics.impressions FROM campaign"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="list_campaign_budgets")
    def list_campaign_budgets(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Campaign budgets."""
        q = """SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros, campaign_budget.status, campaign_budget.delivery_method FROM campaign_budget"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_budget_performance")
    def get_budget_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Budget-linked performance."""
        q = """SELECT campaign.id, campaign.name, campaign_budget.amount_micros, metrics.cost_micros, metrics.impressions, metrics.clicks FROM campaign"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="list_ad_groups")
    def list_ad_groups(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """List ad groups."""
        q = """SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type, campaign.id, campaign.name FROM ad_group ORDER BY ad_group.id"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_ad_group")
    def get_ad_group(ad_group_id: int, customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Get ad group by ID."""
        q = """SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type, ad_group.cpc_bid_micros, campaign.id FROM ad_group WHERE ad_group.id = {ad_group_id}"""
        q = q.format(ad_group_id=ad_group_id)
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_ad_group_performance")
    def get_ad_group_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Ad group performance."""
        q = """SELECT ad_group.id, ad_group.name, ad_group.status, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM ad_group"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="list_ads")
    def list_ads(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """List ads."""
        q = """SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.type, ad_group.id, campaign.id FROM ad_group_ad"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_ad")
    def get_ad(ad_group_id: int, ad_id: int, customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Get ad by ad group and ad ID."""
        q = """SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.type, ad_group_ad.ad.final_urls, ad_group.id FROM ad_group_ad WHERE ad_group.id = {ad_group_id} AND ad_group_ad.ad.id = {ad_id}"""
        q = q.format(ad_group_id=ad_group_id)
        q = q.format(ad_id=ad_id)
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_ad_performance")
    def get_ad_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Ad performance."""
        q = """SELECT ad_group_ad.ad.id, ad_group.id, ad_group_ad.status, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM ad_group_ad"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="list_keywords")
    def list_keywords(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """List keywords."""
        q = """SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, ad_group_criterion.status, ad_group.id, campaign.id FROM keyword_view"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_keyword_performance")
    def get_keyword_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Keyword performance."""
        q = """SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.status, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM keyword_view"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="get_keyword_quality_score")
    def get_keyword_quality_score(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Keyword quality score components."""
        q = """SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.quality_info.quality_score, ad_group_criterion.quality_info.creative_quality_score, ad_group_criterion.quality_info.post_click_quality_score, ad_group_criterion.quality_info.search_predicted_ctr FROM keyword_view"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="get_search_terms")
    def get_search_terms(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Search terms report."""
        q = """SELECT search_term_view.search_term, campaign.id, ad_group.id, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM search_term_view"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="get_search_term_performance")
    def get_search_term_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Search term performance."""
        q = """SELECT search_term_view.search_term, segments.search_term_match_type, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM search_term_view"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="get_geographic_performance")
    def get_geographic_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Geographic performance."""
        q = """SELECT geographic_view.country_criterion_id, geographic_view.location_type, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM geographic_view"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="get_device_performance")
    def get_device_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Device performance."""
        q = """SELECT segments.device, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM campaign"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="get_network_performance")
    def get_network_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Network performance."""
        q = """SELECT segments.ad_network_type, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM campaign"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="get_hourly_performance")
    def get_hourly_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Hour-of-day performance."""
        q = """SELECT segments.hour, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM campaign"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="get_day_of_week_performance")
    def get_day_of_week_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Day-of-week performance."""
        q = """SELECT segments.day_of_week, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM campaign"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="get_audience_performance")
    def get_audience_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Audience performance."""
        q = """SELECT campaign_audience_view.resource_name, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM campaign_audience_view"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="get_demographic_performance")
    def get_demographic_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Demographic performance by gender (age_range_view is a separate query; combined age+gender is not supported)."""
        q = """SELECT ad_group_criterion.gender.type, metrics.impressions, metrics.clicks, metrics.cost_micros FROM gender_view"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="list_assets")
    def list_assets(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """List assets."""
        q = """SELECT asset.id, asset.name, asset.type, asset.resource_name FROM asset"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_asset_performance")
    def get_asset_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Asset performance."""
        q = """SELECT asset.id, asset.name, asset.type, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM asset"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="list_campaign_assets")
    def list_campaign_assets(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Campaign assets."""
        q = """SELECT campaign_asset.asset, campaign_asset.field_type, campaign_asset.status, campaign.id FROM campaign_asset"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="list_ad_group_assets")
    def list_ad_group_assets(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Ad group assets."""
        q = """SELECT ad_group_asset.asset, ad_group_asset.field_type, ad_group_asset.status, ad_group.id FROM ad_group_asset"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="list_customer_assets")
    def list_customer_assets(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Customer assets."""
        q = """SELECT customer_asset.asset, customer_asset.field_type, customer_asset.status FROM customer_asset"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="list_asset_sets")
    def list_asset_sets(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Asset sets."""
        q = """SELECT asset_set.id, asset_set.name, asset_set.type, asset_set.status FROM asset_set"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_sitelinks")
    def get_sitelinks(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Sitelink assets."""
        q = """SELECT asset.id, asset.name, asset.sitelink_asset.link_text, asset.sitelink_asset.description1, asset.sitelink_asset.description2 FROM asset WHERE asset.type = SITELINK"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_callouts")
    def get_callouts(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Callout assets."""
        q = """SELECT asset.id, asset.name, asset.callout_asset.callout_text FROM asset WHERE asset.type = CALLOUT"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_structured_snippets")
    def get_structured_snippets(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Structured snippet assets."""
        q = """SELECT asset.id, asset.name, asset.structured_snippet_asset.header, asset.structured_snippet_asset.values FROM asset WHERE asset.type = STRUCTURED_SNIPPET"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_call_assets")
    def get_call_assets(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Call assets."""
        q = """SELECT asset.id, asset.name, asset.call_asset.phone_number, asset.call_asset.country_code FROM asset WHERE asset.type = CALL"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_location_assets")
    def get_location_assets(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Location assets."""
        q = """SELECT asset.id, asset.name, asset.location_asset.place_id FROM asset WHERE asset.type = LOCATION"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_image_assets")
    def get_image_assets(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Image assets."""
        q = """SELECT asset.id, asset.name, asset.image_asset.full_size.url, asset.image_asset.full_size.width_pixels, asset.image_asset.full_size.height_pixels FROM asset WHERE asset.type = IMAGE"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_conversions")
    def get_conversions(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Conversion metrics."""
        q = """SELECT segments.conversion_action_name, metrics.conversions, metrics.conversions_value FROM campaign"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="get_conversion_actions")
    def get_conversion_actions(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Conversion actions."""
        q = """SELECT conversion_action.id, conversion_action.name, conversion_action.status, conversion_action.type, conversion_action.category FROM conversion_action"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_conversion_goals")
    def get_conversion_goals(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Custom conversion goals (v25 custom_conversion_goal resource)."""
        q = """SELECT custom_conversion_goal.id, custom_conversion_goal.name, custom_conversion_goal.status FROM custom_conversion_goal"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_campaign_conversion_goals")
    def get_campaign_conversion_goals(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Campaign conversion goals."""
        q = """SELECT campaign_conversion_goal.category, campaign_conversion_goal.origin, campaign_conversion_goal.biddable, campaign.id FROM campaign_conversion_goal"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_customer_conversion_goals")
    def get_customer_conversion_goals(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Customer conversion goals."""
        q = """SELECT customer_conversion_goal.category, customer_conversion_goal.origin, customer_conversion_goal.biddable FROM customer_conversion_goal"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_conversion_performance")
    def get_conversion_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Conversion action performance."""
        q = """SELECT conversion_action.id, conversion_action.name, metrics.conversions, metrics.conversions_value, metrics.all_conversions FROM conversion_action"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="get_recommendations")
    def get_recommendations(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Active recommendations."""
        q = """SELECT recommendation.resource_name, recommendation.type, recommendation.impact.base_metrics.impressions, recommendation.impact.base_metrics.clicks FROM recommendation"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_optimization_score")
    def get_optimization_score(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Account optimization score."""
        q = """SELECT customer.id, customer.optimization_score FROM customer"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_change_history")
    def get_change_history(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Change history events."""
        q = """SELECT change_event.resource_name, change_event.change_date_time, change_event.change_resource_type, change_event.client_type, change_event.user_email FROM change_event ORDER BY change_event.change_date_time DESC LIMIT 100"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_change_events")
    def get_change_events(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Recent change events."""
        q = """SELECT change_event.resource_name, change_event.change_date_time, change_event.change_resource_type, change_event.changed_fields FROM change_event ORDER BY change_event.change_date_time DESC LIMIT 200"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_policy_issues")
    def get_policy_issues(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Policy-related issues."""
        q = """SELECT ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.review_status, ad_group_ad.ad.id, campaign.id FROM ad_group_ad WHERE ad_group_ad.policy_summary.approval_status != APPROVED"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_disapproved_ads")
    def get_disapproved_ads(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Disapproved ads."""
        q = """SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.policy_summary.approval_status, ad_group.id, campaign.id FROM ad_group_ad WHERE ad_group_ad.policy_summary.approval_status = DISAPPROVED"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_limited_ads")
    def get_limited_ads(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Limited ads."""
        q = """SELECT ad_group_ad.ad.id, ad_group_ad.policy_summary.approval_status, ad_group.id, campaign.id FROM ad_group_ad WHERE ad_group_ad.policy_summary.approval_status = APPROVED_LIMITED"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_keyword_policy_issues")
    def get_keyword_policy_issues(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Keyword policy issues."""
        q = """SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.system_serving_status, ad_group_criterion.approval_status FROM ad_group_criterion WHERE ad_group_criterion.type = KEYWORD AND ad_group_criterion.approval_status != APPROVED"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_bidding_strategies")
    def get_bidding_strategies(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Bidding strategies."""
        q = """SELECT bidding_strategy.id, bidding_strategy.name, bidding_strategy.type, bidding_strategy.status FROM bidding_strategy"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_bid_strategy_performance")
    def get_bid_strategy_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Bid strategy performance."""
        q = """SELECT bidding_strategy.id, bidding_strategy.name, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM bidding_strategy"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="get_account_budgets")
    def get_account_budgets(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Account budgets."""
        q = """SELECT account_budget.id, account_budget.name, account_budget.status, account_budget.approved_spending_limit_micros FROM account_budget"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_billing_setups")
    def get_billing_setups(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Billing setups."""
        q = """SELECT billing_setup.id, billing_setup.status, billing_setup.payments_account_info.payments_account_name FROM billing_setup"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_invoices_if_supported")
    def get_invoices_if_supported(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Invoices (may require elevated access)."""
        return {
            "success": False,
            "message": "invoice is not a GoogleAdsService GAQL resource in API v25. Use InvoiceService.list_invoices via google_ads_service_call (requires billing setup and issue month).",
            "suggested_action": "Call InvoiceService.list_invoices with customer_id, billing_setup, and issue_year_month.",
        }

    @mcp.tool(name="get_experiments")
    def get_experiments(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Experiments."""
        q = """SELECT experiment.resource_name, experiment.name, experiment.status, experiment.type FROM experiment"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_campaign_experiments")
    def get_campaign_experiments(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Campaign experiment arms (v25 experiment_arm; campaign_experiment was removed)."""
        q = """SELECT experiment_arm.resource_name, experiment_arm.experiment, experiment_arm.campaigns, experiment_arm.control FROM experiment_arm"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_audiences")
    def get_audiences(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Audiences."""
        q = """SELECT audience.id, audience.name, audience.status, audience.description FROM audience"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_user_lists")
    def get_user_lists(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """User lists."""
        q = """SELECT user_list.id, user_list.name, user_list.type, user_list.size_for_display, user_list.membership_status FROM user_list"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_audience_segments")
    def get_audience_segments(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Audience segments."""
        q = """SELECT audience.id, audience.name, audience.status FROM audience"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_performance_max_campaigns")
    def get_performance_max_campaigns(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Performance Max campaigns."""
        q = """SELECT campaign.id, campaign.name, campaign.status FROM campaign WHERE campaign.advertising_channel_type = PERFORMANCE_MAX"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_asset_groups")
    def get_asset_groups(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Asset groups."""
        q = """SELECT asset_group.id, asset_group.name, asset_group.status, campaign.id FROM asset_group"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_asset_group_performance")
    def get_asset_group_performance(customer_id: str | None = None, date_range: str | None = "LAST_30_DAYS", page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Asset group performance."""
        q = """SELECT asset_group.id, asset_group.name, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM asset_group"""
        return gaql_tool(q, customer_id=customer_id, date_range=date_range, page_size=page_size, stream=stream)

    @mcp.tool(name="get_asset_group_assets")
    def get_asset_group_assets(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Asset group assets."""
        q = """SELECT asset_group_asset.asset, asset_group_asset.field_type, asset_group.id FROM asset_group_asset"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_asset_group_signals")
    def get_asset_group_signals(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Asset group signals."""
        q = """SELECT asset_group_signal.audience.audience, asset_group.id FROM asset_group_signal"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_shopping_campaigns")
    def get_shopping_campaigns(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Shopping campaigns."""
        q = """SELECT campaign.id, campaign.name, campaign.status FROM campaign WHERE campaign.advertising_channel_type = SHOPPING"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_shopping_products_or_listing_groups_if_supported")
    def get_shopping_products_or_listing_groups_if_supported(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Shopping listing groups."""
        q = """SELECT asset_group_listing_group_filter.id, asset_group_listing_group_filter.type, asset_group.id FROM asset_group_listing_group_filter"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_video_campaigns_if_supported")
    def get_video_campaigns_if_supported(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Video campaigns."""
        q = """SELECT campaign.id, campaign.name, campaign.status FROM campaign WHERE campaign.advertising_channel_type = VIDEO"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_display_campaigns")
    def get_display_campaigns(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Display campaigns."""
        q = """SELECT campaign.id, campaign.name, campaign.status FROM campaign WHERE campaign.advertising_channel_type = DISPLAY"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_search_campaigns")
    def get_search_campaigns(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Search campaigns."""
        q = """SELECT campaign.id, campaign.name, campaign.status FROM campaign WHERE campaign.advertising_channel_type = SEARCH"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_negative_keywords")
    def get_negative_keywords(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Negative keywords."""
        q = """SELECT campaign_criterion.criterion_id, campaign_criterion.keyword.text, campaign.id FROM campaign_criterion WHERE campaign_criterion.type = KEYWORD AND campaign_criterion.negative = TRUE"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_negative_keyword_lists")
    def get_negative_keyword_lists(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Shared negative keyword lists."""
        q = """SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status FROM shared_set WHERE shared_set.type = NEGATIVE_KEYWORDS"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_shared_sets")
    def get_shared_sets(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Shared sets."""
        q = """SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status FROM shared_set"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_shared_criteria")
    def get_shared_criteria(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Shared set criteria."""
        q = """SELECT shared_criterion.criterion_id, shared_criterion.keyword.text, shared_set.id FROM shared_criterion"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_labels")
    def get_labels(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Labels."""
        q = """SELECT label.id, label.name, label.status FROM label"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_campaign_labels")
    def get_campaign_labels(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Campaign labels."""
        q = """SELECT campaign_label.label, campaign_label.campaign FROM campaign_label"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_ad_group_labels")
    def get_ad_group_labels(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Ad group labels."""
        q = """SELECT ad_group_label.label, ad_group_label.ad_group FROM ad_group_label"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_ad_labels")
    def get_ad_labels(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Ad labels."""
        q = """SELECT ad_group_ad_label.label, ad_group_ad_label.ad_group_ad FROM ad_group_ad_label"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_keyword_labels")
    def get_keyword_labels(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Keyword labels."""
        q = """SELECT ad_group_criterion_label.label, ad_group_criterion_label.ad_group_criterion FROM ad_group_criterion_label"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_locations")
    def get_locations(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Location criteria."""
        q = """SELECT campaign_criterion.location.geo_target_constant, campaign.id FROM campaign_criterion WHERE campaign_criterion.type = LOCATION"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_language_constants")
    def get_language_constants(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Language constants."""
        q = """SELECT language_constant.id, language_constant.code, language_constant.name FROM language_constant"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_geo_target_constants")
    def get_geo_target_constants(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Geo target constants."""
        q = """SELECT geo_target_constant.id, geo_target_constant.name, geo_target_constant.country_code, geo_target_constant.target_type FROM geo_target_constant LIMIT 100"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_keyword_plan_ideas")
    def get_keyword_plan_ideas(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Keyword plan ideas require KeywordPlanIdeaService; returns guidance."""
        return {"success": False, "message": "Use google_ads_service_call with KeywordPlanIdeaService.generate_keyword_ideas for keyword plan ideas.", "suggested_action": "Call KeywordPlanIdeaService.generate_keyword_ideas via google_ads_service_call."}

    @mcp.tool(name="get_keyword_historical_metrics")
    def get_keyword_historical_metrics(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Keyword historical metrics require KeywordPlanIdeaService; placeholder GAQL anchor."""
        return {"success": False, "message": "Use google_ads_service_call with KeywordPlanIdeaService.generate_keyword_historical_metrics.", "suggested_action": "Call KeywordPlanIdeaService.generate_keyword_historical_metrics via google_ads_service_call."}

    @mcp.tool(name="get_account_recommendations")
    def get_account_recommendations(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Account recommendations."""
        q = """SELECT recommendation.resource_name, recommendation.type, recommendation.campaign FROM recommendation"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="get_campaign_recommendations")
    def get_campaign_recommendations(customer_id: str | None = None, page_size: int | None = None, stream: bool = False) -> dict[str, Any]:
        """Campaign recommendations."""
        q = """SELECT recommendation.resource_name, recommendation.type, recommendation.campaign FROM recommendation WHERE recommendation.campaign IS NOT NULL"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

    @mcp.tool(name="list_extensions_or_equivalent_asset_based_extensions")
    def list_extensions_or_equivalent_asset_based_extensions(
        customer_id: str | None = None,
        page_size: int | None = None,
        stream: bool = False,
    ) -> dict[str, Any]:
        """Asset-linked extensions (sitelinks, callouts, snippets, calls, locations, images)."""
        q = """SELECT campaign.id, campaign_asset.asset, campaign_asset.field_type, campaign_asset.status FROM campaign_asset WHERE campaign_asset.field_type IN (SITELINK, CALLOUT, STRUCTURED_SNIPPET, CALL, LOCATION, IMAGE)"""
        return gaql_tool(q, customer_id=customer_id, page_size=page_size, stream=stream)

