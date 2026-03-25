from typing import Dict, Any, Callable

import drawsvg


class DrawerContext:
    cfg: Any
    pins_count: int
    pin_by_pos: Dict[int, Any]
    image: drawsvg.Drawing
    create_pin_images: Callable[['DrawerContext', int], Dict[str, Any]]
    filter_fn: Callable[[str], bool]
