import argparse
import json
import re
from dataclasses import dataclass

import yaml
from PIL import Image, ImageDraw, ImageFont
from colorzero import Color, Hue
import seaborn as sns

import drawing
import filters
from drawer_context import DrawerContext

fnt12 = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 12)
fnt9 = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 9)

palette = sns.color_palette("tab10")


def draw_pin_text(ctx: DrawerContext, text, font, fill=(0, 0, 0)):
    x, y, w, h = font.getbbox(text)
    tmp = Image.new('RGBA', (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(tmp)
    d.text((0, 0), text, font=font, fill=fill)
    return tmp


def draw_pin_text_append(image, text, font, fill=(0, 0, 0)):
    x, y, w, h = font.getbbox(text)
    tmp = Image.new('RGBA', (image.size[0] + w, max(image.size[1], h)), (255, 255, 255, 255))
    d = ImageDraw.Draw(tmp)
    tmp.paste(im=image, box=(0, 0))
    d.text((image.size[0], 0), text, font=font, fill=fill)
    return tmp


def color_to_pillow(x: Color):
    return tuple((int(y * 255)) for y in x.rgb)


@dataclass
class PeripheralDesc:
    group_hash: int
    number: int

    @staticmethod
    def parse(name: str) -> 'PeripheralDesc':
        peripheral_group = name.split("_")[0]

        m = re.search(r"\d+$", peripheral_group)
        if m:
            peripheral_number = int(m.group())
            return PeripheralDesc(group_hash=sum(ord(x) for x in peripheral_group),
                                  number=peripheral_number)
        else:
            return PeripheralDesc(group_hash=0, number=0)


def create_pin_images(ctx: DrawerContext, pin: int):
    use_colors = ctx.cfg.get("color", False)

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
    if is_system_pin:
        text = pin_name
        fill = (255, 128, 0)
        outer_image = draw_pin_text(ctx, text, fnt12, fill=fill)
    else:
        signals = [x for x in pin_data["signals"] if ctx.filter_fn(x)]

        outer_image = Image.new('RGBA', (0, 0), (255, 255, 255, 255))
        is_first = True
        for s in signals:
            if use_colors:
                peripheral_desc = PeripheralDesc.parse(s)
                if peripheral_desc.group_hash == 0:
                    fill = (0, 0, 0)
                else:
                    peripheral_base_color = Color.from_rgb(*palette[peripheral_desc.group_hash % len(palette)])

                    fill = color_to_pillow(peripheral_base_color + Hue(0.05 * peripheral_desc.number))
            else:
                fill = (0, 0, 0)

            if not is_first:
                outer_image = draw_pin_text_append(outer_image, " / ", fnt12, fill=(0, 0, 0))
            outer_image = draw_pin_text_append(outer_image, s, fnt12, fill=fill)
            is_first = False

        if any(("ADC" in x and "_IN" in x) for x in pin_data["signals"]):
            if use_colors:
                fill = (200, 128, 0)
            else:
                fill = (0, 0, 0)
            outer_image = draw_pin_text_append(outer_image, " (A)", fnt12, fill=fill)

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
