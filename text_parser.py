import re
pattern = r"\W*(?P<CanCollide>True|False)\w*\W+\w*(?P<CastShadow>True|False)\w*\D+(?P<Color>[ \-\d\.,]+)\W+?(?P<Material>\w+?)[vV]*\s+\D*(?P<Reflectance>[ \-\d\.,]+)\D+?(?P<Surface>\w+?)[vV]*\s+\D*(?P<Transparency>[ \-\d\.,]+)\D+?(?P<Position>[ \-\d\.,]+)\D+?(?P<Size>[ \-\d\.,]+)\D+?(?P<Rotation>[ \-\d\.,]+)\s+.*?(?P<Shape>\w+?)[vV]*\s+.*"

def parse_oc_image_text(text: str, for_csv: bool):
    """
    returns f"{csv_string}\\n" by default
    """

    res = re.match(pattern, text).groupdict()
    
    # making them the correct type
    res["CanCollide"] = bool(res["CanCollide"])
    res["CastShadow"] = bool(res["CastShadow"])
    res["Color"] = tuple(int(n) for n in res["Color"].split(',')[:3])
    res["Reflectance"] = float(res["Reflectance"])
    res["Transparency"] = float(res["Transparency"])
    res["Position"] = tuple(float(n) for n in res["Position"].split(',')[:3])
    res["Size"] = tuple(float(n) for n in res["Size"].split(',')[:3])
    res["Rotation"] = tuple(float(n) for n in res["Rotation"].split(',')[:3])
    if not for_csv: return res

    csv_tup = tuple([
        res["CanCollide"],
        res["CastShadow"],
        res["Color"][0], res["Color"][1], res["Color"][2],
        res["Material"],
        res["Reflectance"],
        res["Surface"],
        res["Transparency"],
        res["Position"][0], res["Position"][1], res["Position"][2],
        res["Size"][0], res["Size"][1], res["Size"][2],
        res["Rotation"][0], res["Rotation"][1], res["Rotation"][2],
        res["Shape"]
    ])
    return ','.join(map(str, csv_tup)) + "\n"