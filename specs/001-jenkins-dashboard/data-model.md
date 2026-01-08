# Data Model: Jenkins Build Status Dashboard

**Feature**: 001-jenkins-dashboard
**Date**: 2026-01-08

## Overview

此 Dashboard 主要從 Jenkins API 讀取資料，本身僅需要儲存使用者 Session 和 Audit Log。

---

## Entities

### 1. User (Session Context)

代表已認證的使用者，資料來自 SSO。

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| id | string | 使用者唯一識別碼 | SSO claim: `sub` |
| email | string | 使用者 email | SSO claim: `email` |
| name | string | 顯示名稱 | SSO claim: `name` |
| roles | list[string] | 使用者角色（PM, RD_Manager） | SSO claim: `groups` or custom |
| login_time | datetime | 登入時間 | System generated |

**Validation Rules:**
- `email` MUST be non-empty
- `roles` MUST contain at least one allowed role (PM, RD_Manager, Admin)

**Note:** 此 Entity 存在於 Session 中，不持久化到資料庫。

---

### 2. JenkinsJob

代表 Jenkins 中的一個 Build Job，資料來自 Jenkins API。

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| name | string | Job 名稱 | Jenkins API: `name` |
| url | string | Job URL | Jenkins API: `url` |
| color | string | 狀態顏色代碼 | Jenkins API: `color` |
| status | enum | 解析後的狀態 | Derived from `color` |
| last_build_number | int? | 最後 Build 編號 | Jenkins API: `lastBuild.number` |
| last_build_result | enum? | 最後 Build 結果 | Jenkins API: build info |
| last_build_timestamp | datetime? | 最後 Build 時間 | Jenkins API: build info |
| last_build_duration_ms | int? | Build 持續時間（毫秒） | Jenkins API: build info |
| is_building | bool | 是否正在 Building | Jenkins API: `color` contains `_anime` |

**Status Enum Values:**
- `SUCCESS` - 最後 Build 成功（綠色）
- `FAILURE` - 最後 Build 失敗（紅色）
- `UNSTABLE` - 最後 Build 不穩定（黃色）
- `BUILDING` - 正在 Building（動畫）
- `DISABLED` - Job 已停用（灰色）
- `NOT_BUILT` - 從未 Build（灰色）
- `ABORTED` - Build 已中止（灰色）
- `UNKNOWN` - 無法判斷狀態

**Color to Status Mapping:**
```
blue -> SUCCESS
red -> FAILURE
yellow -> UNSTABLE
blue_anime -> BUILDING (was SUCCESS)
red_anime -> BUILDING (was FAILURE)
yellow_anime -> BUILDING (was UNSTABLE)
disabled -> DISABLED
notbuilt -> NOT_BUILT
aborted -> ABORTED
```

**Validation Rules:**
- `name` MUST be non-empty
- `url` MUST be valid URL format
- `last_build_number` MUST be > 0 if present

---

### 3. DashboardState

Dashboard 的即時狀態，用於快取和顯示。

| Field | Type | Description |
|-------|------|-------------|
| jobs | list[JenkinsJob] | 所有 Job 列表 |
| last_refresh | datetime | 最後成功刷新時間 |
| is_jenkins_available | bool | Jenkins 是否可連線 |
| error_message | string? | 錯誤訊息（如有） |
| total_jobs | int | Job 總數 |
| success_count | int | 成功 Job 數量 |
| failure_count | int | 失敗 Job 數量 |
| building_count | int | Building 中數量 |

**Derived Statistics:**
- `success_rate` = success_count / total_jobs * 100
- `health_indicator` = based on failure_count (0: healthy, 1-2: warning, 3+: critical)

---

### 4. AuditLogEntry

安全稽核日誌，符合 FR-010。

| Field | Type | Description |
|-------|------|-------------|
| id | uuid | 唯一識別碼 |
| timestamp | datetime | 事件時間 |
| user_id | string? | 使用者 ID（如已認證） |
| user_email | string? | 使用者 email |
| action | enum | 動作類型 |
| result | enum | 結果 |
| ip_address | string | 來源 IP |
| user_agent | string? | 瀏覽器資訊 |
| details | dict? | 額外資訊 |

**Action Enum Values:**
- `LOGIN_ATTEMPT` - 登入嘗試
- `LOGIN_SUCCESS` - 登入成功
- `LOGIN_FAILURE` - 登入失敗
- `LOGOUT` - 登出
- `ACCESS_DENIED` - 存取被拒絕
- `SESSION_EXPIRED` - Session 過期

**Result Enum Values:**
- `SUCCESS` - 成功
- `FAILURE` - 失敗
- `BLOCKED` - 被阻擋

**Storage:** 建議寫入檔案或外部日誌系統（如 ELK），不需要資料庫。

---

## State Transitions

### User Session State

```
[Anonymous] --login()--> [Authenticated] --logout()--> [Anonymous]
                              |
                              +--session_expired--> [Anonymous]
                              |
                              +--role_revoked--> [AccessDenied] --> [Anonymous]
```

### Jenkins Connection State

```
[Unknown] --connect()--> [Connected] --timeout/error--> [Disconnected]
                              |                              |
                              +<----retry_success------------+
```

---

## Relationships

```
┌─────────────────┐
│     User        │
│  (from SSO)     │
└────────┬────────┘
         │ views
         ▼
┌─────────────────┐      fetches      ┌─────────────────┐
│ DashboardState  │ ◄───────────────► │  Jenkins API    │
│   (in-memory)   │                   │   (external)    │
└────────┬────────┘                   └─────────────────┘
         │ contains
         ▼
┌─────────────────┐
│   JenkinsJob    │
│  (list, cached) │
└─────────────────┘

User actions ──► AuditLogEntry (append-only log)
```

---

## Data Flow

1. **Authentication Flow:**
   - User → SSO → User entity created in session
   - Login event → AuditLogEntry

2. **Dashboard Refresh Flow:**
   - Timer/Manual trigger → Jenkins API call
   - API response → Parse into JenkinsJob list
   - Update DashboardState
   - Display to User

3. **Error Handling Flow:**
   - Jenkins API error → Set is_jenkins_available = false
   - Preserve cached jobs
   - Display warning with last_refresh timestamp
