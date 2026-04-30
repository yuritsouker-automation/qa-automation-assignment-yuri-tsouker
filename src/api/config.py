from dataclasses import dataclass


@dataclass(frozen=True)
class ApiConfig:
    base_url: str
    timeout: float

    def build_url(self, path: str) -> str:
        normalized_path = path if path.startswith("/") else f"/{path}"
        return f"{self.base_url.rstrip('/')}{normalized_path}"

