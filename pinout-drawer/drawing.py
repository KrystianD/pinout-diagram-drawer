from typing import Dict, Any

from PIL import ImageDraw

from drawer_context import DrawerContext

text_margin = 8
text_margin2 = 10


def draw_point(image, xy, fill):
    d = ImageDraw.Draw(image)
    w = 2
    d.ellipse((xy[0] - w, xy[1] - w, xy[0] + w, xy[1] + w), fill=fill)


def draw_pad(ctx: DrawerContext, xy):
    draw_point(ctx.image, xy, fill=(0, 0, 0))


def draw_pin_left(ctx: DrawerContext, xy, images: Dict[str, Any]):
    draw_pad(ctx, xy)

    w = images["inner_image"].rotate(0, expand=True)
    s = w.size
    xy2 = (xy[0] + text_margin, xy[1] - s[1] // 2)
    ctx.image.paste(im=w, box=xy2)

    w = images["outer_image"].rotate(0, expand=True)
    s = w.size
    xy2 = (xy[0] - s[0] - text_margin, xy[1] - s[1] // 2)
    ctx.image.paste(im=w, box=xy2)


def draw_pin_bottom(ctx: DrawerContext, xy, images):
    draw_pad(ctx, xy)

    w = images["inner_image"].rotate(90, expand=True)
    s = w.size
    xy2 = (xy[0] - s[0] // 2, xy[1] - s[1] - text_margin)
    ctx.image.paste(im=w, box=xy2)

    w = images["outer_image"].rotate(90, expand=True)
    s = w.size
    xy2 = (xy[0] - s[0] // 2, xy[1] + text_margin)
    ctx.image.paste(im=w, box=xy2)


def draw_pin_right(ctx: DrawerContext, xy, images):
    draw_pad(ctx, xy)

    w = images["inner_image"].rotate(0, expand=True)
    s = w.size
    xy2 = (xy[0] - s[0] - text_margin, xy[1] - s[1] // 2)
    ctx.image.paste(im=w, box=xy2)

    w = images["outer_image"].rotate(0, expand=True)
    s = w.size
    xy2 = (xy[0] + text_margin, xy[1] - s[1] // 2)
    ctx.image.paste(im=w, box=xy2)


def draw_pin_top(ctx: DrawerContext, xy, images):
    draw_pad(ctx, xy)

    w = images["inner_image"].rotate(90, expand=True)
    s = w.size
    xy2 = (xy[0] - s[0] // 2, xy[1] + text_margin)
    ctx.image.paste(im=w, box=xy2)

    w = images["outer_image"].rotate(90, expand=True)
    s = w.size
    xy2 = (xy[0] - s[0] // 2, xy[1] - s[1] - text_margin)
    ctx.image.paste(im=w, box=xy2)


def draw(ctx: DrawerContext):
    die_size = ctx.pins_count * ctx.cfg["drawing"]["die_size"]

    d = ImageDraw.Draw(ctx.image)

    center_x = ctx.image.size[0] // 2
    center_y = ctx.image.size[1] // 2
    l = center_x - die_size / 2
    t = center_y - die_size / 2
    r = center_x + die_size / 2
    b = center_y + die_size / 2

    rotate = ctx.cfg["rotate"] % 4

    die_mark_size = 20
    die_points = [
        [l + die_mark_size, t, r, t, r, b, l, b, l, t + die_mark_size],
        [l, t, r - die_mark_size, t, r, t + die_mark_size, r, b, l, b],
        [l, t, r, t, r, b - die_mark_size, r - die_mark_size, b, l, b],
        [l, t, r, t, r, b, l + die_mark_size, b, l, b - die_mark_size],
    ]
    d.polygon(die_points[rotate], outline=(0, 0, 0))

    die_margin = ctx.cfg["drawing"]["die_margin"]

    pin_per_side = ctx.pins_count // 4
    for i in range(pin_per_side):
        pin = i + 1

        pins_distance = (die_size - die_margin * 2) / (pin_per_side + 1)
        pin_pos_offset = pin * pins_distance

        pin_num_offset = pin_per_side * rotate

        pin_xy = (int(center_x - die_size / 2), int(center_y - die_size / 2 + pin_pos_offset + die_margin))
        pin_images = ctx.create_pin_images(ctx, pin + pin_num_offset)
        draw_pin_left(ctx, pin_xy, pin_images)

        pin_xy = (int(center_x - die_size / 2 + pin_pos_offset + die_margin), int(center_y + die_size / 2))
        pin_images = ctx.create_pin_images(ctx, pin + pin_per_side + pin_num_offset)
        draw_pin_bottom(ctx, pin_xy, pin_images)

        pin_xy = (int(center_x + die_size / 2), int(center_y - die_size / 2 + pin_pos_offset + die_margin))
        pin_images = ctx.create_pin_images(ctx, pin_per_side * 3 - pin + 1 + pin_num_offset)
        draw_pin_right(ctx, pin_xy, pin_images)

        pin_xy = (int(center_x - die_size / 2 + pin_pos_offset + die_margin), int(center_y - die_size / 2))
        pin_images = ctx.create_pin_images(ctx, pin_per_side * 4 - pin + 1 + pin_num_offset)
        draw_pin_top(ctx, pin_xy, pin_images)
