import argparse
import json

import yaml
from PIL import Image, ImageDraw, ImageFont

import drawing
import filters
from drawer_context import DrawerContext

fnt12 = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 12)
fnt9 = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 9)


def draw_pin_text(ctx: DrawerContext, text, font, fill=(0, 0, 0)):
    x, y, w, h = font.getbbox(text)
    tmp = Image.new('RGBA', (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(tmp)
    d.text((0, 0), text, font=font, fill=fill)
    return tmp


def create_pin_images(ctx: DrawerContext, pin: int):
    pin = (pin - 1) % ctx.pins_count + 1

    pin_data = ctx.pin_by_pos[pin]
    pin_name = pin_data["name"]

    is_system_pin = pin_data["type"] in ("Power", "Boot", "Reset")

    # inner image
    if is_system_pin:
        text = str(pin)
    else:
        text = str(pin) + " | " + pin_name

    inner_image = draw_pin_text(ctx, text, fnt9)

    # outer image
    signals = " / ".join(x for x in pin_data["signals"] if ctx.filter_fn(x))

    fill = (0, 0, 0)
    if is_system_pin:
        text = pin_name
        fill = (255, 128, 0)
    else:
        text = signals

    if any(("ADC" in x and "_IN" in x) for x in pin_data["signals"]):
        text = text + " (A)"

    outer_image = draw_pin_text(ctx, text, fnt12, fill=fill)

    return {
        "inner_image": inner_image,
        "outer_image": outer_image,
    }


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-c', '--config', default="config.yaml", type=str, metavar="PATH")
    argparser.add_argument('-o', '--output', default="output.png", type=str, metavar="PATH")
    args = argparser.parse_args()

    cfg = yaml.load(open(args.config, "rt"), Loader=yaml.SafeLoader)

    filter_fn = filters.create_filter_func_array(cfg["filters"])

    mcu_data = json.load(open(cfg["pinout"], "rt"))

    package = mcu_data["package"]

    if not package.startswith(("LQFP",)):
        print(f"Unsupported package {package}")
        exit(1)

    ctx = DrawerContext()
    ctx.cfg = cfg
    ctx.pins_count = len(mcu_data["pinout"])
    ctx.pin_by_pos = {int(x["position"]): x for x in (mcu_data["pinout"])}
    ctx.image = Image.new("RGB", (cfg["drawing"]["image_size_w"], cfg["drawing"]["image_size_h"]), (255, 255, 255, 0))
    ctx.create_pin_images = create_pin_images
    ctx.filter_fn = filter_fn
    drawing.draw(ctx)
    ctx.image.save(args.output)


main()
