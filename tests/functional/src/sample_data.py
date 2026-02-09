import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]  # tests/functional
TESTDATA_DIR = BASE_DIR / "testdata"


def _read(name: str) -> list[dict]:
    return json.loads((TESTDATA_DIR / name).read_text(encoding="utf-8-sig"))


FILMS = _read("films.json")
PERSONS = _read("persons.json")
GENRES = _read("genres.json")


def _id_of(obj: dict) -> str:
    return str(obj.get("id") or obj.get("uuid") or obj.get("_id"))


def film_id() -> str:
    return _id_of(FILMS[0])


def film_title() -> str:
    f = FILMS[0]
    return str(f.get("title") or f.get("name") or "")


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


def person_id_for_first_film() -> str:
    ids = _extract_person_ids_from_film(FILMS[0])
    if ids:
        return ids[0]
    return _id_of(PERSONS[0])


def genre_id() -> str:
    return _id_of(GENRES[0])


def search_phrase_from_first_film_title() -> str:
    title = film_title()
    words = re.findall(r"[A-Za-zА-Яа-я0-9]+", title)
    words = [w for w in words if len(w) >= 3]
    if not words:
        return "a"
    return max(words, key=len).lower()
