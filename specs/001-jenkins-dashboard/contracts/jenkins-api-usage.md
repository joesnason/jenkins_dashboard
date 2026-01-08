# Jenkins API Usage Contract

**Feature**: 001-jenkins-dashboard
**Date**: 2026-01-08

## Overview

本文件定義 Dashboard 如何使用 Jenkins REST API。

---

## Authentication

**Method:** API Token

```python
import jenkins

server = jenkins.Jenkins(
    url=JENKINS_URL,          # e.g., "https://jenkins.company.com"
    username=JENKINS_USER,    # Service account username
    password=JENKINS_API_TOKEN  # API Token (NOT password)
)
```

**Environment Variables:**
- `JENKINS_URL` - Jenkins 伺服器 URL
- `JENKINS_USER` - Service account 使用者名稱
- `JENKINS_API_TOKEN` - API Token

---

## API Endpoints Used

### 1. Get All Jobs

**Endpoint:** `GET /api/json`

**python-jenkins Method:**
```python
jobs = server.get_all_jobs()
```

**Response Fields Used:**
```json
{
  "jobs": [
    {
      "name": "frontend-build",
      "url": "https://jenkins.company.com/job/frontend-build/",
      "color": "blue"
    }
  ]
}
```

**Color Mapping:**
| Jenkins Color | Dashboard Status |
|---------------|------------------|
| `blue` | SUCCESS |
| `red` | FAILURE |
| `yellow` | UNSTABLE |
| `blue_anime` | BUILDING |
| `red_anime` | BUILDING |
| `yellow_anime` | BUILDING |
| `disabled` | DISABLED |
| `notbuilt` | NOT_BUILT |
| `aborted` | ABORTED |

---

### 2. Get Job Info

**Endpoint:** `GET /job/{job_name}/api/json`

**python-jenkins Method:**
```python
job_info = server.get_job_info(job_name)
```

**Response Fields Used:**
```json
{
  "name": "frontend-build",
  "url": "https://jenkins.company.com/job/frontend-build/",
  "color": "blue",
  "lastBuild": {
    "number": 142,
    "url": "https://jenkins.company.com/job/frontend-build/142/"
  },
  "lastCompletedBuild": {
    "number": 142
  },
  "lastSuccessfulBuild": {
    "number": 142
  },
  "lastFailedBuild": {
    "number": 140
  }
}
```

---

### 3. Get Build Info

**Endpoint:** `GET /job/{job_name}/{build_number}/api/json`

**python-jenkins Method:**
```python
build_info = server.get_build_info(job_name, build_number)
```

**Response Fields Used:**
```json
{
  "number": 142,
  "result": "SUCCESS",
  "timestamp": 1704708600000,
  "duration": 45000,
  "building": false,
  "displayName": "#142",
  "url": "https://jenkins.company.com/job/frontend-build/142/"
}
```

**Result Values:**
- `SUCCESS` - Build 成功
- `FAILURE` - Build 失敗
- `UNSTABLE` - Build 不穩定（測試失敗等）
- `ABORTED` - Build 被中止
- `null` - Build 進行中

**Timestamp:** Unix timestamp in milliseconds

---

## Request Patterns

### Initial Load

```python
def load_all_jobs_with_details():
    """載入所有 Jobs 及其最後 Build 資訊"""
    jobs = server.get_all_jobs()
    result = []

    for job in jobs:
        job_info = server.get_job_info(job['name'])

        last_build = None
        if job_info.get('lastBuild'):
            last_build = server.get_build_info(
                job['name'],
                job_info['lastBuild']['number']
            )

        result.append(parse_jenkins_job(job_info, last_build))

    return result
```

### Refresh (Optimized)

```python
def refresh_jobs():
    """刷新 Jobs（使用 tree 參數優化）"""
    # 使用 tree 參數減少資料量
    url = f"{JENKINS_URL}/api/json?tree=jobs[name,url,color,lastBuild[number]]"
    response = requests.get(url, auth=(JENKINS_USER, JENKINS_API_TOKEN))
    return response.json()
```

---

## Rate Limiting

**Policy:**
- 自動刷新間隔：30 秒
- 手動刷新：無限制（使用者觸發）
- 建議：生產環境中每分鐘不超過 60 次 API 呼叫

**Backoff Strategy:**
```python
import time
import random

def fetch_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait)
```

---

## Error Handling

| HTTP Status | Meaning | Dashboard Behavior |
|-------------|---------|-------------------|
| 200 | Success | 正常顯示資料 |
| 401 | Unauthorized | 顯示 "Jenkins 認證失敗" 錯誤 |
| 403 | Forbidden | 顯示 "無權限存取 Jenkins" 錯誤 |
| 404 | Not Found | Job 不存在，顯示警告 |
| 500 | Server Error | 顯示 "Jenkins 伺服器錯誤" |
| Connection Error | 無法連線 | 顯示快取資料 + 連線警告 |

---

## Security Considerations

1. **API Token 管理:**
   - 使用專用 Service Account
   - Token 僅需讀取權限
   - 定期輪換 Token（建議 6-12 個月）

2. **最小權限原則:**
   - Service Account 僅需 `Overall/Read` 和 `Job/Read` 權限
   - 不需要 Build、Configure 等權限

3. **網路安全:**
   - 使用 HTTPS 連線
   - 考慮使用 VPN 或內網存取
