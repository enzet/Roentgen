"""Generate iconscript code."""

from pathlib import Path


def generate_bus_stops(config: dict) -> Path:
    """Generate iconscript code for bus stops."""
    variables: str = Path("iconscript/stop_variables.iconscript").read_text()

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

        if (
            id_ in config["__transport_items"]
            or id_ in config["__transport_items"]["__traffic_sign"]
        ):
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
