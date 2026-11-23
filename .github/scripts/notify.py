"""Firebase Cloud Messaging(HTTP v1)으로 토픽 알림을 보낸다.

환경 변수
    FIREBASE_SERVICE_ACCOUNT  서비스 계정 키 JSON 전체 (없으면 알림을 건너뜀)
    FCM_TOPIC                 보낼 토픽 (기본값: algo)
    NOTIFY_TITLE / NOTIFY_BODY / NOTIFY_URL
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request


def main() -> int:
    raw = os.environ.get("FIREBASE_SERVICE_ACCOUNT", "").strip()
    if not raw:
        print("FIREBASE_SERVICE_ACCOUNT가 없어서 알림을 건너뛰어요.")
        return 0

    from google.oauth2 import service_account  # pip install google-auth requests
    from google.auth.transport.requests import Request

    info = json.loads(raw)
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/firebase.messaging"])
    creds.refresh(Request())

    title = os.environ.get("NOTIFY_TITLE", "코테 분석")
    body = os.environ.get("NOTIFY_BODY", "")
    link = os.environ.get("NOTIFY_URL", "")
    message: dict = {
        "topic": os.environ.get("FCM_TOPIC") or "algo",
        "notification": {"title": title, "body": body},
        "data": {"url": link},
    }
    if link.startswith("https://"):
        message["webpush"] = {"fcm_options": {"link": link}}

    req = urllib.request.Request(
        f"https://fcm.googleapis.com/v1/projects/{info['project_id']}/messages:send",
        data=json.dumps({"message": message}).encode(),
        headers={"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        print("알림 전송:", res.read().decode())
    return 0


if __name__ == "__main__":
    sys.exit(main())
