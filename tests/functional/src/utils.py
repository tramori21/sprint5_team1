import asyncio
import json
from pathlib import Path

from elasticsearch import AsyncElasticsearch
from elasticsearch import BadRequestError


BASE_DIR = Path(__file__).resolve().parents[1]  # tests/functional
TESTDATA_DIR = BASE_DIR / "testdata"


def _read_json(name: str) -> list[dict]:
    return json.loads((TESTDATA_DIR / name).read_text(encoding="utf-8-sig"))


def _id_of(obj: dict) -> str:
    return str(obj.get("id") or obj.get("uuid") or obj.get("_id"))


def _extract_person_ids_from_film(film: dict) -> list[str]:
    ids: list[str] = []

    def add(v):
        if v is None:
            return
        if isinstance(v, str):
            ids.append(v)
            return
        if isinstance(v, dict):
            pid = v.get("id") or v.get("uuid") or v.get("_id")
            if pid:
                ids.append(str(pid))
            return
        if isinstance(v, list):
            for x in v:
                add(x)

    for key in ("persons", "actors", "writers", "director", "directors"):
        add(film.get(key))

    seen = set()
    out: list[str] = []
    for x in ids:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


async def _wait_for_es(es: AsyncElasticsearch, timeout_s: int = 60) -> None:
    last_exc: Exception | None = None
    for _ in range(timeout_s):
        try:
            await es.info()
            return
        except Exception as e:
            last_exc = e
            await asyncio.sleep(1)
    if last_exc:
        raise last_exc


async def _recreate_index(es: AsyncElasticsearch, index: str, mappings: dict) -> None:
    await es.indices.delete(index=index, ignore_unavailable=True)

    for _ in range(40):
        exists = await es.indices.exists(index=index)
        if not exists:
            break
        await asyncio.sleep(0.5)

    try:
        await es.indices.create(index=index, mappings=mappings)
    except BadRequestError as e:
        if "resource_already_exists_exception" not in str(e):
            raise


async def load_data():
    es = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])
    try:
        await _wait_for_es(es)

        await _recreate_index(
            es,
            "movies",
            mappings={
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "persons": {"type": "keyword"},
                }
            },
        )
        await _recreate_index(
            es,
            "genres",
            mappings={
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                }
            },
        )
        await _recreate_index(
            es,
            "persons",
            mappings={
                "properties": {
                    "id": {"type": "keyword"},
                    "full_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                }
            },
        )

        films = _read_json("films.json")
        genres = _read_json("genres.json")
        persons = _read_json("persons.json")

        for doc in films:
            doc_id = _id_of(doc)
            doc["id"] = doc_id
            if "title" not in doc and "name" in doc:
                doc["title"] = doc["name"]
            doc["persons"] = _extract_person_ids_from_film(doc)
            await es.index(index="movies", id=doc_id, document=doc)

        for doc in genres:
            doc_id = _id_of(doc)
            doc["id"] = doc_id
            if "name" not in doc and "title" in doc:
                doc["name"] = doc["title"]
            await es.index(index="genres", id=doc_id, document=doc)

        for doc in persons:
            doc_id = _id_of(doc)
            doc["id"] = doc_id
            if "full_name" not in doc and "name" in doc:
                doc["full_name"] = doc["name"]
            await es.index(index="persons", id=doc_id, document=doc)

        await es.indices.refresh(index=["movies", "genres", "persons"])
    finally:
        await es.close()
