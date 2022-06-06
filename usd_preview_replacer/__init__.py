# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess
import sys
from pathlib import Path

import bpy
import pip

from .parse_mdl import parse_mdl
from .utils import get_preview_texture_path, get_texture_path


bl_info = {
    "name" : "USD-preview-replacer",
    "author" : "Vadim Karpenko",
    "description" : "",
    "blender" : (3, 1, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}


class OmniversePreviewReplaceSelected(bpy.types.Operator):
    """Replace the preview maps with the main maps to improve texture quality"""
    bl_idname = "opr.replace_selected_previews"
    bl_label = "Omniverse Replace Selected Previews"
    bl_options = {'REGISTER', 'UNDO'}

    def process_looks(self, looks, scene_context):
        """
        It takes a list of USD materials, and returns a dictionary of material names and their corresponding
        texture maps
        
        :param looks: The list of looks to process
        :param scene_context: This is the context of the scene. It contains the following parameters:
        :return: A dictionary of material names and their associated data.
        """
        result = {}
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
                    "ao": {},
                },
                "preview": {
                    "base_color": {},
                    "normal": {},
                    "metallic": {},
                    "roughness": {},
                    "specular": {},
                    "emissive": {},
                    "opacity": {},
                    "ao": {},
                }
            }
            material_name = ""
            for material in materials:
                material_type = material.GetAttribute("info:id").Get()
                mdl_file = material.GetAttribute("info:mdl:sourceAsset").Get()
                if mdl_file:
                    mdl_material_data = parse_mdl(mdl_file.resolvedPath)

                if material_type == None:
                    material_name = material.GetName()
                    if scene_context.is_diffuse_selected:
                        allowed_params = ["inputs:Albedo", "inputs:BaseColor", "inputs:Diffuse", "inputs:albedo", "inputs:baseColor", "inputs:diffuse"]
                        material_data["main"]["base_color"] = get_texture_path(material, allowed_params) or mdl_material_data.get("base_color", {}).get("texture_map")
                    if scene_context.is_normal_selected:
                        allowed_params = ["inputs:Normal", "inputs:normal"]
                        material_data["main"]["normal"] = get_texture_path(material, allowed_params) or mdl_material_data.get("normal", {}).get("texture_map")
                    if scene_context.is_roughness_selected:
                        allowed_params = ["inputs:Roughness", "inputs:roughness", "inputs:Roughness_tp", "inputs:roughness_tp"]
                        material_data["main"]["roughness"] = get_texture_path(material, allowed_params) or mdl_material_data.get("roughness", {}).get("texture_map")
                    if scene_context.is_metallic_selected:
                        allowed_params = ["inputs:Metallic", "inputs:metallic"]
                        material_data["main"]["metallic"] = get_texture_path(material, allowed_params) or mdl_material_data.get("metallic", {}).get("texture_map")
                    if scene_context.is_specular_selected:
                        allowed_params = ["inputs:Specular", "inputs:specular"]
                        material_data["main"]["specular"] = get_texture_path(material, allowed_params) or mdl_material_data.get("specular", {}).get("texture_map")
                    if scene_context.is_emissive_selected:
                        allowed_params = ["inputs:Emissive", "inputs:emissive", "inputs:EmissiveColor", "inputs:emissiveColor"]
                        material_data["main"]["emissive"] = get_texture_path(material, allowed_params) or mdl_material_data.get("emissive", {}).get("texture_map")
                    if scene_context.is_opacity_selected:
                        allowed_params = ["inputs:Opacity", "inputs:opacity", "inputs:Opacity_map", "inputs:opacity_map"]
                        material_data["main"]["opacity"] = get_texture_path(material, allowed_params) or mdl_material_data.get("opacity", {}).get("texture_map")
                    if scene_context.is_ao_selected:
                        allowed_params = ["inputs:AO", "inputs:ao", "inputs:AO_map", "inputs:ao_map", "inputs:AmbientOcclusion", "inputs:ambientOcclusion"]
                        material_data["main"]["ao"] = get_texture_path(material, allowed_params) or mdl_material_data.get("ao")
                elif material_type == "UsdUVTexture":
                    mat_type, path = get_preview_texture_path(material)
                    material_data["preview"][mat_type] = path
            if material_name:
                result[material_name] = material_data
        return result
    
    def get_usd_materials_from_references(self, stage_ref, scene_context, selected_objs):
        """
        It takes a list of objects, and returns a dictionary of all the materials used by those objects
        
        :param stage_ref: The stage reference
        :param scene_context: The scene context is a dictionary that contains information about the
        scene
        :param selected_objs: A list of objects that are selected in the scene
        :return: A dictionary of materials.
        """
        allowed_materials = {}
        for obj in selected_objs:
            if obj.type == "MESH":
                for mat_slot in obj.material_slots:
                    if mat_slot.material:
                        if "." in mat_slot.material.name:
                            material_name = mat_slot.material.name.split(".")[0]
                        else:
                            material_name = mat_slot.material.name
                        if material_name:
                            allowed_materials[material_name] = ""

        result = {}
        level_objects = stage_ref.GetPrimAtPath('/Root').GetChildren()
        for obj in level_objects:
            looks = obj.GetPrimAtPath("Looks").GetChildren()
            result.update(self.process_looks(looks, scene_context))
        return result

    def get_usd_materials_from_looks(self, stage_ref, scene_context):
        """
        It takes a stage reference and a scene context, and returns a list of USD materials
        
        :param stage_ref: The stage reference that you're currently working with
        :param scene_context: This is the context of the scene. It's a dictionary that contains the
        following keys:
        :return: A list of materials.
        """
        looks = stage_ref.GetPrimAtPath('/Root/Looks').GetChildren()
        return self.process_looks(looks, scene_context)
        


    def execute(self, context):
        if not context.scene.usd_file_path:
            return None

        if context.scene.usd_replace_selected:
            selected_objs = context.selected_objects
        else:
            scene = context.scene
            # Get all objects in the scene
            selected_objs = scene.objects

        from pxr import Usd
        usd_path = bpy.path.abspath(context.scene.usd_file_path)
        stage_ref = Usd.Stage.Open(usd_path)
        if stage_ref.GetPrimAtPath('/Root/Looks').IsValid():
            usd_materials = self.get_usd_materials_from_looks(stage_ref, context.scene)
        else:
            usd_materials = self.get_usd_materials_from_references(stage_ref, context.scene, selected_objs)
        
        for obj in selected_objs:
            if obj.type == "MESH":
                for mat_slot in obj.material_slots:
                    if mat_slot.material:
                        if "." in mat_slot.material.name:
                            usd_material = usd_materials.get(mat_slot.material.name.split(".")[0])
                        else:
                            usd_material = usd_materials.get(mat_slot.material.name)
                        if usd_material and mat_slot.material.node_tree:
                           #print("material:" + str(mat_slot.material.name))                
                           for node in mat_slot.material.node_tree.nodes:
                                if node.type=='TEX_IMAGE':
                                    for image_type, image_path in usd_material["main"].items():
                                        if node.image and image_path and node.image.name in usd_material["preview"][image_type]:
                                            node.image = bpy.data.images.load(image_path)
                                            if image_type == "normal":
                                                node.image.colorspace_settings.name = "Non-Color"
                                   #print(" texture: "+str(node.image.name))

        

        return {'FINISHED'}


