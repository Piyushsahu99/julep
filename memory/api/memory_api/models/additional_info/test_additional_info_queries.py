# Tests for entry queries
from uuid import uuid4

from cozo_migrate.api import init, apply
from pycozo import Client
from ward import test

from .create_additional_info import create_additional_info_query
from .delete_additional_info import delete_additional_info_by_id_query
from .get_additional_info import get_additional_info_snippets_by_id_query
from .list_additional_info import list_additional_info_snippets_by_owner_query
from .search_additional_info import search_additional_info_snippets_by_embedding_query


def cozo_client(migrations_dir: str = "./migrations"):
    # Create a new client for each test
    # and initialize the schema.
    client = Client()

    init(client)
    apply(client, migrations_dir=migrations_dir, all_=True)

    return client


@test("create additional info")
def _():
    client = cozo_client()

    for owner_type in ("user", "agent"):
        owner_id = uuid4()
        id = uuid4()

        query = create_additional_info_query(
            owner_type, owner_id, id, title="Hello", content="World"
        )

        result = client.run(query)
        assert result["created_at"][0]


@test("get additional info")
def _():
    client = cozo_client()

    owner_type = "user"
    owner_id = uuid4()
    id = uuid4()

    create_query = create_additional_info_query(
        owner_type, owner_id, id, title="Hello", content="World"
    )

    client.run(create_query)

    query = get_additional_info_snippets_by_id_query(owner_type, id)

    result = client.run(query)
    assert len(result) == 1, "Only 1 should have been found"


@test("delete additional info")
def _():
    client = cozo_client()

    owner_type = "user"
    owner_id = uuid4()
    id = uuid4()

    create_query = create_additional_info_query(
        owner_type, owner_id, id, title="Hello", content="World"
    )

    client.run(create_query)

    query = delete_additional_info_by_id_query(owner_type, owner_id, id)

    result = client.run(query)
    delete_info = next(
        (row for row in result.to_dict("records") if row["_kind"] == "deleted"), None
    )

    assert delete_info is not None, "Delete operation found the row"


@test("list additional info")
def _():
    client = cozo_client()

    owner_type = "user"
    owner_id = uuid4()
    id = uuid4()

    create_query = create_additional_info_query(
        owner_type, owner_id, id, title="Hello", content="World"
    )

    client.run(create_query)

    query = list_additional_info_snippets_by_owner_query(owner_type, owner_id)

    result = client.run(query)
    assert len(result) == 1, "Only 1 should have been found"


@test("search additional info")
def _():
    client = cozo_client()

    owner_type = "user"
    owner_id = uuid4()
    id = uuid4()

    create_query = create_additional_info_query(
        owner_type, owner_id, id, title="Hello", content="World"
    )

    client.run(create_query)

    ### Add embedding to the snippet
    client.update(
        "information_snippets",
        dict(additional_info_id=str(id), snippet_idx=0, embedding=[1.0] * 768),
    )

    ### Search
    query_embedding = [0.99] * 768

    query = search_additional_info_snippets_by_embedding_query(
        owner_type,
        owner_id,
        query_embedding,
    )

    result = client.run(query)
    assert len(result) == 1, "Only 1 should have been found"