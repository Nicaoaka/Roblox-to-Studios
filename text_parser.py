import re
pattern =\
r"""[\s\d.,]*(?P<CanCollide>[a-zA-Z]+)[ \d.,]*?
[\s\d.,]*(?P<CastShadow>[a-zA-Z]+)[ \d.,]*?
[\s\D]*?(?P<Color>[A \-\d\.,]+)[ \D]*?
[\s\d.,]*(?P<Material>[a-zA-Z]+?) *?[vV]*[ ]*?
[\s\D]*?(?P<Reflectance>[A \-\d\.,]+)[\s\D]*?
[\s\d.,]*(?P<SurfaceType>[a-zA-Z]+?) *?[vV]*[ ]*?
[\s\D]*?(?P<Transparency>[A \-\d\.,]+)[\sa-zA-Z]*?
[\s\D]*?(?P<Position>[A \-\d\.,]+)[\sa-zA-Z]*?
[\s\D]*?(?P<Size>[A \-\d\.,]+)[\sa-zA-Z]*?
[\s\D]*?(?P<Orientation>[A \-\d\.,]+)[\sa-zA-Z]*?
[\s,.]*(?P<PartType>[\w]+?)\s*[vV]*[ ,.]*?
(?P<Rest>[\w\s]*)"""

PARTTYPE = {
    "Ball", "Block", "Cylinder", "Wedge", "CornerWedge" # TrussPart (edge case)
}

SURFACETYPE = {
    "Smooth", "Glue", "Weld", "Studs", "Inlet", "Universal", "Hinge", 
    "Motor", "SteppingMotor", "SmoothNoOutlines"
}

MATERIAL = {
    "Plastic", "SmoothPlastic", "Neon", "Wood", "WoodPlanks", "Marble", "Slate", "Concrete", "Granite",
    "Brick", "Pebble", "Cobblestone", "Rock", "Sandstone", "Basalt", "CrackedLava", "Limestone", "Pavement",
    "CorrodedMetal", "DiamondPlate", "Foil", "Metal", "Grass", "LeafyGrass", "Sand", "Fabric", "Snow", "Mud",
    "Ground", "Asphalt", "Salt", "Ice", "Glacier", "Glass", "ForceField", "Air", "Water", "Cardboard", "Carpet",
    "CeramicTiles", "ClayRoofTiles", "RoofShingles", "Leather", "Plaster", "Rubber"
}

# trusses will have a Style unlike all other parts
TRUSS_INSTANCE_NAME = "TrussPart"
TRUSS_STYLES = {
    "alternating": "AlternatingSupports",   # Alternating
    "bridgestyle": "BridgeStyleSupports",   # Bridge Style
    "nosupports": "NoSupports",             # No Supports

    # LOOSER
    "alt": "AlternatingSupports",          # Alternating
    "bri": "BridgeStyleSupports",          # Bridge Style
    "osu": "NoSupports",                   # No Supports
}

DEFUALTS = {
    'Instance': "Part",
    'CanCollide': True,
    'CastShadow': True,
    'Color_1': 255,
    'Color_2': 255,
    'Color_3': 255,
    'Material': 'Plastic',
    'Reflectance': 0,
    'SurfaceType': 'Studs',
    'Transparency': 0,
    'Position_1': 0,
    'Position_2': 0,
    'Position_3': 0,
    'Size_1': 1,
    'Size_2': 1,
    'Size_3': 1,
    'Orientation_1': 0,
    'Orientation_2': 0,
    'Orientation_3': 0,
    'PartType': 'Block'
}

def to_bool(string: str, field_name: str, uncertainties: dict) -> bool:
    string = string.strip()
    if "true" in string.lower():
        return True
    elif "false" in string.lower():
        return False
    
    uncertainties[field_name] = repr(string)
    return DEFUALTS[field_name]

def to_float(string: str, field_name: str, uncertainties: dict) -> float:
    try:
        return float(string)
    except Exception: # ValueError / TypeError
        pass

    uncertainties[field_name] = repr(string)

    if len(string) == 0:
        return DEFUALTS[field_name]
    
    # OCR misinterpretation: "-4" as "A"
    if string[0] == "A":
        string = "-4" + string[1:]

    # Remove additional decimal points beyond the first valid one
    if string.count(".") >= 2:
        first = string.find(".")
        string = string[:first + 1] + string[first + 1:].replace(".", "")

    try:
        return float(string)
    except Exception: # ValueError
        return DEFUALTS[field_name]

