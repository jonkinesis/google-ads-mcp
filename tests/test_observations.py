from unittest.mock import patch
import pytest
from starlette.testclient import TestClient
from app.observations import collect_observations, ACCOUNT, QUERIES
from app.config import get_settings
KEY='observer-test-only-'+'x'*40

def test_boundary(monkeypatch):
 monkeypatch.setenv('COMMAND_CENTER_GOOGLE_ADS_READ_SECRET',KEY)
 from app.server import create_mcp
 with patch('app.observations.collect_observations',return_value={'safe':True}) as collect:
  with TestClient(create_mcp().http_app(path='/mcp',stateless_http=True)) as c:
   path='/observations/google-ads/snapshot'
   for key in ['wrong','test-key']:
    assert c.get(path,headers={'Authorization':'Bearer '+key}).status_code==401
   headers={'Authorization':'Bearer '+KEY}
   for method in ['post','put','patch','delete']:assert getattr(c,method)(path,headers=headers).status_code==405
   assert c.get(path+'?query=mutate',headers=headers).status_code==400
   assert c.post('/mcp',headers=headers,json={'jsonrpc':'2.0','id':1,'method':'tools/list'}).status_code==401
   assert collect.call_count==0
   assert c.get(path,headers=headers).json()=={'safe':True}
   assert c.get(path,headers=headers).status_code==200
   assert collect.call_count==1

def test_queries_account_periods_and_no_inferred_zero(monkeypatch):
 monkeypatch.setenv('GOOGLE_ADS_CUSTOMER_ID',ACCOUNT);get_settings.cache_clear()
 calls=[]
 def query(q,**kwargs):
  assert q.startswith('SELECT ');assert kwargs=={'customer_id':ACCOUNT,'stream':True};calls.append(q)
  rows=[{'customer':{'id':ACCOUNT,'time_zone':'America/New_York'}}] if q==QUERIES['account'] else []
  if q==QUERIES['last30']:rows=[{'metrics':{'cost_micros':'0','conversions':0}}]
  return {'success':True,'customer_id':ACCOUNT,'data':rows}
 result=collect_observations(query)
 assert len(calls)==16
 assert result["details"]["keywords"]["state"]=="available"
 assert result['scope']=='marketing_channel'
 assert result['periods']['30']['metrics']['cost_micros']=='0'
 assert 'clicks' not in result['periods']['30']['metrics']
 assert result['periods']['7']['state']=='unavailable'
 assert 'events' not in result
 assert result['conversionValueTrust']=='unverified_mixed_actions'

def test_failure_and_account_lock(monkeypatch):
 with pytest.raises(ValueError):collect_observations(lambda *a,**k: {})
 monkeypatch.setenv('GOOGLE_ADS_CUSTOMER_ID',ACCOUNT);get_settings.cache_clear()
 with pytest.raises(ValueError):collect_observations(lambda *a,**k: {'success':False})

def test_optional_detail_failure_preserves_aggregate_contract(monkeypatch):
 from app.observations import DETAIL_QUERIES
 monkeypatch.setenv('GOOGLE_ADS_CUSTOMER_ID',ACCOUNT);get_settings.cache_clear()
 def query(q,**kwargs):
  if q==DETAIL_QUERIES['keywords']: return {'success':False}
  rows=[{'customer':{'id':ACCOUNT,'time_zone':'America/New_York'}}] if q==QUERIES['account'] else []
  return {'success':True,'customer_id':ACCOUNT,'data':rows}
 result=collect_observations(query)
 assert result['details']['keywords']['state']=='unavailable'
 assert result['details']['keywords']['rows']==[]
 assert result['details']['devices']['state']=='available'
 assert result['details']['campaignPerformance7']['period']==result['periods']['7']
 assert result['details']['daily']['period']==result['periods']['30']


def test_separate_completed_seven_day_details(monkeypatch):
 from app.observations import DETAIL_QUERIES
 monkeypatch.setenv('GOOGLE_ADS_CUSTOMER_ID',ACCOUNT);get_settings.cache_clear()
 def query(q,**kwargs):
  rows=[{'customer':{'id':ACCOUNT,'time_zone':'America/New_York'}}] if q==QUERIES['account'] else []
  if q==DETAIL_QUERIES['searchTerms7']: return {'success':False}
  if q==DETAIL_QUERIES['keywords7']: rows=[{'metrics':{'clicks':7}}]
  if q==DETAIL_QUERIES['keywords']: rows=[{'metrics':{'clicks':30}}]
  return {'success':True,'customer_id':ACCOUNT,'data':rows}
 result=collect_observations(query)
 for name in ('devices','keywords','searchTerms'):
  assert 'LAST_7_DAYS' in DETAIL_QUERIES[name+'7']
  assert result['details'][name+'7']['period']==result['periods']['7']
  assert result['details'][name]['period']==result['periods']['30']
 assert result['details']['keywords7']['rows'][0]['metrics']['clicks']==7
 assert result['details']['keywords']['rows'][0]['metrics']['clicks']==30
 assert result['details']['searchTerms7']['state']=='unavailable'
 assert result['details']['searchTerms7']['rows']==[]
 assert result['details']['searchTerms']['state']=='available'
