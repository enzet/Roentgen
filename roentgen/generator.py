"""Generate iconscript code."""

from pathlib import Path
from textwrap import dedent


def generate_bus_stops(config: dict) -> Path:
    """Generate iconscript code for bus stops."""
    variables: str = dedent("""
        sign =
            {w 2 s +0,0 +5,6}  # External.
            {w 2 r s +1,1 +3,3}  # Negative.
            {s +1.5,1.5 +2,1}  # Internal.
            {l +2.5,5.5 +0,5 l +-2,0 +4,0}  # Base.

        sign_small =
            {s +0,0 +4,5}  # Sign.
            {r s +1,1 +2,1}  # Negative.
            {l +2,4 +0,7}  # Base.

        platform = l +0,0 +13,0
        platform_center = l +0,0 +12,0
        cover = l 1,1 +13,0
        cover_center = l 1,1 +12,0
        wall = l 13,1 +0,13
        wall_short = {l 13,1 +0,9} {r l 12,10 +2,0}
        bench =
            {s +0,0 +9,1}  # Sit.
            {l +1,1 +0,2}  # Left leg.
            {l +8,1 +0,2}  # Right leg.
        bench_narrow =
            {s +-1,0 +5,1}
            {r l +-1,-1 +0,3}
            {l +3,1 +0,2}
        bin = lf +0,0 +3,0 +-1,3 +-1,0 +-1,-3

        lit =
            c +0,0 2  # Lamp.
            {l +0,2 +0,1.5}  # Central ray.
            {l +-2,1.5 +-1,1}  # Left ray.
            {l +2,1.5 +1,1}  # Right ray.

        lit_narrow =
            c +0,0 2  # Lamp.
            {l +-1,2 +-0.5,1.5}  # Left ray.
            {l +1,2 +0.5,1.5}  # Right ray.
        """)

    parameters: list[str] = [
        "bin",
        "bench",
        "cover",
        "lit",
        "platform",
        "shelter",
    ]
    result: str = ""
    for vector in range(2 ** len(parameters)):
        id_: str = "bus_stop"
        current_parameters: list[str] = []
        for i, parameter in enumerate(parameters):
            if vector & (1 << i):
                id_ += f"___{parameter}"
                current_parameters.append(parameter)

        is_bin: bool = "bin" in current_parameters
        is_bench: bool = "bench" in current_parameters
        is_cover: bool = "cover" in current_parameters
        is_lit: bool = "lit" in current_parameters
        is_platform: bool = "platform" in current_parameters
        is_shelter: bool = "shelter" in current_parameters

        if id_ in config["__transport_items"]:
            continue
        if is_cover and is_shelter:
            continue

        is_roof: bool = is_shelter or is_cover
        top_offset: float = 1 if is_roof else 0

        is_center: bool = not (is_bin or is_bench or is_shelter or is_lit)
        cover: str = "cover_center" if is_center else "cover"
        platform: str = "platform_center" if is_center else "platform"

        config["__transport_items"][id_] = {"name": id_, "sketch": True}

        code: str = f"icon {id_} = {{"
        if is_center:
            code += f"p 4.5,{2.5 + top_offset} @sign"
        else:
            code += f"p 1,{2 + top_offset} @sign_small"
        if is_bin:
            code += f" p 11,{10 + top_offset} @bin"
        if is_bench:
            code += (
                f" p 5,{10 + top_offset} @bench_narrow"
                if is_bin
                else f" p 5,{10 + top_offset} @bench"
            )
        if is_cover:
            code += f" @{cover}"
        if is_shelter:
            code += f" @{cover} @wall_short" if is_bin else f" @{cover} @wall"
        if is_lit:
            code += " p 9,1.5 @lit_narrow" if is_shelter else " p 11,1.5 @lit"
        if is_platform:
            code += f" p 1,{13 + top_offset} @{platform}"
        result += code + "}\n"

    directory: Path = Path("out") / "iconscript"
    directory.mkdir(parents=True, exist_ok=True)
    path: Path = directory / "bus_stop.iconscript"
    with path.open("w", encoding="utf-8") as file:
        file.write(variables + result)
    return path


def generate(_config: dict) -> list[Path]:
    """Generate iconscript code for all icons."""
    return []
