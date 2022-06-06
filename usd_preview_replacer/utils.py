from pathlib import Path

def convert_texture_path_to_absolute(mdl_file, texture_path):
    """
    It converts the texture path to absolute path
    
    :param
    :return:
    """
    mdl_file_path = Path(mdl_file)
    mdl_file_path = mdl_file_path.parent
    mdl_file_path = str(mdl_file_path) + texture_path.replace("./", "/").replace("/", "\\")
    return mdl_file_path


def get_texture_path(material, attr_names):
    """
    It returns the path of the texture assigned to the material using attribute name
    
    :param material: The material you want to get the texture path from
    :param attr_name: The name of the attribute you want to get the texture path from
    :return: The path to the texture file.
    """
    for attr_name in attr_names:
        material_value = material.GetAttribute(attr_name).Get()
        if material_value and material_value.__class__.__name__ == "AssetPath":
            path = material_value.resolvedPath
            return path


def get_preview_texture_path(material, attr_name="inputs:file"):
    """
    It takes a material and an attribute name, and returns a tuple of the material's type and the path
    to the texture file
    
    :param material: The material you want to get the texture path from
    :param attr_name: The name of the attribute that contains the texture path, defaults to inputs:file
    (optional)
    :return: the material name, the material value, and the path.
    """
    material_name = material.GetName().lower()
    material_value = material.GetAttribute(attr_name).Get()
    path = material_value.resolvedPath

    if material_value:
        if "diffuse" in material_name:
            return "base_color", path
        elif "normal" in material_name:
            return "normal", path
        elif "metallic" in material_name:
            return "metallic", path
        elif "roughness" in material_name:
            return "roughness", path
        elif "specular" in material_name:
            return "specular", path
        elif "emissive" in material_name:
            return "emissive", path
        elif "opacity" in material_name:
            return "opacity", path