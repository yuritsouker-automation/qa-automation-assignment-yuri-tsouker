"""
test_utils/assertions.py
------------------------
Reusable assertion helpers for the QA automation suite.

Design goals
~~~~~~~~~~~~
* **Grep-able failure messages** – every failure line starts with a
  SCREAMING_SNAKE_CASE tag (e.g. ``STATUS_CODE_MISMATCH``) so you can
  search CI logs with a single string.
* **Expected-vs-actual clarity** – each helper surfaces both expected
  and actual values in a structured block:
      FIELD_TYPE_MISMATCH | field='id' | expected=int | actual=str | item={'id': '1', ...}
* **Zero magic** – helpers are plain functions; no custom test
  framework required.  Any pytest ``assert`` failure is immediately
  actionable.
"""

from __future__ import annotations

from typing import Any

import requests


# ---------------------------------------------------------------------------
# HTTP response assertions
# ---------------------------------------------------------------------------

def assert_status_code(response: requests.Response, expected: int) -> None:
    """Assert an HTTP response carries the expected status code.

    Failure tag: ``STATUS_CODE_MISMATCH``

    Example failure message::

        STATUS_CODE_MISMATCH | url=https://jsonplaceholder.typicode.com/posts/99999
          expected=404 | actual=200
    """
    actual = response.status_code
    assert actual == expected, (
        f"STATUS_CODE_MISMATCH | url={response.url}\n"
        f"  expected={expected} | actual={actual}"
    )


def assert_status_code_in(response: requests.Response, expected: tuple[int, ...]) -> None:
    """Assert an HTTP response status code is one of the allowed values.

    Failure tag: ``STATUS_CODE_NOT_IN_ALLOWED``

    Example failure message::

        STATUS_CODE_NOT_IN_ALLOWED | url=https://jsonplaceholder.typicode.com/posts/1
          allowed=(200, 204) | actual=500
    """
    actual = response.status_code
    assert actual in expected, (
        f"STATUS_CODE_NOT_IN_ALLOWED | url={response.url}\n"
        f"  allowed={expected} | actual={actual}"
    )


def assert_json_array(payload: Any, *, context: str = "response body") -> None:
    """Assert a parsed JSON payload is a list.

    Failure tag: ``PAYLOAD_NOT_ARRAY``

    Example failure message::

        PAYLOAD_NOT_ARRAY | context=response body | actual_type=dict
    """
    assert isinstance(payload, list), (
        f"PAYLOAD_NOT_ARRAY | context={context} | actual_type={type(payload).__name__}"
    )


def assert_non_empty(collection: list[Any], *, context: str = "collection") -> None:
    """Assert a collection is not empty.

    Failure tag: ``EMPTY_COLLECTION``

    Example failure message::

        EMPTY_COLLECTION | context=posts list | length=0
    """
    assert len(collection) > 0, (
        f"EMPTY_COLLECTION | context={context} | length={len(collection)}"
    )


def assert_array_length(
    payload: list[Any], expected_length: int, *, context: str = "response body"
) -> None:
    """Assert a JSON array has an exact expected length.

    Failure tag: ``ARRAY_LENGTH_MISMATCH``

    Example failure message::

        ARRAY_LENGTH_MISMATCH | context=response body | expected=100 | actual=99
    """
    assert_json_array(payload, context=context)
    actual = len(payload)
    assert actual == expected_length, (
        f"ARRAY_LENGTH_MISMATCH | context={context} | expected={expected_length} | actual={actual}"
    )


# ---------------------------------------------------------------------------
# Schema / contract assertions
# ---------------------------------------------------------------------------

def assert_field_present(item: dict[str, Any], field: str, *, index: int | None = None) -> None:
    """Assert a required field exists in a response object.

    Failure tag: ``MISSING_FIELD``

    Example failure message::

        MISSING_FIELD | field='userId' | index=3 | item={'id': 4, 'title': 'foo'}
    """
    index_info = f" | index={index}" if index is not None else ""
    assert field in item, (
        f"MISSING_FIELD | field='{field}'{index_info} | item={item}"
    )


