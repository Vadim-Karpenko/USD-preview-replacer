from pxr import Usd # Make sure to run `pip install usd-core` to install dependencies


def get_texture_path(material, attr_name):
    """
    If the material has a texture attribute with the given name, return the path to the texture.
    
    :param attr_name: The name of the attribute you want to get the texture path from
    :return: The path to the texture file.
    """
    material_value = material.GetAttribute(attr_name).Get()
    if material_value and material_value.__class__.__name__ == "AssetPath":
        path = material_value.path
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
    material_name = material.GetName()
    material_value = material.GetAttribute(attr_name).Get()
    path = material_value.path

    if material_value:
        if "DiffuseColorTex" in material_name:
            return "base_color", path
        elif "NormalTex" in material_name:
            return "normal", path
        elif "MetallicTex" in material_name:
            return "metallic", path
        elif "RoughnessTex" in material_name:
            return "roughness", path
        elif "SpecularColorTex" in material_name:
            return "specular", path
        elif "EmissiveColorTex" in material_name:
            return "emissive", path
        elif "OpacityMaskTex" in material_name:
            return "opacity", path


def replace_matches(usd_text, preview_value, main_value):
    """
    If the main value is not empty, replace the preview value with the main value
    
    :param usd_text: The text of the USD file
    :param preview_value: The value that is currently in the USD file
    :param main_value: The value that will be used to replace the preview_value
    :return: the usd_text variable.
    """
    if main_value and preview_value:
        usd_text = usd_text.replace(preview_value, main_value)
    return usd_text
    
    

def replace_preview_maps(file_name):
    """
    It opens the USD file, finds all the materials, and replaces the preview textures with the main
    textures
    
    :param file_name: The path to the USD file you want to replace the preview maps in
    """
    stage_ref = Usd.Stage.Open(file_name)

    looks = stage_ref.GetPrimAtPath('/Root/Looks').GetChildren()
    with open(file_name) as f:
        usd_text=f.read()
        for look in looks:
            materials = look.GetChildren()
            material_data = {
                "main": {
                    "base_color": {},
                    "normal": {},
                    "metallic": {},
                    "roughness": {},
                    "specular": {},
                    "emissive": {},
                    "opacity": {},
                },
                "preview": {
                    "base_color": {},
                    "normal": {},
                    "metallic": {},
                    "roughness": {},
                    "specular": {},
                    "emissive": {},
                    "opacity": {},
                }
            }

            for material in materials:
                material_type = material.GetAttribute("info:id").Get()

                if material_type == None:
                    material_data["main"]["base_color"] = get_texture_path(material, "inputs:Albedo")

                    material_data["main"]["normal"] = get_texture_path(material, "inputs:Normal")

                    material_data["main"]["roughness"] = get_texture_path(material, "inputs:Roughness_tp")

                    material_data["main"]["metallic"] = get_texture_path(material, "inputs:Metallic")
                elif material_type == "UsdUVTexture":
                    mat_type, path = get_preview_texture_path(material)
                    material_data["preview"][mat_type] = path

            for key, texture_data in material_data["main"].items():
                if material_data["preview"][key] and texture_data:
                    usd_text = replace_matches(usd_text, material_data["preview"][key], texture_data)
    with open(file_name, "w") as f:
        f.write(usd_text)



if __name__ == "__main__":
    print("Make sure that the file is located in the same directory as this script")
    file_name = input("Please enter name of your usda file (e.g example.usda): ")
    replace_preview_maps(file_name)

        
