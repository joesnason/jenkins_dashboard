# Internal API Contracts: Jenkins Build Status Dashboard

**Feature**: 001-jenkins-dashboard
**Date**: 2026-01-08

## Overview

此 Dashboard 使用 Streamlit，主要透過 Python 函數而非 REST API 進行內部通訊。
以下定義內部 Service Layer 的函數契約。

---

## Authentication Service

### `authenticate_user() -> User | None`

從 Streamlit SSO 取得已認證使用者。

**Returns:**
- `User` - 已認證的使用者物件
- `None` - 使用者未登入

**Example:**
```python
user = authenticate_user()
if user is None:
    st.login()
    st.stop()
```

---

### `check_authorization(user: User) -> bool`

檢查使用者是否有權限存取 Dashboard。

**Parameters:**
- `user: User` - 使用者物件

**Returns:**
- `True` - 使用者有權限（PM 或 RD Manager 角色）
- `False` - 使用者無權限

**Side Effects:**
- 記錄 `ACCESS_DENIED` 到 Audit Log（若回傳 False）

---

### `logout_user() -> None`

登出當前使用者。

**Side Effects:**
- 清除 Session 資料
- 記錄 `LOGOUT` 到 Audit Log
- 呼叫 `st.logout()`

---

## Jenkins Service

### `get_all_jobs() -> list[JenkinsJob]`

取得所有 Jenkins Job 及其狀態。

**Returns:**
- `list[JenkinsJob]` - Job 列表

**Raises:**
- `JenkinsConnectionError` - Jenkins 連線失敗
- `JenkinsAuthError` - Jenkins 認證失敗

**Caching:**
- TTL: 30 秒
- 使用 `@st.cache_data(ttl=30)`

**Example Response:**
```python
[
    JenkinsJob(
        name="frontend-build",
        url="https://jenkins.company.com/job/frontend-build/",
        status=JobStatus.SUCCESS,
        last_build_number=142,
        last_build_result="SUCCESS",
        last_build_timestamp=datetime(2026, 1, 8, 10, 30, 0),
        last_build_duration_ms=45000,
        is_building=False
    ),
    JenkinsJob(
        name="backend-deploy",
        url="https://jenkins.company.com/job/backend-deploy/",
        status=JobStatus.BUILDING,
        last_build_number=89,
        last_build_result=None,  # Still building
        last_build_timestamp=datetime(2026, 1, 8, 11, 0, 0),
        last_build_duration_ms=None,
        is_building=True
    )
]
```

---

### `get_job_details(job_name: str) -> JenkinsJob`

取得單一 Job 的詳細資訊。

**Parameters:**
- `job_name: str` - Job 名稱

**Returns:**
- `JenkinsJob` - Job 詳細資訊

**Raises:**
- `JenkinsJobNotFoundError` - Job 不存在
- `JenkinsConnectionError` - Jenkins 連線失敗

---

### `refresh_jobs() -> DashboardState`

手動刷新所有 Job 資料（清除快取）。

**Returns:**
- `DashboardState` - 更新後的 Dashboard 狀態

**Side Effects:**
- 清除 `get_all_jobs` 快取
- 更新 `st.session_state.last_refresh`

---

## Dashboard State Service

### `get_dashboard_state() -> DashboardState`

取得當前 Dashboard 狀態。

**Returns:**
```python
DashboardState(
    jobs=[...],
    last_refresh=datetime(2026, 1, 8, 11, 5, 30),
    is_jenkins_available=True,
    error_message=None,
    total_jobs=15,
    success_count=12,
    failure_count=2,
    building_count=1
)
```

**Fallback Behavior:**
- 若 Jenkins 不可用，回傳最後快取的狀態
- `is_jenkins_available` 設為 `False`
- `error_message` 包含錯誤描述

---

### `calculate_statistics(jobs: list[JenkinsJob]) -> dict`

計算 Job 統計資料。

**Parameters:**
- `jobs: list[JenkinsJob]` - Job 列表

**Returns:**
```python
{
    "total": 15,
    "success": 12,
    "failure": 2,
    "building": 1,
    "disabled": 0,
    "success_rate": 80.0,
    "health": "warning"  # "healthy" | "warning" | "critical"
}
```

---

## Audit Service

### `log_event(action: AuditAction, result: AuditResult, user: User | None, details: dict | None) -> None`

記錄稽核事件。

**Parameters:**
- `action: AuditAction` - 動作類型
- `result: AuditResult` - 結果
- `user: User | None` - 使用者（可選）
- `details: dict | None` - 額外資訊

**Side Effects:**
- 寫入 Audit Log 檔案或系統

**Log Format:**
```json
{
    "timestamp": "2026-01-08T11:05:30.123Z",
    "action": "LOGIN_SUCCESS",
    "result": "SUCCESS",
    "user_id": "user123",
    "user_email": "pm@company.com",
    "ip_address": "192.168.1.100",
    "details": {}
}
```

---

## Error Types

```python
class JenkinsConnectionError(Exception):
    """Jenkins 伺服器無法連線"""
    pass

class JenkinsAuthError(Exception):
    """Jenkins API 認證失敗"""
    pass

class JenkinsJobNotFoundError(Exception):
    """指定的 Job 不存在"""
    pass

class AuthorizationError(Exception):
    """使用者無權限存取"""
    pass
```

---

## Type Definitions

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class JobStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    UNSTABLE = "unstable"
    BUILDING = "building"
    DISABLED = "disabled"
    NOT_BUILT = "not_built"
    ABORTED = "aborted"
    UNKNOWN = "unknown"

class AuditAction(Enum):
    LOGIN_ATTEMPT = "login_attempt"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    ACCESS_DENIED = "access_denied"
    SESSION_EXPIRED = "session_expired"

class AuditResult(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    BLOCKED = "blocked"

@dataclass
class User:
    id: str
    email: str
    name: str
    roles: list[str]
    login_time: datetime

@dataclass
class JenkinsJob:
    name: str
    url: str
    status: JobStatus
    last_build_number: Optional[int]
    last_build_result: Optional[str]
    last_build_timestamp: Optional[datetime]
    last_build_duration_ms: Optional[int]
    is_building: bool

@dataclass
class DashboardState:
    jobs: list[JenkinsJob]
    last_refresh: datetime
    is_jenkins_available: bool
    error_message: Optional[str]
    total_jobs: int
    success_count: int
    failure_count: int
    building_count: int
```
