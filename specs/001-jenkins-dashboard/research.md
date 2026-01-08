# Research: Jenkins Build Status Dashboard

**Feature**: 001-jenkins-dashboard
**Date**: 2026-01-08

## Decision Summary

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Web Framework | Streamlit | 快速開發、內建 UI 元件、自動刷新功能、適合 Dashboard 類應用 |
| SSO Integration | Native Streamlit OIDC | Streamlit 1.32+ 內建 OIDC 支援，可整合企業 SSO |
| Jenkins Client | python-jenkins | 維護良好、API 完整、OpenStack 支持 |
| Caching | In-memory with TTL | 簡單有效，適合單一實例部署 |

---

## 1. Web Framework Selection

### Decision: Streamlit

**Rationale:**
- 內建 Dashboard UI 元件（表格、圖表、狀態指示器）
- 自動刷新功能符合 FR-005 需求（30 秒自動更新）
- 開發速度快，適合此規模的專案
- 原生支援 OIDC 認證（v1.32+）

**Alternatives Considered:**

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| Flask | 完全控制、高度客製化 | 需自建前端、開發時間長 | 開發成本過高，Dashboard 不需要高度客製化 |
| FastAPI + React | 分離前後端、效能好 | 複雜度高、需要前端技能 | 過度工程化，不符 YAGNI 原則 |

---

## 2. SSO Integration

### Decision: Native Streamlit OIDC

**Rationale:**
- Streamlit 1.32+ 內建 `st.login()`, `st.logout()`, `st.user` API
- 支援任何 OIDC-compliant provider（Azure AD, Okta, Google, Auth0）
- 無需額外套件，降低維護成本

**Implementation Pattern:**
```python
import streamlit as st

if not st.user.is_logged_in:
    if st.button("使用公司帳號登入"):
        st.login()
    st.stop()

st.markdown(f"歡迎，{st.user.name}")
```

**Configuration (secrets.toml):**
```toml
[auth]
redirect_uri = "https://dashboard.company.com/oauth2callback"
cookie_secret = "<strong-random-secret>"

[auth.company_sso]
client_id = "<sso-client-id>"
client_secret = "<sso-client-secret>"
server_metadata_url = "https://sso.company.com/.well-known/openid-configuration"
```

**Limitations:**
- Cookie 過期時間固定 30 天（不可配置）
- 僅支援 OIDC，若使用 SAML 需透過 Auth0/Descope 轉換
- 授權（role-based access）需自行實作

**Alternatives Considered:**

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| streamlit-authenticator | 簡單設定 | 僅支援帳號密碼，無 SSO | 不符合 FR-012 SSO 需求 |
| streamlit-keycloak | 完整 Keycloak 支援 | 限定 Keycloak | 假設公司使用通用 OIDC provider |

---

## 3. Jenkins API Integration

### Decision: python-jenkins Library

**Rationale:**
- OpenStack 維護，穩定可靠
- 提供完整的 Job 和 Build 資訊 API
- 支援 API Token 認證

**Key API Patterns:**
```python
import jenkins

server = jenkins.Jenkins(
    'https://jenkins.company.com',
    username='service-account',
    password='api-token'  # 使用 API Token，非密碼
)

# 取得所有 Jobs
jobs = server.get_all_jobs()

# 取得 Job 狀態
job_info = server.get_job_info('my-job')
last_build_num = job_info['lastCompletedBuild']['number']

# 取得 Build 詳情
build_info = server.get_build_info('my-job', last_build_num)
status = build_info['result']  # SUCCESS, FAILURE, UNSTABLE, ABORTED
```

**Alternatives Considered:**

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| jenkinsapi | 更 Pythonic | 維護較少 | 穩定性考量選擇 python-jenkins |
| Direct requests | 無依賴 | 需手動處理 API | 重複造輪子，增加維護成本 |

---

## 4. Caching Strategy

### Decision: In-memory Caching with TTL

**Rationale:**
- 單一實例部署，in-memory 足夠
- 避免對 Jenkins 過度請求
- 使用 `@st.cache_data` 配合 TTL

**Implementation Pattern:**
```python
import streamlit as st

@st.cache_data(ttl=30)  # 30 秒 TTL
def get_all_job_statuses():
    return jenkins_client.get_all_jobs_status()
```

**Caching Policy:**
- Job 狀態：30 秒 TTL（符合 FR-005）
- 已完成的 Build 詳情：永久快取（不會改變）
- 連線錯誤時顯示快取資料並標示時間戳

---

## 5. Role-Based Access Control

### Decision: Session-based Role Validation

**Rationale:**
- 從 SSO 取得使用者資訊後驗證角色
- 使用 `st.session_state` 儲存角色資訊

**Implementation Approach:**
```python
ALLOWED_ROLES = {"PM", "RD_Manager", "Admin"}

def check_authorization():
    if not st.user.is_logged_in:
        return False

    # 假設 SSO 返回 groups/roles 資訊
    user_roles = set(st.user.get("groups", []))
    return bool(user_roles & ALLOWED_ROLES)
```

**Note:** 具體實作取決於公司 SSO 返回的 claims 格式。

---

## 6. Error Handling Strategy

### Decision: Graceful Degradation with Cached Data

**Rationale:**
- 符合 SC-007：Jenkins 不可用時仍顯示快取資料
- 提供清楚的錯誤訊息和最後更新時間

**Pattern:**
```python
try:
    jobs = get_all_job_statuses()
    st.session_state.last_refresh = datetime.now()
except JenkinsConnectionError:
    st.warning("⚠️ 無法連接 Jenkins，顯示快取資料")
    st.caption(f"最後更新: {st.session_state.last_refresh}")
    jobs = st.session_state.cached_jobs
```

---

## Technology Stack Summary

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.11+ |
| Web Framework | Streamlit | 1.32+ |
| Jenkins Client | python-jenkins | Latest |
| Authentication | Native Streamlit OIDC | Built-in |
| Testing | pytest | Latest |
| Linting | ruff | Latest |
| Type Checking | mypy | Latest |