def to_int(string: str, field_name: str, uncertainties: dict) -> int:
    try:
        return int(string)
    except ValueError:
        pass

    uncertainties[field_name] = repr(string)
    
    string.replace(".", "")
    try:
        return int(string)
    except ValueError:
        pass
    return DEFUALTS[field_name]

def to_enum(string: str, enum: set[str], field_name: str, uncertainties: dict) -> str:
    string = string.strip()
    if string in enum:
        return string
    
    # Case-insensitive matching
    lower_enum = {e.lower(): e for e in enum}
    if string.lower() in lower_enum.keys():
        return lower_enum[string.lower()]
    
    uncertainties[field_name] = repr(string)
    return DEFUALTS[field_name]

def to_vector(string: str, size: int, convert_fn, field_name: str, uncertainties: dict) -> list[str]:
    parts = string.split(',')
    
    if len(parts) < size:
        uncertainties[field_name] = "LOW "+repr(string)
        parts += [""] * (size - len(parts))
    elif len(parts) > size:
        uncertainties[field_name] = "HIGH "+repr(string)
        parts = parts[:size]

    return [convert_fn(dimension, f"{field_name}_{i+1}", uncertainties)
            for i, dimension in enumerate(parts)]


FIELD_METADATA = {
    "CanCollide":   {"type": "bool"},
    "CastShadow":   {"type": "bool"},
    "Color":        {"type": "vector", "size": 3, "convert_fn": to_int},
    "Material":     {"type": "enum", "enum": MATERIAL},
    "Reflectance":  {"type": "float"},
    "Transparency": {"type": "float"},
    "SurfaceType":  {"type": "enum", "enum": SURFACETYPE},
    "Position":     {"type": "vector", "size": 3, "convert_fn": to_float},
    "Size":         {"type": "vector", "size": 3, "convert_fn": to_float},
    "Orientation":  {"type": "vector", "size": 3, "convert_fn": to_float},
    "PartType":     {"type": "enum", "enum": PARTTYPE},
}

def parse_image_text(text: str) -> list[dict, dict]:
    text += "\n" # for regex pattern
    regex_match = re.match(pattern, text)
    if not regex_match:
        raise ValueError("Failed to parse input text: " + repr(text))
    data = regex_match.groupdict()
    data = {key: str(value) for key, value in data.items()}

    part_data = dict()
    uncertainties = dict()
    for field in FIELD_METADATA.keys():

        match(FIELD_METADATA[field]["type"]):
            case "bool":
                part_data[field] = to_bool(data[field], field, uncertainties)
            case "float":
                part_data[field] = to_float(data[field], field, uncertainties)
            case "enum":
                enum = FIELD_METADATA[field]["enum"]
                part_data[field] = to_enum(data[field], enum, field, uncertainties)
            case "vector":
                size = FIELD_METADATA[field]["size"]
                convert_fn = FIELD_METADATA[field]["convert_fn"]
                part_data[field] = to_vector(data[field], size, convert_fn, field, uncertainties)
    

    # Truss edge case
    #   Instance
    #   PartType -> Style
    # Note: There isn't a good way to do meshes (they all look the same in properties)
    part_data["Instance"] = DEFUALTS["Instance"] # Default Instance Type
    if uncertainties.get("PartType"):
        for style in TRUSS_STYLES.keys():
            if style in data["Rest"].lower():
                del part_data["PartType"]
                del uncertainties["PartType"]
                part_data["Instance"] = TRUSS_INSTANCE_NAME
                part_data["Style"] = TRUSS_STYLES[style]
                break

    return part_data, uncertainties



def to_delimeted(json_data: dict, uncertainties: dict, delimter: str):
    part_data = [
        json_data["Instance"],
        json_data["CanCollide"],
        json_data["CastShadow"],
        json_data["Color"][0], json_data["Color"][1], json_data["Color"][2],
        json_data["Material"],
        json_data["Reflectance"],
        json_data["SurfaceType"],
        json_data["Transparency"],
        json_data["Position"][0], json_data["Position"][1], json_data["Position"][2],
        json_data["Size"][0], json_data["Size"][1], json_data["Size"][2],
        json_data["Orientation"][0], json_data["Orientation"][1], json_data["Orientation"][2],
        json_data.get("PartType") or json_data.get("Style")
    ]
    
    part_data = list(map(str, part_data))
    uncertainties = [f"{field_name} = {recieve}" for field_name, recieve in uncertainties.items()]
    fields = part_data + uncertainties
    if any([delimter in field for field in fields]):
        raise ValueError(f"Delimeter: '{delimter}' cannot be used.")
    return delimter.join(fields) + "\n"
