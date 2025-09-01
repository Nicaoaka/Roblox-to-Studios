import re

PATTERN =\
r"""[\s\d.,]*(?P<CanCollide>[a-zA-Z]+)[ \d.,]*?
[\s\d.,]*(?P<CastShadow>[a-zA-Z]+)[ \d.,]*?
[\s\D]*?(?P<Color>[AT \-\d\.,]+)[ \D]*?
[\s\d.,]*(?P<Material>[\w\d ]+?) *?[vV]*[ ]*?
[\s\D]*?(?P<Reflectance>[AT \-\d\.,]+)[\s\D]*?
[\s\d.,]*(?P<SurfaceType>[\w\d ]+?) *?[vV]*[ ]*?
[\s\D]*?(?P<Transparency>[AT \-\d\.,]+)[\sa-zA-Z]*?
[\s\D]*?(?P<Position>[AT \-\d\.,]+)[\sa-zA-Z]*?
[\s\D]*?(?P<Size>[AT \-\d\.,]+)[\sa-zA-Z]*?
[\s\D]*?(?P<Orientation>[AT \-\d\.,]+)[\sa-zA-Z]*?
[\s,.]*(?P<PartType>[\w\d ]+?) *?[vV]*[ ]*?
(?P<Rest>[\w\s,\.-]*)"""

PARTTYPE: set[str] = {
    "Ball", "Block", "Cylinder", "Wedge", "CornerWedge" # TrussPart (edge case)
}

SURFACETYPE: set[str] = {
    "Smooth", "Glue", "Weld", "Studs", "Inlet", "Universal", "Hinge", 
    "Motor", "SteppingMotor", "SmoothNoOutlines"
}

MATERIAL: set[str] = {
    "Plastic", "SmoothPlastic", "Neon", "Wood", "WoodPlanks", "Marble", "Slate", "Concrete", "Granite",
    "Brick", "Pebble", "Cobblestone", "Rock", "Sandstone", "Basalt", "CrackedLava", "Limestone", "Pavement",
    "CorrodedMetal", "DiamondPlate", "Foil", "Metal", "Grass", "LeafyGrass", "Sand", "Fabric", "Snow", "Mud",
    "Ground", "Asphalt", "Salt", "Ice", "Glacier", "Glass", "ForceField", "Air", "Water", "Cardboard", "Carpet",
    "CeramicTiles", "ClayRoofTiles", "RoofShingles", "Leather", "Plaster", "Rubber"
}

# trusses will have a Style unlike all other parts
TRUSS_INSTANCE_NAME = "TrussPart"
TRUSS_STYLES: dict[str, str] = {
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
    # loose comparison
    if "tru" in string.lower():
        return True
    elif "fal" in string.lower():
        return False
    
    uncertainties[field_name] = repr(string)
    return DEFUALTS[field_name]

def to_float(string: str, field_name: str, uncertainties: dict) -> float:

    if string and string[0] == '.':
        uncertainties[field_name] = repr(string)
        string = string[1:]
    else:
        try:
            return round(float(string), 3)
        except Exception: # ValueError / TypeError
            pass
        uncertainties[field_name] = repr(string)

    # OCR misinterpretations
    # A -> -4
    # -A -> --4 -> -4
    # T -> 7
    string = string.replace('A', '-4')
    string = string.replace('--', '-')
    string = string.replace('T', '7')

    if len(string) == 0:
        return DEFUALTS[field_name]
    # Remove additional decimal points beyond the first valid one
    if string.count(".") >= 2:
        first = string.find(".")
        string = string[:first + 1] + string[first + 1:].replace(".", "")

    try:
        return round(float(string), 3)
    except Exception: # ValueError
        return DEFUALTS[field_name]

def to_int(string: str, field_name: str, uncertainties: dict) -> int:
    
    if string and string[0] == '.':
        uncertainties[field_name] = repr(string)
        string = string[1:]
    else:
        try:
            return int(string)
        except Exception: # ValueError / TypeError
            pass
        uncertainties[field_name] = repr(string)

    uncertainties[field_name] = repr(string)

    # OCR misinterpretations
    string = string.replace('A', '-4')
    string = string.replace('T', '7')
    string = string.replace(".", "")

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
    string = string.strip()
    parts = string.split(',')
    
    if len(parts) < size:
        uncertainties[field_name] = "LOW "+repr(string)
        parts = string.split(',') + [""] * (size - len(parts))

    elif len(parts) > size:
        uncertainties[field_name] = "HIGH "+repr(string)
        if string[0] == ',':
            string  = string[1:]
        if string[-1] == ',':
            string  = string[:-1]
        
        # 1,111,2.222,3.333 -> 1.111,2.222,3.333
        num_elements = string.count(',') + 1
        if num_elements > size:
            string = string.replace(',', '.', 1)
        
        num_elements = string.count(',') + 1
        parts = string.split(',')[:3] + [""] * (size - num_elements)

    return [convert_fn(part, f"{field_name}_{i+1}", uncertainties)
            for i, part in enumerate(parts)]



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

def parse_image_text(text: str) -> dict[str, str|dict|list]:
    text += "\n" # for regex pattern
    regex_match = re.match(PATTERN, text)
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
    part_data["Name"] = part_data["PartType"]
    if uncertainties.get("PartType"):
        part_data["Name"] = "Unknown"
        for style in TRUSS_STYLES.keys():
            if style in data["Rest"].lower():
                del part_data["PartType"]
                del uncertainties["PartType"]
                part_data["Instance"] = TRUSS_INSTANCE_NAME
                part_data["Name"] = TRUSS_INSTANCE_NAME
                part_data["Style"] = TRUSS_STYLES[style]
                break
    part_data["Uncertainties"] = uncertainties
    return part_data


def to_delimeted(json_data: dict, delimter: str) -> str:
    part_data = [
        json_data["Name"],
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
    uncertainties = [f"{field_name} = {recieve}" for field_name, recieve in json_data["Uncertainties"].items()]
    fields = part_data + uncertainties
    if any([delimter in field for field in fields]):
        raise ValueError(f"Delimeter: '{delimter}' cannot be used.")
    return delimter.join(fields) + "\n"
