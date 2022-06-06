import re

from .utils import convert_texture_path_to_absolute


# Parse Nvidia MDL file to get original texture maps from it
def parse_mdl(mdl_file):
    """
    It reads the mdl file and finds all the texture maps and their variable names. Then it reads the
    file again and finds the type of the texture based on the variable name
    
    :param mdl_file: The path to the .mdl file
    :return: A list of dictionaries.
    """
    parsed_raw = []
    texture_types = {
        "BaseColor_mdl": "base_color",
        "Normal_mdl": "normal",
        "Metallic_mdl": "metallic",
        "Roughness_mdl": "roughness",
        "AmbientOcclusion_mdl": "ao",
        "Emissive_mdl": "emissive",
        "Opacity_mdl": "opacity",
        "Specular_mdl": "specular",
    }
    # Open file
    with open(mdl_file, 'r') as f:
        # Read file
        lines = f.readlines()
        
        # Get texture maps and their variable names
        for line in lines:
            # Find using re module string that is located between "texture_2d\(\"" and "\",::" which is our texture map
            texture_map = re.findall(r'texture_2d\(\"(.*?)\",::', line)
            texture_variable_name = re.search(r'float4 (.*?) =|uniform texture_2d (.*?) =', line)
            if texture_variable_name and texture_map:
                texture_variable_name = texture_variable_name[0].replace("float4 ", "").replace("uniform texture_2d ", "").replace(" =", "")
                parsed_raw.append({'variable_name': texture_variable_name, 'texture_map': convert_texture_path_to_absolute(mdl_file, texture_map[0])})

        # Read lines again and get texture types based on their variable names
        for line in lines:
            # loop through collected textures from above
            for texture_data in parsed_raw:
                if texture_data["variable_name"] in line:
                    # For most cases this is more than enough to distinguish the texture type, just based on the variable name
                    if texture_data["variable_name"].lower() in ["albedo", "basecolor", "color", "diffuse", "base_color"]:
                        texture_data["type"] = "base_color"
                    elif texture_data["variable_name"].lower() in ["normal", "normalmap", "normal_map"]:
                        texture_data["type"] = "normal"
                    elif texture_data["variable_name"].lower() in ["emissive", "emissivemap", "emissive_map", "emmisive", "emmisivemap", "emmisive_map"]:
                        texture_data["type"] = "emissive"
                    elif texture_data["variable_name"].lower() in ["metallic", "metallicmap", "metallic_map"]:
                        texture_data["type"] = "metallic"
                    elif texture_data["variable_name"].lower() in ["roughness", "roughnessmap", "roughness_map"]:
                        texture_data["type"] = "roughness"
                    elif texture_data["variable_name"].lower() in ["opacity", "opacitymap", "opacity_map"]:
                        texture_data["type"] = "opacity"
                    elif texture_data["variable_name"].lower() in ["ao", "aomap", "ao_map"]:
                        texture_data["type"] = "ao"
                    elif texture_data["variable_name"].lower() in ["specular", "specularmap", "specular_map"]:
                        texture_data["type"] = "specular"
                    else:
                        # if float3 is present it means that it is a texture file
                        if "float3" in line:
                            # UE mdl files have same pattern for float textures, we can use it to determine the type of the texture
                            for texture_type, type_name in texture_types.items():
                                if texture_type in line:
                                    texture_data["type"] = texture_types[texture_type]
                                    break
                            else:
                                # Some mdl files does operations on the texture along the way, so we need to get
                                # the new variable name until we find the texture type old one with the 
                                # new one on each loop.
                                new_texture_variable_name = re.findall(r'float3 (.*?) =', line)
                                if new_texture_variable_name:
                                    texture_data["variable_name"] = new_texture_variable_name[0]
                        elif "lookup_float4" in line:
                            new_texture_variable_name = re.findall(r'float4 (.*?) =', line)
                            if new_texture_variable_name:
                                texture_data["variable_name"] = new_texture_variable_name[0]
                        else:
                            custom_texture_mapping = {
                                "x": None,
                                "y": None,
                                "z": None,
                            }
                            is_has_custom_mapping = False
                            is_variables_instead_of_mapping = False
                            for key, value in custom_texture_mapping.items():
                                # Check if the texture is a custom texture mapping by going through all three possible keys (x, y, z)
                                if f"{texture_data['variable_name']}.{key}" in line:
                                    # UE mdl files have same pattern for float textures, we can use it to determine the type of the texture
                                    for texture_type, type_name in texture_types.items():
                                        if texture_type in line:
                                            custom_texture_mapping[key] = texture_types[texture_type]
                                            # to make sure that we won't save empty custom_texture_mapping into the object
                                            is_has_custom_mapping = True
                                        else:
                                            # Same as above, but for mapped textures, they have slightly different structure
                                            new_texture_variable_name = re.findall(r'float (.*?) =', line)
                                            if new_texture_variable_name:
                                                custom_texture_mapping[key] = new_texture_variable_name[0]
                                                is_has_custom_mapping = True
                                                texture_data["is_variables_instead_of_mapping"] = True
                                        
                            if is_has_custom_mapping:
                                if "custom_texture_mapping" in texture_data:
                                    if custom_texture_mapping["x"] is not None:
                                        texture_data["custom_texture_mapping"]["x"] = custom_texture_mapping["x"]
                                    if custom_texture_mapping["y"] is not None:
                                        texture_data["custom_texture_mapping"]["y"] = custom_texture_mapping["y"]
                                    if custom_texture_mapping["z"] is not None:
                                        texture_data["custom_texture_mapping"]["z"] = custom_texture_mapping["z"]
                                else:
                                    texture_data["custom_texture_mapping"] = custom_texture_mapping
                                # texture_data["custom_texture_mapping"] = custom_texture_mapping
                
    # We'll read file again in case if we found a texture that contains custom mapping (e.g rgb that contains 3 maps at once)
    for texture_data in parsed_raw:
        # if custom_texture_mapping is present and not False
        if "is_variables_instead_of_mapping" in texture_data and texture_data["is_variables_instead_of_mapping"]:
            # loop through xyz keys
            for key, value in texture_data["custom_texture_mapping"].items():
                # loop through lines again
                for line in lines:
                    # if the line contains the unique name of the texture (e.g Normal_mdl) AND the variable of the custom_texture_mapping
                    if texture_data["custom_texture_mapping"][key] and texture_data["custom_texture_mapping"][key] in line:
                        for texture_type, type_name in texture_types.items():
                            if texture_type in line:
                                # Replace the key (where we stored variable name for mapped texture) with the type of the texture
                                texture_data["custom_texture_mapping"][key] = texture_types[texture_type]
    
    result = {}
    for texture_data in parsed_raw:
        # Remove the variable name from the list because we don't really need this info elsewhere
        if "custom_texture_mapping" in texture_data:
            for key, value in texture_data["custom_texture_mapping"].items():
                result[value] = {"texture_map": texture_data["texture_map"], "channel": key}
        else:
            if "type" in texture_data:
                result[texture_data["type"]] = {"texture_map": texture_data["texture_map"]}
    return result
