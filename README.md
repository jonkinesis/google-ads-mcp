# google-ads-mcp

Production-ready **remote MCP server** that connects ChatGPT Business (or any MCP client) to the **Google Ads API** using **service-account authentication**.

Built for the Myth Nightclub Google Ads account with conservative initial usage (monitoring, reporting, small approved optimizations), while exposing broad generic read/mutate capabilities so you do not need to redesign the connector later.

## Stack

- Python 3.12
- [FastMCP](https://gofastmcp.com/) (HTTP / Streamable MCP)
- Official [`google-ads`](https://pypi.org/project/google-ads/) Python client (uses the library's current default API version, e.g. **v25** with `google-ads` 32.x)
- Uvicorn ASGI on Railway

## Endpoints

| Path | Auth | Purpose |
|------|------|---------|
| `GET /health` | None | Health check (no secrets) |
| `/mcp` | `Authorization: Bearer <MCP_API_KEY>` | MCP transport |

## Environment variables

```env
GOOGLE_ADS_CUSTOMER_ID=
GOOGLE_ADS_LOGIN_CUSTOMER_ID=
GOOGLE_SERVICE_ACCOUNT_JSON=
MCP_API_KEY=
MCP_TOOL_MODE=compact
MAX_BUDGET_CHANGE_PERCENT=15
MAX_BID_CHANGE_PERCENT=15
PORT=
```

Notes:

- `MCP_TOOL_MODE` controls how many tools ChatGPT sees at the MCP layer (default **`compact`**). All tools remain implemented in code; **`full`** exposes every registered tool (~200+).
- `GOOGLE_ADS_CUSTOMER_ID` must be **10 digits, numbers only** (no hyphens). Hyphens in input are stripped automatically.
- `GOOGLE_ADS_LOGIN_CUSTOMER_ID` is optional (use for MCC / manager access).
- `GOOGLE_SERVICE_ACCOUNT_JSON` is the **full service account JSON** as one variable. Escaped `\n` inside `private_key` is supported.
- **Developer token is not required** for this deployment model (Google Cloud project API access level controls production access).
- Secrets are never logged.

## Local development

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GOOGLE_ADS_CUSTOMER_ID=XXXXXXXXXX
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
export MCP_API_KEY=your-secret
uvicorn app.server:app --host 0.0.0.0 --port 8000
```

Run tests:

```bash
pytest
```

## Railway deployment

1. Create a new Railway project from this repository.
2. Set **Root Directory** to repo root (contains `Dockerfile`).
3. Add environment variables from `.env.example` (paste service account JSON into `GOOGLE_SERVICE_ACCOUNT_JSON`).
4. Railway sets `PORT` automatically; the container listens on `0.0.0.0:$PORT`.
5. Deploy and verify:
   - `GET https://<your-app>.up.railway.app/health`
6. Configure ChatGPT Business MCP:
   - **URL:** `https://<your-app>.up.railway.app/mcp`
   - **Header:** `Authorization: Bearer <MCP_API_KEY>`

### Railway checklist

- [ ] Service account has **Standard** access on the Google Ads account
- [ ] Google Cloud project has Google Ads API enabled with appropriate access level
- [ ] `GOOGLE_ADS_CUSTOMER_ID` set (Myth Nightclub account, digits only)
- [ ] `MCP_API_KEY` set to a long random secret
- [ ] `/health` returns `{"status":"ok",...}`

## MCP tool exposure modes

| Mode | Env value | Behavior |
|------|-----------|----------|
| **Compact** (default) | `MCP_TOOL_MODE=compact` | Exposes ~60 high-value read/write/remove tools plus generic API tools (`google_ads_query`, `google_ads_mutate`, `google_ads_resource_mutate`, etc.). |
| **Full** | `MCP_TOOL_MODE=full` | Exposes every implemented tool for advanced operators. |

`GET /health` includes `mcp_tool_mode`, `tools_exposed`, and `tools_implemented`.

## Safety controls

All mutation tools support:

- `dry_run: bool` — uses `validate_only` when the API supports it
- `override_limits: bool` — bypasses convenience budget/bid guardrails

Environment guardrails (convenience tools):

- `MAX_BUDGET_CHANGE_PERCENT`
- `MAX_BID_CHANGE_PERCENT`

Generic raw mutation tools (`google_ads_mutate`, `google_ads_service_call`, etc.) emit a **limit warning** when guardrails are configured but not overridden.

Remove operations always return an explicit **remove summary** (resource name + customer ID).

## Architecture

```
app/
  server.py            # FastMCP + /health + ASGI app
  auth.py              # Service account JSON parsing
  config.py            # Environment settings
  google_ads_client.py # Client factory + GAQL execution
  gaql.py              # GAQL validation
  errors.py            # Google Ads error formatting
  audit.py             # Structured stdout audit logs
  safety.py            # Budget/bid limits
  mutations.py         # Generic mutate + service call dispatch
  services_registry.py # Dynamic service/method allowlist
tools/
  raw_api.py           # Generic/future-proof tools
  reporting.py         # GAQL convenience reads
  campaigns.py ...     # Domain write tools
```

## Tool surface (summary)

### Generic / future-proof

- `google_ads_query`
- `google_ads_describe_fields`
- `google_ads_list_services`
- `google_ads_service_call`
- `google_ads_mutate`
- `google_ads_batch_mutate` / `google_ads_multi_mutate`
- `google_ads_resource_mutate`
- `google_ads_batch_job`

### Convenience reads (GAQL)

Account, campaigns, budgets, ad groups, ads, keywords, search terms, segments (geo/device/network/time), assets & extensions, conversions, recommendations, policy, bidding, billing, experiments, audiences, Performance Max, shopping/video/display/search campaign filters, negatives, labels, geo/language constants, etc. (see `tools/reporting.py`).

### Convenience writes

Campaigns, budgets, bidding, ad groups, keywords/negatives, targeting, ads (RSA), assets, conversions upload, recommendations, audiences/user lists, Performance Max, experiments, labels, billing setup, batch jobs.

Use `google_ads_list_services` + `google_ads_service_call` for any additional Google Ads service methods not wrapped by a named convenience tool.

## Known API Coverage Gaps

- **Keyword Plan Idea / historical metrics**: use `google_ads_service_call` with `KeywordPlanIdeaService` (not full GAQL).
- **Customer Match member removal**: requires `OfflineUserDataJobService` job workflow; helper returns guidance.
- **Invoices**: `invoice` is **not** a `GoogleAdsService` GAQL resource in API v25. `get_invoices_if_supported` returns guidance; use `InvoiceService.list_invoices` via `google_ads_service_call` (billing setup + issue month; may require elevated access).
- **`conversion_goal` resource**: removed. Convenience reads use `custom_conversion_goal` (plus `campaign_conversion_goal` / `customer_conversion_goal`). The newer `goal` resource is not wrapped as a named convenience tool.
- **`campaign_experiment` resource**: removed. Use `experiment` and `experiment_arm`.
- **Combined age + gender demographics**: not supported in one GAQL query. `get_demographic_performance` uses `gender_view` only; query `age_range_view` separately via `google_ads_query`.
- **Asset / listing metrics**: some `FROM asset` metric combinations can be rejected by the live API even when fields exist on the proto. Errors are returned verbatim — do not assume every convenience report is selectable together.
- **Per-service named wrappers**: all installed services are reachable via `google_ads_service_call`; not every service has a dedicated convenience alias.
- **Explorer access limitations**: write or specialized endpoints may fail until Google Cloud API access is upgraded — errors include suggested actions.
- **Resource mutate dispatcher**: maps to the primary `mutate_*` method per service; exotic operation shapes may require `google_ads_service_call` with an explicit request payload.

## Audit logging

Structured JSON logs for write operations go to **stdout** (Railway log retention), including tool name, customer ID, dry-run flag, resource names, success/failure, and Google request ID when available. Secrets are not logged.
