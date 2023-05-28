from typing import Dict, Any, Callable


class DrawerContext:
    cfg: Any
    pins_count: int
    pin_by_pos: Dict[int, Any]
    image: Any
    create_pin_images: Callable[['DrawerContext', int], Dict[str, Any]]
    filter_fn: Callable[[str], bool]
