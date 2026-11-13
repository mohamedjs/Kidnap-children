"""Tiny HTTP client for the seed and the smoke test. Uploads use the real presigned flow:
ask the api for a PUT URL, PUT the bytes straight to the bucket, confirm."""

from typing import Any

import httpx


class ApiError(RuntimeError):
    def __init__(self, status: int, body: Any) -> None:
        super().__init__(f"{status}: {body}")
        self.status, self.body = status, body


class Api:
    def __init__(self, base_url: str, token: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.http = httpx.Client(base_url=self.base_url, timeout=30)
        self.token = token

    def as_user(self, token: str) -> "Api":
        return Api(self.base_url, token)

    def call(self, method: str, path: str, json: Any = None, params: Any = None, expect: int | None = None) -> Any:
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        res = self.http.request(method, path, json=json, params=params, headers=headers)
        body = res.json() if res.content and "json" in res.headers.get("content-type", "") else None
        if expect is not None and res.status_code != expect:
            raise ApiError(res.status_code, body)
        if expect is None and res.status_code >= 400:
            raise ApiError(res.status_code, body)
        return body["data"] if isinstance(body, dict) and "data" in body else body

    def login(self, email: str, password: str) -> "Api":
        return self.as_user(self.call("POST", "/api/auth/login", {"email": email, "password": password})["token"])

    def request_upload(self, data: bytes, content_type: str, purpose: str, name: str = "photo.jpg",
                       declared: int | None = None) -> dict[str, Any]:
        result: dict[str, Any] = self.call("POST", "/api/uploads", {
            "purpose": purpose, "content_type": content_type, "size": declared or len(data), "filename": name})
        return result

    @staticmethod
    def put(ticket: dict[str, Any], data: bytes, content_type: str | None = None) -> httpx.Response:
        headers = dict(ticket["headers"])
        if content_type:
            headers["Content-Type"] = content_type
        return httpx.put(ticket["url"], content=data, headers=headers, timeout=30)

    def upload(self, data: bytes, content_type: str = "image/jpeg", purpose: str = "report_photo",
               name: str = "photo.jpg") -> str:
        ticket = self.request_upload(data, content_type, purpose, name)
        res = self.put(ticket, data)
        if res.status_code not in (200, 201, 204):
            raise ApiError(res.status_code, res.text[:300])
        self.call("POST", f"/api/uploads/{ticket['upload_id']}/confirm")
        return str(ticket["upload_id"])
