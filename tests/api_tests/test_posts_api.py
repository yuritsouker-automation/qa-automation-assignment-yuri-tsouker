"""API tests for listing post resources and validating response contracts."""

import json
import os

from src.api import ApiClient

POSTS_PATH = "/posts"
EXPECTED_POSTS_COUNT = 100
REQUIRED_FIELDS = {"userId": int, "id": int, "title": str, "body": str}
POSTS_TEST_DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "test_data", "posts.json"
)

with open(POSTS_TEST_DATA_PATH) as f:
    _posts_test_data = json.load(f)


def test_get_posts_returns_200_json_array_and_expected_schema(api_client: ApiClient):
    """
    Validate GET /posts returns 200, a JSON array of expected length,
    and a sample item with required fields and types.
    """
    # 1. Send GET /posts request
    response = api_client.get(POSTS_PATH)

    # 2. Verify status code is 200
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # 3. Parse response and validate top-level array contract
    payload = response.json()
    assert isinstance(payload, list), f"Expected response body to be a list, got {type(payload).__name__}"
    assert len(payload) == EXPECTED_POSTS_COUNT, (
        f"Expected {EXPECTED_POSTS_COUNT} posts, got {len(payload)}"
    )

    # 4. Validate required fields and field types on a sample item
    first_item = payload[0]
    for field_name, expected_type in REQUIRED_FIELDS.items():
        assert field_name in first_item, f"Missing field '{field_name}' in response item"
        assert isinstance(first_item[field_name], expected_type), (
            f"Field '{field_name}' should be of type {expected_type.__name__}, "
            f"got {type(first_item[field_name]).__name__}"
        )


def test_list_all_resources_returns_json_array(api_client: ApiClient):
    """
    Validate listing all post resources returns 200 and a non-empty JSON array,
    where each item contains the required contract fields.
    """
    # 1. Send GET /posts request
    response = api_client.get(POSTS_PATH)

    # 2. Verify status code is 200
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # 3. Parse response JSON and verify list contract
    payload = response.json()
    assert isinstance(payload, list), f"Expected response body to be a list, got {type(payload).__name__}"
    assert len(payload) > 0, "Expected posts list to contain at least one resource"

    # 4. Validate required fields exist on each resource item
    for index, item in enumerate(payload):
        for field_name in REQUIRED_FIELDS:
            assert field_name in item, f"Item at index {index} is missing field '{field_name}'"


def test_get_post_by_valid_id_returns_200(api_client: ApiClient):
    """Validate GET /posts/{id} returns 200 for a valid resource id."""
    # 1. Send GET /posts/{valid_id} request
    response = api_client.get(f"{POSTS_PATH}/{_posts_test_data['valid_post_id']}")

    # 2. Verify status code is 200
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"


def test_get_post_by_non_existent_id_returns_404(api_client: ApiClient):
    """Validate GET /posts/{id} returns 404 for a non-existent resource id."""
    # 1. Send GET /posts/{non_existent_id} request
    response = api_client.get(f"{POSTS_PATH}/{_posts_test_data['non_existent_post_id']}")

    # 2. Verify status code is 404
    assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"


def test_create_post_returns_201_and_echoes_payload(api_client: ApiClient):
    """Validate POST /posts returns 201, echoes payload fields, and includes a generated id."""
    # 1. Load create payload and send POST /posts request
    payload = _posts_test_data["create_post_payload"]
    response = api_client.post(
        POSTS_PATH,
        json=payload,
        headers={"Content-type": "application/json; charset=UTF-8"},
    )

    # 2. Verify status code is 201
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"

    # 3. Verify response echoes payload and includes generated id
    body = response.json()
    assert body["title"] == payload["title"], "Response title should echo request payload"
    assert body["body"] == payload["body"], "Response body should echo request payload"
    assert body["userId"] == payload["userId"], "Response userId should echo request payload"
    assert "id" in body, "Response should include generated 'id'"
    assert isinstance(body["id"], int), f"Expected generated id as int, got {type(body['id']).__name__}"
    assert body["id"] > 0, "Generated id should be a positive integer"


def test_update_post_returns_200_and_echoes_payload(api_client: ApiClient):
    """Validate PUT /posts/{id} returns 200 and echoes the full updated payload."""
    # 1. Load update payload and send PUT /posts/{id} request
    payload = _posts_test_data["update_post_payload"]
    post_id = payload["id"]
    response = api_client.put(
        f"{POSTS_PATH}/{post_id}",
        json=payload,
        headers={"Content-type": "application/json; charset=UTF-8"},
    )

    # 2. Verify status code is 200
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # 3. Verify response echoes the full update payload
    body = response.json()
    assert body["id"] == post_id, f"Response id should be {post_id}, got {body.get('id')}"
    assert body["title"] == payload["title"], "Response title should echo request payload"
    assert body["body"] == payload["body"], "Response body should echo request payload"
    assert body["userId"] == payload["userId"], "Response userId should echo request payload"


def test_delete_post_returns_200_or_204_with_empty_body(api_client: ApiClient):
    """
    Validate DELETE /posts/{id} returns 200 (or 204) and an empty response body.
    Note: writes are simulated by JSONPlaceholder; persistence is not asserted.
    """
    # 1. Send DELETE /posts/{id} request
    post_id = _posts_test_data["delete_post_id"]
    response = api_client.delete(f"{POSTS_PATH}/{post_id}")

    # 2. Verify status code is either 200 or 204
    assert response.status_code in (200, 204), (
        f"Expected status code 200 or 204, got {response.status_code}"
    )

    # 3. Verify response body is empty (simulated writes)
    body = response.json()
    assert body == {}, f"Expected empty response body after delete, got {body}"