def assert_field_type(
    item: dict[str, Any],
    field: str,
    expected_type: type,
    *,
    index: int | None = None,
) -> None:
    """Assert a field value is of the expected Python type.

    Failure tag: ``FIELD_TYPE_MISMATCH``

    Example failure message::

        FIELD_TYPE_MISMATCH | field='id' | expected=int | actual=str
          | index=0 | item={'id': '1', 'title': 'foo', ...}
    """
    assert_field_present(item, field, index=index)
    actual_type = type(item[field])
    index_info = f" | index={index}" if index is not None else ""
    assert isinstance(item[field], expected_type), (
        f"FIELD_TYPE_MISMATCH | field='{field}'"
        f" | expected={expected_type.__name__} | actual={actual_type.__name__}"
        f"{index_info} | item={item}"
    )


def assert_schema(
    item: dict[str, Any],
    required_fields: dict[str, type],
    *,
    index: int | None = None,
) -> None:
    """Assert all required fields exist and have the correct types.

    ``required_fields`` maps field name → expected Python type, e.g.::

        {"userId": int, "id": int, "title": str, "body": str}

    Failure tags: ``MISSING_FIELD``, ``FIELD_TYPE_MISMATCH``
    """
    for field, expected_type in required_fields.items():
        assert_field_type(item, field, expected_type, index=index)


def assert_all_items_have_fields(
    items: list[dict[str, Any]],
    required_fields: dict[str, type] | set[str],
    *,
    context: str = "items",
) -> None:
    """Assert every item in a list contains all required fields (and correct types
    when ``required_fields`` is a ``dict``).

    Failure tags: ``MISSING_FIELD``, ``FIELD_TYPE_MISMATCH``
    """
    if isinstance(required_fields, set):
        # presence-only check
        for index, item in enumerate(items):
            for field in required_fields:
                assert_field_present(item, field, index=index)
    else:
        for index, item in enumerate(items):
            assert_schema(item, required_fields, index=index)


# ---------------------------------------------------------------------------
# Resource echo assertions (create / update round-trips)
# ---------------------------------------------------------------------------

def assert_field_equals(
    item: dict[str, Any],
    field: str,
    expected: Any,
    *,
    context: str = "response body",
) -> None:
    """Assert a field value equals an expected value.

    Failure tag: ``FIELD_VALUE_MISMATCH``

    Example failure message::

        FIELD_VALUE_MISMATCH | field='title' | context=response body
          expected='foo' | actual='bar' | item={'id': 1, 'title': 'bar', ...}
    """
    assert_field_present(item, field)
    actual = item[field]
    assert actual == expected, (
        f"FIELD_VALUE_MISMATCH | field='{field}' | context={context}\n"
        f"  expected={expected!r} | actual={actual!r} | item={item}"
    )


def assert_payload_echoed(
    response_body: dict[str, Any],
    sent_payload: dict[str, Any],
    fields: list[str] | None = None,
    *,
    context: str = "response body",
) -> None:
    """Assert the server echoed back every field from the sent payload.

    :param fields: Subset of payload keys to check.  When *None* all keys are
                   checked.

    Failure tag: ``FIELD_VALUE_MISMATCH``
    """
    keys_to_check = fields if fields is not None else list(sent_payload.keys())
    for field in keys_to_check:
        expected = sent_payload[field]
        assert_field_equals(response_body, field, expected, context=context)


def assert_auto_generated_id(
    response_body: dict[str, Any], *, field: str = "id", context: str = "response body"
) -> None:
    """Assert the server responded with a positive integer auto-generated id.

    Failure tags: ``MISSING_FIELD``, ``FIELD_TYPE_MISMATCH``, ``INVALID_AUTO_ID``

    Example failure message::

        INVALID_AUTO_ID | field='id' | context=response body | value=0
          (expected a positive integer)
    """
    assert_field_type(response_body, field, int)
    value = response_body[field]
    assert value > 0, (
        f"INVALID_AUTO_ID | field='{field}' | context={context} | value={value}\n"
        f"  (expected a positive integer)"
    )


def assert_empty_body(
    response_body: Any, *, context: str = "response body after delete"
) -> None:
    """Assert a response body is an empty dict (simulated-write APIs often return ``{}``).

    Failure tag: ``NON_EMPTY_RESPONSE_BODY``

    Example failure message::

        NON_EMPTY_RESPONSE_BODY | context=response body after delete | body={'id': 1}
    """
    assert response_body == {}, (
        f"NON_EMPTY_RESPONSE_BODY | context={context} | body={response_body}"
    )

