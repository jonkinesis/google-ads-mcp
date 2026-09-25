"""Fixed account-level reporting boundary; never dispatches MCP tools or mutations."""
from __future__ import annotations
import hmac
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse
from app.config import get_settings
from app.google_ads_client import execute_gaql

ACCOUNT = '5227914768'
METRICS = 'metrics.cost_micros, metrics.impressions, metrics.clicks, metrics.ctr, metrics.average_cpc, metrics.conversions, metrics.conversions_value, metrics.cost_per_conversion, metrics.conversions_from_interactions_rate'
QUERIES = {
 'account': 'SELECT customer.id, customer.descriptive_name, customer.currency_code, customer.time_zone, customer.status FROM customer LIMIT 2',
 'campaigns': "SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type, campaign.primary_status, campaign.primary_status_reasons, campaign_budget.amount_micros FROM campaign WHERE campaign.status != 'REMOVED' LIMIT 501",
 'conversionActions': 'SELECT conversion_action.id, conversion_action.name, conversion_action.status, conversion_action.type, conversion_action.category, conversion_action.primary_for_goal, conversion_action.value_settings.default_value, conversion_action.value_settings.always_use_default_value FROM conversion_action LIMIT 501',
 'conversionPerformance': 'SELECT segments.conversion_action, segments.conversion_action_name, segments.conversion_action_category, metrics.conversions, metrics.conversions_value, metrics.all_conversions FROM customer WHERE segments.date DURING LAST_30_DAYS LIMIT 501',
 'campaignPerformance': 'SELECT campaign.id, metrics.cost_micros, metrics.impressions, metrics.clicks, metrics.conversions FROM campaign WHERE segments.date DURING LAST_30_DAYS LIMIT 501',
 'diagnostics': "SELECT campaign.id, campaign.status, ad_group_ad.ad.id, ad_group_ad.policy_summary.approval_status FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED' AND ad_group_ad.policy_summary.approval_status = 'DISAPPROVED' LIMIT 501",
}
QUERIES['campaignPerformance'] = f'SELECT campaign.id, {METRICS} FROM campaign WHERE segments.date DURING LAST_30_DAYS LIMIT 501'
DETAIL_QUERIES = {
 'campaignPerformance7': f'SELECT campaign.id, {METRICS} FROM campaign WHERE segments.date DURING LAST_7_DAYS LIMIT 2001',
 'daily': f'SELECT campaign.id, segments.date, {METRICS} FROM campaign WHERE segments.date DURING LAST_30_DAYS LIMIT 2001',
 'devices': f'SELECT segments.device, {METRICS} FROM customer WHERE segments.date DURING LAST_30_DAYS LIMIT 2001',
 'keywords': f'SELECT campaign.id, ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, {METRICS} FROM keyword_view WHERE segments.date DURING LAST_30_DAYS AND metrics.impressions > 0 LIMIT 2001',
 'searchTerms': f'SELECT campaign.id, ad_group.id, search_term_view.search_term, {METRICS} FROM search_term_view WHERE segments.date DURING LAST_30_DAYS LIMIT 2001',
}
for name in ('devices', 'keywords', 'searchTerms'):
 DETAIL_QUERIES[name+'7'] = DETAIL_QUERIES[name].replace('LAST_30_DAYS', 'LAST_7_DAYS')
for days in (7,30):
 QUERIES[f'last{days}'] = f'SELECT {METRICS} FROM customer WHERE segments.date DURING LAST_{days}_DAYS LIMIT 2'

def collect_observations(query=execute_gaql):
 settings=get_settings()
 if settings.google_ads_customer_id != ACCOUNT: raise ValueError('Account mismatch')
 results={}
 for name, gaql in QUERIES.items():
  value=query(gaql,customer_id=ACCOUNT,stream=True)
  rows=value.get('data')
  if value.get('success') is not True or value.get('customer_id')!=ACCOUNT or not isinstance(rows,list) or len(rows)>=501 or value.get('next_page_token'): raise ValueError('Incomplete reporting')
  results[name]=rows
 if len(results['account'])!=1 or results['account'][0].get('customer',{}).get('id')!=ACCOUNT: raise ValueError('Account mismatch')
 account=results['account'][0]['customer']
 today=datetime.now(ZoneInfo(account['time_zone'])).date()
 periods={}
 for days in (7,30):
  rows=results[f'last{days}']
  if len(rows)>1: raise ValueError('Invalid aggregate')
  periods[str(days)]={'since':str(today-timedelta(days=days)), 'until':str(today-timedelta(days=1)), 'state':'available' if rows else 'unavailable', 'metrics':rows[0].get('metrics',{}) if rows else {}}
 details={}
 for name, gaql in DETAIL_QUERIES.items():
  try:
   value=query(gaql,customer_id=ACCOUNT,stream=True)
   rows=value.get('data')
   if value.get('success') is not True or value.get('customer_id')!=ACCOUNT or not isinstance(rows,list) or len(rows)>=2001 or value.get('next_page_token'): raise ValueError('Incomplete detail')
   details[name]={'state':'available','rows':rows,'period':periods['7' if name.endswith('7') else '30']}
  except Exception:
   details[name]={'state':'unavailable','rows':[],'period':periods['7' if name.endswith('7') else '30']}
 return {'details':details,'version':1,'provider':'Google Ads','scope':'marketing_channel','channel':'nightlife','destination':'https://nightlife.mythexperience.com/','observedAt':datetime.now(timezone.utc).isoformat(),'account':account,'periods':periods,'campaigns':results['campaigns'],'campaignPerformance':results['campaignPerformance'],'conversionActions':results['conversionActions'],'conversionPerformance':results['conversionPerformance'],'diagnostics':results['diagnostics'],'conversionValueTrust':'unverified_mixed_actions','provenance':{'interface':'fixed-gaql-read-only','periodSemantics':'account timezone; completed days; excludes today'}}

def register_observations(mcp):
 cache=None
 expires=0.0
 lock=threading.Lock()
 def cached():
  nonlocal cache,expires
  with lock:
   if cache is None or time.monotonic()>=expires:
    result=collect_observations()
    cache=result;expires=time.monotonic()+60
   return cache
 @mcp.custom_route('/observations/google-ads/snapshot',methods=['GET','POST','PUT','PATCH','DELETE','HEAD'])
 async def observations(request):
  headers={'Cache-Control':'private, no-store'}
  key=os.environ.get('COMMAND_CENTER_GOOGLE_ADS_READ_SECRET','')
  execution=get_settings().mcp_api_key
  if len(key)<32 or not execution or hmac.compare_digest(key,execution): return JSONResponse({'error':'Observer not configured'},503,headers=headers)
  supplied=request.headers.get('authorization','')
  if not hmac.compare_digest(supplied.encode(),('Bearer '+key).encode()): return JSONResponse({'error':'Unauthorized'},401,headers=headers)
  if request.method!='GET': return JSONResponse({'error':'Read-only endpoint'},405,headers=headers)
  if request.query_params or request.headers.get('transfer-encoding') or request.headers.get('content-length','0')!='0': return JSONResponse({'error':'Parameters not accepted'},400,headers=headers)
  try: return JSONResponse(await run_in_threadpool(cached),headers=headers)
  except Exception: return JSONResponse({'error':'Google Ads observations unavailable; previous observations preserved'},502,headers=headers)
