from typing import TypeVar, Iterable, Callable, List, Dict

T = TypeVar("T")
TKey = TypeVar("TKey")
TProject = TypeVar("TProject")
TProjectGroup = TypeVar("TProjectGroup")


def groupby(items: Iterable[T], key: Callable[[T], TKey],
            project_item: Callable[[T], TProject] = lambda x: x,
            project_group: Callable[[List[TProject]], TProjectGroup] = lambda x: x) \
        -> Dict[TKey, TProjectGroup]:
    data = {}  # type: Dict[TKey,List[TProject]]
    for x in items:
        item_key = key(x)
        if item_key not in data:
            data[item_key] = []
        data[item_key].append(project_item(x))
    datap = {key: project_group(items) for key, items in data.items()}
    return datap