class OmniversePreviewsReplacerPanel(bpy.types.Panel):
    
    bl_idname = 'VIEW3D_PT_omniverse_replacer_previews'
    bl_label = 'Omniverse Previews Replacer'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_description = "Replaces preview textures for objects from the Omniverse with the origin ones"
    bl_category = "Omniverse"
    
    def draw(self, context):
        """
        It creates a column layout, then for each property in the PROPS list, it creates a row layout,
        and adds a property to that row
        
        :param context: The context of the operator
        """
        col = self.layout.column()
        for (prop_name, _) in PROPS:
            row = col.row()
            row.prop(context.scene, prop_name)

        col.operator('opr.replace_selected_previews', text='Replace Previews')
        #col.operator('opr.replace_selected_previews', text='Restore Previews')



PROPS = [
    ('usd_file_path', bpy.props.StringProperty(name='USD File', default='', subtype='FILE_PATH')),
    ('is_diffuse_selected', bpy.props.BoolProperty(name='Diffuse', default=True, description='Replace diffuse textures')),
    ('is_normal_selected', bpy.props.BoolProperty(name='Normal', default=True, description='Replace normal textures')),
    ('is_specular_selected', bpy.props.BoolProperty(name='Specular', default=True, description='Replace specular textures')),
    ('is_roughness_selected', bpy.props.BoolProperty(name='Roughness', default=True, description='Replace roughness textures')),
    ('is_metallic_selected', bpy.props.BoolProperty(name='Metallic', default=True, description='Replace metallic textures')),
    ('is_emissive_selected', bpy.props.BoolProperty(name='Emissive', default=True, description='Replace emissive textures')),
    ('is_opacity_selected', bpy.props.BoolProperty(name='Metallic', default=True, description='Replace metallic textures')),
    ('is_ao_selected', bpy.props.BoolProperty(name='AO', default=True, description='Replace AO textures')),
    ('usd_replace_selected', bpy.props.BoolProperty(name='Only Selected Meshes', default=True, description='Take action only to selected objects, uncheck to select all objects in the scene')),
]


CLASSES = [
    OmniversePreviewReplaceSelected,
    OmniversePreviewsReplacerPanel,
]


def register():
    """
    It creates a new property for each item in the PROPS list, and then registers each class in the
    CLASSES list
    """
    try:
        from pxr import Usd
    except:
        py_exec = str(sys.executable)
        # Get lib directory
        lib = Path(py_exec).parent.parent / "lib"
        # Ensure pip is installed
        subprocess.call([py_exec, "-m", "ensurepip", "--user" ])
        # Update pip (not mandatory)
        subprocess.call([py_exec, "-m", "pip", "install", "--upgrade", "pip" ])
        # Install packages
        subprocess.call([py_exec,"-m", "pip", "install", f"--target={str(lib)}", "usd-core"])
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for blender_class in CLASSES:
        bpy.utils.register_class(blender_class)


def unregister():
    """
    It removes the properties from the scene and unregisters the classes
    """
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)

    for blender_class in CLASSES:
        bpy.utils.unregister_class(blender_class)


if __name__ == "__main__":
    register()
