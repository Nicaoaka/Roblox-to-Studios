import re
pattern = r"\W*(?P<CanCollide>[a-zA-Z]+)\s+(?P<CastShadow>[a-zA-Z]+)\D+(?P<Color>[ \-\d\.,]+)\W+?(?P<Material>[a-zA-Z]+?)[vV]*\s+\D*(?P<Reflectance>[ \-\d\.,]+)\D+?(?P<SurfaceType>[a-zA-Z]+?)[vV]*\s+\D*(?P<Transparency>[ \-\d\.,]+)\D+?(?P<Position>[ \-\d\.,]+)\D+?(?P<Size>[ \-\d\.,]+)\D+?(?P<Orientation>[ \-\d\.,]+)\s+.*?(?P<PartType>[a-zA-Z]+?)[vV]*\s+.*"

PARTTYPE = {
    "Ball", "Block", "Cylinder", "Wedge", "CornerWedge"
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

DEFUALTS = {
    'CanCollide': True,
    'CastShadow': True,
    'Color_R': 255,
    'Color_G': 255,
    'Color_B': 255,
    'Material': 'Plastic',
    'Reflectance': 0,
    'SurfaceType': 'Studs',
    'Transparency': 0,
    'Position_X': 0,
    'Position_Y': 0,
    'Position_Z': 0,
    'Size_X': 1,
    'Size_Y': 1,
    'Size_Z': 1,
    'Orientation_X': 0,
    'Orientation_Y': 0,
    'Orientation_Z': 0,
    'PartType': 'Block'
}

_DEFUALTS = {
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
    return _DEFUALTS[field_name]

def to_float(string: str, field_name: str, uncertainties: dict) -> float:
    try:
        return float(string)
    except Exception: # ValueError / TypeError
        pass

    uncertainties[field_name] = repr(string)

    if len(string) == 0:
        return _DEFUALTS[field_name]
    
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
        return _DEFUALTS[field_name]

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
    return _DEFUALTS[field_name]

def to_enum(string: str, enum: set[str], field_name: str, uncertainties: dict) -> str:    
    string = string.strip()
    if string == enum:
        return string
    
    # Case-insensitive matching
    lower_enum = {e.lower(): e for e in enum}
    if string.lower() in lower_enum:
        return lower_enum[string.lower()]
    
    uncertainties[field_name] = repr(string)
    return _DEFUALTS[field_name]

def to_vector(string: str, size: int, convert_fn, field_name: str, uncertainties: dict) -> tuple[str]:
    parts = string.split(',')
    
    if len(parts) < size:
        uncertainties[field_name] = f"LOW '{parts}'"
        parts += [""] * (size - len(parts))
    elif len(parts) > size:
        uncertainties[field_name] = f"HIGH '{parts}'"
        parts = parts[:size]

    return tuple(convert_fn(p, f"{field_name}_{i}", uncertainties) for i, p in enumerate(parts))


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

def parse_image_text(text: str) -> tuple[dict, dict]:
    regex_match = re.match(pattern, text)
    if not regex_match:
        raise ValueError("Failed to parse input text: " + repr(text))
    part_data = regex_match.groupdict()

    uncertainties = dict()
    for field in FIELD_METADATA:

        match(FIELD_METADATA[field]["type"]):
            case "bool":
                part_data[field] = to_bool(part_data[field], field, uncertainties)
            case "float":
                part_data[field] = to_float(part_data[field], field, uncertainties)
            case "enum":
                enum = FIELD_METADATA[field]["enum"]
                part_data[field] = to_enum(part_data[field], enum, field, uncertainties)
            case "vector":
                size = FIELD_METADATA[field]["size"]
                convert_fn = FIELD_METADATA[field]["convert_fn"]
                part_data[field] = to_vector(part_data[field], size, convert_fn, field, uncertainties)
    
    return part_data, uncertainties



def parse_oc_image_text(text: str) -> tuple[dict, dict]:

    uncertainties: dict[str: str] = dict()
    # scripts to attatch to part
    # format:
    #   "field_name" = "recieved"

    # inner function so they can change uncertainties directly
    def to_bool(value: str | None, field_name: str) -> bool:
        """
        Converts a stirng to a bool.
        """
        on_failure = None if not field_name else DEFUALTS[field_name]
        try:
            value = value.strip()
            if "true" in value.lower():
                return True
            elif "false" in value.lower():
                return False
        except Exception: # AttributeError (from None)
            pass
        if field_name:
            uncertainties[field_name] = repr(value)
        return on_failure

    def to_float(value: str | None, field_name: str) -> float:
        """
        Converts a string to a float, handling OCR errors and formatting issues.
        """
        on_failure = None if not field_name else DEFUALTS[field_name]
        try:
            return float(value)
        except Exception: # ValueError / TypeError
            pass
        
        if field_name:
            uncertainties[field_name] = repr(value)

        if not value:
            return on_failure

        # OCR misinterpretation: "-4" as "A"
        if value[0] == "A":
            value = "-4" + value[1:]

        # Remove additional decimal points beyond the first valid one
        if value.count(".") >= 2:
            first = value.find(".")
            value = value[:first + 1] + value[first + 1:].replace(".", "")

        try:
            return float(value)
        except Exception: # ValueError
            return on_failure

    def to_int(value: str | None, field_name: str) -> int:
        """
        Converts a string to an integer, will process as a float if necessary.
        """
        on_failure = None if not field_name else DEFUALTS[field_name]
        try:
            return int(value)
        except Exception: # ValueError / TypeError
            if field_name:
                uncertainties[field_name] = repr(value)

        float_value = to_float(value, field_name="")
        if float_value is not None:
            return round(float_value) # Rounds only if conversion succeeds
        return on_failure
    
    def valid_Enum(value: str | None, Enum: set[str], field_name: str):
        on_failure = None if not field_name else DEFUALTS[field_name]
        if not value:
            if field_name:
                uncertainties[field_name] = repr(value)
            return on_failure
        
        value = value.strip()
        if value in Enum:
            return value
        # Case-insensitive matching
        lower_enum = {e.lower(): e for e in Enum}
        if value.lower() in lower_enum:
            return lower_enum[value.lower()]
        if field_name:
            uncertainties[field_name] = repr(value)
        return on_failure

    def split_null_normalized(value: str | None, delimeter: str, to_size: int, field_name: str) -> tuple:
        if not value:
            if field_name:
                uncertainties[field_name] = "NONE "+repr(value)
            return tuple([None] * (to_size - len(array)))

        array = value.split(delimeter)

        if len(array) == to_size:
            return tuple(array)
        
        if len(array) >= to_size:
            if field_name:
                uncertainties[field_name] = "HIGH "+repr(value)
            return tuple(array[:to_size])
        else:
            if field_name:
                uncertainties[field_name] = "LOW "+repr(value)
            return tuple(array + [None] * (to_size - len(array)))

    match = re.match(pattern, text)
    if not match:
        raise ValueError("Failed to parse input text: " + repr(text))
    res = match.groupdict()
    
    res["CanCollide"] = to_bool(res["CanCollide"], "CanCollide")
    res["CastShadow"] = to_bool(res["CastShadow"], "CastShadow")

    res["Reflectance"] = to_float(res["Reflectance"], "Reflectance")
    res["Transparency"] = to_float(res["Transparency"], "Transparency")    

    res["Material"] = valid_Enum(res["Material"], MATERIAL, "Material")
    res["SurfaceType"] = valid_Enum(res["SurfaceType"], SURFACETYPE, "SurfaceType")
    res["PartType"] = valid_Enum(res["PartType"], PARTTYPE, "PartType")

    r, g, b = split_null_normalized(res["Color"], ',', 3, "Color")
    res["Color"] = tuple([
            to_int(r, "Color_R"),
            to_int(g, "Color_G"), 
            to_int(b, "Color_B")
        ])

    x, y, z = split_null_normalized(res["Position"], ',', 3, "Position")
    res["Position"] = tuple([
            to_float(x, "Position_X"),
            to_float(y, "Position_Y"), 
            to_float(z, "Position_Z")
        ])

    x, y, z = split_null_normalized(res["Size"], ',', 3, "Size")
    res["Size"] = tuple([
            to_float(x, "Size_X"),
            to_float(y, "Size_Y"), 
            to_float(z, "Size_Z")
        ])
    
    x, y, z = split_null_normalized(res["Orientation"], ',', 3, "Orientation")
    res["Orientation"] = tuple([
            to_float(x, "Orientation_X"),
            to_float(y, "Orientation_Y"), 
            to_float(z, "Orientation_Z")
        ])
    
    # if uncertainties:
    #     with open("ParseUncertanties.txt", 'a') as f:
    #         import json
    #         f.write(f"{'-'*100}\n\"\"\"{text}\"\"\",\n")
    #         f.write(f"Parsed to:\n{json.dumps(res, indent=4, sort_keys=False)}\n\n")
    
    return res, uncertainties



def to_delimeted(json_data: dict, uncertainties: dict, delimter: str):
    part_data = [
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
        json_data["PartType"]
    ]
    part_data = list(map(str, part_data))
    uncertainties = [f"{field_name} = {recieve}" for field_name, recieve in uncertainties.items()]
    fields = part_data + uncertainties
    if any([delimter in field for field in fields]):
        raise ValueError(f"Delimeter: '{delimter}' cannot be used.")
    return delimter.join(fields) + "\n"
