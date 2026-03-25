import argparse
import json
import re
from dataclasses import dataclass

import yaml
import drawsvg
from colorzero import Color, Hue
import seaborn as sns

import drawing
import drawing_TSSOP
import filters
from drawer_context import DrawerContext
import myutils

fnt9 = dict(font_size=9, font_family='DejaVu Sans')
fnt12 = dict(font_size=12, font_family='DejaVu Sans')

palette = sns.color_palette("tab10")


def color_to_tuple(x: Color):
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
    pin_name = "/".join(x["name"] for x in pin_data)

    is_system_pin = any(x["type"] in ("Power", "Boot", "Reset") for x in pin_data)

    # inner image
    if is_system_pin:
        text = str(pin)
    else:
        text = str(pin) + " | " + pin_name

    inner_txt = drawsvg.Text('', x=0, y=0, dominant_baseline='middle', **fnt9)
    inner_txt.append(drawsvg.TSpan(text))

    all_signals = [y for x in pin_data for y in x["signals"]]

    outer_txt = drawsvg.Text('', x=0, y=0, dominant_baseline='middle', **fnt12)

    # outer image
    if is_system_pin:
        text = pin_name
        fill = (255, 128, 0)
        outer_txt.append(drawsvg.TSpan(text, fill=f"rgb({fill[0]},{fill[1]},{fill[2]})"))
    else:
        signals = [x for x in all_signals if ctx.filter_fn(x)]

        is_first = True
        for s in signals:
            if use_colors:
                peripheral_desc = PeripheralDesc.parse(s)
                if peripheral_desc.group_hash == 0:
                    fill = (0, 0, 0)
                else:
                    peripheral_base_color = Color.from_rgb(*palette[peripheral_desc.group_hash % len(palette)])

                    fill = color_to_tuple(peripheral_base_color + Hue(0.05 * peripheral_desc.number))
            else:
                fill = (0, 0, 0)

            if not is_first:
                outer_txt.append(drawsvg.TSpan(" / ", fill="black"))
            outer_txt.append(drawsvg.TSpan(s, fill=f"rgb({fill[0]},{fill[1]},{fill[2]})"))
            is_first = False

        if any(("ADC" in x and "_IN" in x) for x in all_signals):
            if use_colors:
                fill = (200, 128, 0)
            else:
                fill = (0, 0, 0)
            outer_txt.append(drawsvg.TSpan(" (A)", fill=f"rgb({fill[0]},{fill[1]},{fill[2]})"))

    return {
        "inner_txt": inner_txt,
        "outer_txt": outer_txt,
    }


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-c', '--config', default="config.yaml", type=str, metavar="PATH")
    argparser.add_argument('-o', '--output', default="output.svg", type=str, metavar="PATH")
    args = argparser.parse_args()

    cfg = yaml.load(open(args.config, "rt"), Loader=yaml.SafeLoader)

    filter_fn = filters.create_filter_func_array(cfg["filters"])

    mcu_data = json.load(open(cfg["pinout"], "rt"))

    package = mcu_data["package"]

    if not package.startswith(("LQFP", "TSSOP")):
        print(f"Unsupported package {package}")
        exit(1)

    d = drawsvg.Drawing(cfg["drawing"]["image_size_w"], cfg["drawing"]["image_size_h"])
    d.append(drawsvg.Rectangle(0, 0, '100%', '100%', fill='white'))

    ctx = DrawerContext()
    ctx.cfg = cfg
    ctx.pin_by_pos = myutils.groupby(mcu_data["pinout"], key=lambda x: int(x["position"]))
    ctx.pins_count = len(ctx.pin_by_pos)
    ctx.image = d
    ctx.create_pin_images = create_pin_images
    ctx.filter_fn = filter_fn
    if package.startswith("LQFP"):
        drawing.draw(ctx)
    if package.startswith("TSSOP"):
        drawing_TSSOP.draw(ctx)
    d.save_svg(args.output)


main()
