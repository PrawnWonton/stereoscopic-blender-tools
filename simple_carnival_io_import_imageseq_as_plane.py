# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Title: Simple Carnival Import Imageseq as Plane
# Author: Jeff Boller (http://3d.simplecarnival.com), Florian Meyer (tstscr), mont29, matali
# Description: Imports an image sequence and creates a plane with the appropriate aspect ratio. The first image in the sequence is mapped to the plane.
#              Only works in Cycles and is intended for use with BISE (Blender Image Sequence Editor).
# Requirements: Blender 2.69+ (http://www.blender.org)

###############################################################################################################################################################
# VERSION HISTORY
#
# 2.3.1 - 11/23/14 - Made it so that the plane's rotation is x=90. That way it will be facing the camera in the default Simple Carnival Animation Template 
#                    settings.
# 2.3.2 - 11/24/14 - Made it so that it pulls in the BISE directory name (above the output directory) and names the image sequence object with the same name
#                    (kind of like Blender's import images as planes).
# 2.3.3 - 3/19/15 - First public release on GitHub.
# 3.0.0 - 6/26/15 - Imports transparent PNG images without having to have a separate alpha image file.
###############################################################################################################################################################

bl_info = {
    "name": "Simple Carnival Import Image Sequence as Plane",
    "author": "Jeff Boller, Florian Meyer (tstscr), mont29, matali",
    "version": (2, 3, 2),
    "blender": (2, 66, 4),
    "location": "File > Import > Images as Sequence as Plane or Add > Mesh > Image Sequence as Plane",
    "description": "Imports an image sequence and creates a plane with the appropriate aspect ratio. "
                   "The first image in the sequence is mapped to the plane."
                   "Only works in Cycles and is intended for use with BISE (Blender Image Sequence Editor).",
    'wiki_url': "3d.simplecarnival.com",
    "tracker_url": "",
    "category": "Import-Export"}

import bpy
from bpy.types import Operator
import mathutils
import os
import collections

from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty,
                       FloatProperty,
                       CollectionProperty,
                       )

from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy_extras.image_utils import load_image

# -----------------------------------------------------------------------------
# Global Vars

EXT_FILTER = getattr(collections, "OrderedDict", dict)((
    ("png", (("png", ), "PNG ({})", "Portable Network Graphics")),
))

CYCLES_SHADERS = (
    ('BSDF_DIFFUSE', "Diffuse", "Diffuse Shader"),
    ('EMISSION', "Emission", "Emission Shader"),
    ('BSDF_DIFFUSE_BSDF_TRANSPARENT', "Diffuse & Transparent", "Diffuse and Transparent Mix"),
    ('EMISSION_BSDF_TRANSPARENT', "Emission & Transparent", "Emission and Transparent Mix"),
    ('ShaderNodeMixShader', 'MIX_SHADER', 'Mix Shader')
)

# store keymaps here to access after registration
addon_keymaps = []


# -----------------------------------------------------------------------------
# Misc utils.
def gen_ext_filter_ui_items():
    return tuple((k, name.format(", ".join("." + e for e in exts)) if "{}" in name else name, desc)
                 for k, (exts, name, desc) in EXT_FILTER.items())


def is_image_fn(fn, ext_key):
    ext = os.path.splitext(fn)[1].lstrip(".").lower()
    return ext in EXT_FILTER[ext_key][0]



# -----------------------------------------------------------------------------
# Cycles utils.
def get_input_nodes(node, nodes, links):
    # Get all links going to node.
    input_links = {lnk for lnk in links if lnk.to_node == node}
    # Sort those links, get their input nodes (and avoid doubles!).
    sorted_nodes = []
    done_nodes = set()
    for socket in node.inputs:
        done_links = set()
        for link in input_links:
            nd = link.from_node
            if nd in done_nodes:
                # Node already treated!
                done_links.add(link)
            elif link.to_socket == socket:
                sorted_nodes.append(nd)
                done_links.add(link)
                done_nodes.add(nd)
        input_links -= done_links
    return sorted_nodes


def auto_align_nodes(node_tree):
    print('\nAligning Nodes')
    x_gap = 200
    y_gap = 100
    nodes = node_tree.nodes
    links = node_tree.links
    to_node = None
    for node in nodes:
        if node.type == 'OUTPUT_MATERIAL':
            to_node = node
            break
    if not to_node:
        return  # Unlikely, but bette check anyway...

    def align(to_node, nodes, links):
        from_nodes = get_input_nodes(to_node, nodes, links)
        for i, node in enumerate(from_nodes):
            node.location.x = to_node.location.x - x_gap
            node.location.y = to_node.location.y
            node.location.y -= i * y_gap
            node.location.y += (len(from_nodes)-1) * y_gap / (len(from_nodes))
            align(node, nodes, links)

    align(to_node, nodes, links)


def clean_node_tree(node_tree):
    nodes = node_tree.nodes
    for node in nodes:
        if not node.type == 'OUTPUT_MATERIAL':
            nodes.remove(node)
    return node_tree.nodes[0]


# -----------------------------------------------------------------------------
# Operator

class IMPORT_OT_imageseq_as_plane(Operator, AddObjectHelper):
    """Create mesh plane(s) from image files with the appropiate aspect ratio"""
    bl_idname = "import_imageseq.as_plane"
    bl_label = "Import Image Sequence as Plane"
    bl_options = {'REGISTER', 'UNDO'}

    # -----------
    # File props.
    files = CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})

    directory = StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    # Show only images/videos, and directories!
    filter_image = BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})
    filter_movie = BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})
    filter_folder = BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})
    filter_glob = StringProperty(default="", options={'HIDDEN', 'SKIP_SAVE'})

    # --------
    # Options.
    align = BoolProperty(name="Align Planes", default=True, description="Create Planes in a row")

    align_offset = FloatProperty(name="Offset", min=0, soft_min=0, default=0.1, description="Space between Planes")

    # Callback which will update File window's filter options accordingly to extension setting.
    def update_extensions(self, context):
        self.filter_image = False
        self.filter_movie = False
        flt = ";".join(("*." + e for e in EXT_FILTER[self.extension][0]))
        self.filter_glob = flt
        # And now update space (file select window), if possible.
        space = bpy.context.space_data
        # XXX Can't use direct op comparison, these are not the same objects!
        if (space.type != 'FILE_BROWSER' or space.operator.bl_rna.identifier != self.bl_rna.identifier):
            return
        space.params.use_filter_image = self.filter_image
        space.params.use_filter_movie = self.filter_movie
        space.params.filter_glob = self.filter_glob
        # XXX Seems to be necessary, else not all changes above take effect...
        bpy.ops.file.refresh()
    extension = EnumProperty(name="Extension", items=gen_ext_filter_ui_items(),
                             description="Only import files of this type", update=update_extensions)

    # -------------------
    # Plane size options.
    _size_modes = (
        ('ABSOLUTE', "Absolute", "Use absolute size"),
        ('DPI', "Dpi", "Use definition of the image as dots per inch"),
        ('DPBU', "Dots/BU", "Use definition of the image as dots per Blender Unit"),
    )
    size_mode = EnumProperty(name="Size Mode", default='ABSOLUTE', items=_size_modes,
                             description="How the size of the plane is computed")

    height = FloatProperty(name="Height", description="Height of the created plane",
                           default=1.0, min=0.001, soft_min=0.001, subtype='DISTANCE', unit='LENGTH')

    factor = FloatProperty(name="Definition", min=1.0, default=600.0,
                           description="Number of pixels per inch or Blender Unit")

    # -------------------------
    # Blender material options.
    t = bpy.types.Material.bl_rna.properties["use_shadeless"]
    use_shadeless = BoolProperty(name=t.name, default=False, description=t.description)

    use_transparency = BoolProperty(name="Use Alpha", default=False, description="Use alphachannel for transparency")

    t = bpy.types.Material.bl_rna.properties["transparency_method"]
    items = tuple((it.identifier, it.name, it.description) for it in t.enum_items)
    transparency_method = EnumProperty(name="Transp. Method", description=t.description, items=items)

    t = bpy.types.Material.bl_rna.properties["use_transparent_shadows"]
    use_transparent_shadows = BoolProperty(name=t.name, default=False, description=t.description)

    #-------------------------
    # Cycles material options.
    shader = EnumProperty(name="Shader", items=CYCLES_SHADERS, description="Node shader to use")

    overwrite_node_tree = BoolProperty(name="Overwrite Material", default=True,
                                       description="Overwrite existing Material with new nodetree "
                                                   "(based on material name)")

    # --------------
    # Image Options.
    t = bpy.types.Image.bl_rna.properties["alpha_mode"]
    alpha_mode_items = tuple((e.identifier, e.name, e.description) for e in t.enum_items)
    alpha_mode = EnumProperty(name=t.name, items=alpha_mode_items, default=t.default, description=t.description)

    t = bpy.types.IMAGE_OT_match_movie_length.bl_rna
    match_len = BoolProperty(name=t.name, default=True, description=t.description)

    t = bpy.types.Image.bl_rna.properties["use_fields"]
    use_fields = BoolProperty(name=t.name, default=False, description=t.description)

#    t = bpy.types.ImageUser.bl_rna.properties["use_auto_refresh"]
#    use_auto_refresh = BoolProperty(name=t.name, default=True, description=t.description)

    t = bpy.types.ImageUser.bl_rna.properties["use_cyclic"]
    use_cyclic = BoolProperty(name=t.name, default=False, description=t.description)

    relative = BoolProperty(name="Relative", default=True, description="Apply relative paths")

    def draw(self, context):
        engine = context.scene.render.engine
        layout = self.layout

        box = layout.box()
        box.label("Import Options:", icon='FILTER')
        box.prop(self, "extension", icon='FILE_IMAGE')
        box.prop(self, "align")
        box.prop(self, "align_offset")

        row = box.row()
        row.active = bpy.data.is_saved
        row.prop(self, "relative")
        # XXX Hack to avoid allowing videos with Cycles, crashes currently!
        
        box = layout.box()
        box.label("Material Settings: (Cycles)", icon='MATERIAL')
        box.prop(self, 'shader', expand = True)
        box.prop(self, 'overwrite_node_tree')
        box.prop(self, "use_cyclic")

        box = layout.box()
        box.label("Plane dimensions:", icon='ARROW_LEFTRIGHT')
        row = box.row()
        row.prop(self, "size_mode", expand=True)
        if self.size_mode == 'ABSOLUTE':
            box.prop(self, "height")
        else:
            box.prop(self, "factor")

    def invoke(self, context, event):
        self.update_extensions(context)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not bpy.data.is_saved:
            self.relative = False

        # the add utils don't work in this case because many objects are added disable relevant things beforehand
        editmode = context.user_preferences.edit.use_enter_edit_mode
        context.user_preferences.edit.use_enter_edit_mode = False
        if context.active_object and context.active_object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

        self.import_images(context)

        context.user_preferences.edit.use_enter_edit_mode = editmode
        return {'FINISHED'}

    # Main...
    def import_images(self, context):
        engine = context.scene.render.engine
        import_list, directory = self.generate_paths()
        import_list2, directory2 = self.generate_paths()

#        for x in import_list:
#             self.report({'INFO'}, x)

        images = (load_image(path, directory) for path in import_list)

        # Figure out the name of the BISE directory (the level above 'output') so we can give the image sequence a name.
        directory_list = directory.split("\\")
        found_output = 0
        img_seq_name = "ImageSequence"
        for dir_element in reversed(directory_list):
            if (found_output == 1):
                img_seq_name = dir_element
                break

            if (dir_element == "output"):
                found_output = 1

        myCount=len(self.files) 

        i=0
        imgWidth = 0
        imgHeight = 0
        for img in images:
            if i==0:                     
                imgWidth, imgHeight = img.size
                materials = self.create_cycles_material(img,myCount) # only make one material
            i += 1

#        planes = tuple(self.create_image_plane(context, mat) for mat in materials)
        planes = self.create_image_plane(context, materials, imgWidth, imgHeight, img_seq_name) # planes only has one plane

        context.scene.update()
#        if self.align:
#            self.align_planes(planes)

#        for plane in planes:
        planes.select = True

#        self.report({'INFO'}, "Added {} Image Plane(s)".format(len(planes)))
        self.report({'INFO'}, "Added 1 Image Plane")

    def create_image_plane(self, context, material, imgWidth, imgHeight, img_seq_name):
        nodes = material.node_tree.nodes
        img = next((node.image for node in nodes if node.type == 'TEX_IMAGE'))
        self.report({'INFO'}, str(img))
        px = imgWidth
        py = imgHeight
        self.report({'INFO'}, "***** create_image_plane px: " + str(px) + "   py: " + str(py))

        # can't load data
        if px == 0 or py == 0:
            px = py = 1

        if self.size_mode == 'ABSOLUTE':
            y = self.height
            x = px / py * y
        elif self.size_mode == 'DPI':
            fact = 1 / self.factor / context.scene.unit_settings.scale_length * 0.0254
            x = px * fact
            y = py * fact
        else:  # elif self.size_mode == 'DPBU'
            fact = 1 / self.factor
            x = px * fact
            y = py * fact

        bpy.ops.mesh.primitive_plane_add('INVOKE_REGION_WIN')
        plane = context.scene.objects.active
        # Why does mesh.primitive_plane_add leave the object in edit mode???
        if plane.mode is not 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        plane.dimensions = x, y, 0.0
        plane.name = img_seq_name
        bpy.ops.object.transform_apply(scale=True)
        bpy.context.object.rotation_euler[0] = 0 # Import at a rotation of x=0 so that it will be facing the camera on Better Blender and The Simple Carnival animation template (Y is up)
        plane.data.uv_textures.new()
        plane.data.materials.append(material)
        plane.data.uv_textures[0].data[0].image = img
#        self.report({'INFO'}, 'putting image on plane: ' + str(img.filepath))
#        plane.data.uv_textures[0].data[0].image = bpy.data.images.load(str(img.filepath))

        material.game_settings.use_backface_culling = False
        material.game_settings.alpha_blend = 'ALPHA'
        return plane

    def align_planes(self, planes):
        gap = self.align_offset
        offset = 0
        for i, plane in enumerate(planes):
            offset += (plane.dimensions.x / 2.0) + gap
            if i == 0:
                continue
            move_local = mathutils.Vector((offset, 0.0, 0.0))
            move_world = plane.location + move_local * plane.matrix_world.inverted()
            plane.location += move_world
            offset += (plane.dimensions.x / 2.0)

    def generate_paths(self):
        return (fn.name for fn in self.files if is_image_fn(fn.name, self.extension)), self.directory

#    # Internal
#    def create_image_textures(self, context, image):
#        fn_full = os.path.normpath(bpy.path.abspath(image.filepath))
#
#        # look for texture with importsettings
#        for texture in bpy.data.textures:
#            if texture.type == 'IMAGE':
#                tex_img = texture.image
#                if (tex_img is not None) and (tex_img.library is None):
#                    fn_tex_full = os.path.normpath(bpy.path.abspath(tex_img.filepath))
#                    if fn_full == fn_tex_full:
#                        self.set_texture_options(context, texture)
#                        return texture
#
#        # if no texture is found: create one
#        name_compat = bpy.path.display_name_from_filepath(image.filepath)
#        texture = bpy.data.textures.new(name=name_compat, type='IMAGE')
#        texture.image = image
#        self.set_texture_options(context, texture)
#        return texture

    def create_material_for_texture(self, texture):
        # look for material with the needed texture
        for material in bpy.data.materials:
            slot = material.texture_slots[0]
            if slot and slot.texture == texture:
                self.set_material_options(material, slot)
                return material

        # if no material found: create one
        name_compat = bpy.path.display_name_from_filepath(texture.image.filepath)
        material = bpy.data.materials.new(name=name_compat)
        slot = material.texture_slots.add()
        slot.texture = texture
        slot.texture_coords = 'UV'
        self.set_material_options(material, slot)
        return material

    def set_image_options(self, image):
        image.alpha_mode = self.alpha_mode
        image.use_fields = self.use_fields

        if self.relative:
            try:  # can't always find the relative path (between drive letters on windows)
                image.filepath = bpy.path.relpath(image.filepath)
            except ValueError:
                pass

    def set_texture_options(self, context, texture):
        texture.image.use_alpha = self.use_transparency
        texture.image_user.use_auto_refresh = 1
        if self.match_len:
            ctx = context.copy()
            ctx["edit_image"] = texture.image
            ctx["edit_image_user"] = texture.image_user
            bpy.ops.image.match_movie_length(ctx)

    def set_material_options(self, material, slot):
        if self.use_transparency:
            material.alpha = 0.0
            material.specular_alpha = 0.0
            slot.use_map_alpha = True
        else:
            material.alpha = 1.0
            material.specular_alpha = 1.0
            slot.use_map_alpha = False
        material.use_transparency = self.use_transparency
        material.transparency_method = self.transparency_method
        material.use_shadeless = self.use_shadeless
        material.use_transparent_shadows = self.use_transparent_shadows

    #--------------------------------------------------------------------------
    # Cycles
    def create_cycles_material(self, image, totalNumOfImages):
        name_compat = bpy.path.display_name_from_filepath(image.filepath)
        self.report({'INFO'}, 'image.filepath: ' + str(image.filepath))
        self.report({'INFO'}, 'name_compat: ' + str(name_compat))
        material = None
        for mat in bpy.data.materials:
            self.report({'INFO'}, 'mat: ' + str(mat))
            self.report({'INFO'}, 'mat.name: ' + str(mat.name))
            if mat.name == name_compat and self.overwrite_node_tree:
                material = mat
        if not material:
            self.report({'INFO'}, 'went into if not material')
            material = bpy.data.materials.new(name=name_compat)

        material.use_nodes = True
        node_tree = material.node_tree
        out_node = clean_node_tree(node_tree)


        bsdf_diffuse = node_tree.nodes.new('ShaderNodeBsdfDiffuse')
        bsdf_transparent = node_tree.nodes.new('ShaderNodeBsdfTransparent') # Used for the actual image transparency
        mix_shader_1 = node_tree.nodes.new('ShaderNodeMixShader') # Used for combining alpha and original images
        bsdf_transparent_fake = node_tree.nodes.new('ShaderNodeBsdfTransparent') # Used for setting the material transparency
        mix_shader_2 = node_tree.nodes.new('ShaderNodeMixShader') # Used for setting the material transparency

        mix_shader_2.inputs['Fac'].default_value=1 # Set to fully opaque


        tex_image = node_tree.nodes.new('ShaderNodeTexImage')
        actual_img = bpy.data.images.load(str(image.filepath))
        if (totalNumOfImages != 1): 
            actual_img.source = 'SEQUENCE' # When you set this to image sequence, it will start with the first image in the directory no matter what.
        tex_image.image = actual_img
        tex_image.show_texture = True
        tex_image.image_user.use_auto_refresh = 1
        tex_image.image_user.frame_duration = totalNumOfImages
        tex_image.image_user.use_cyclic = self.use_cyclic

        node_tree.links.new(out_node.inputs[0], mix_shader_2.outputs[0])
        node_tree.links.new(mix_shader_2.inputs[1], bsdf_transparent_fake.outputs[0])
        node_tree.links.new(mix_shader_2.inputs[2], mix_shader_1.outputs[0])

        node_tree.links.new(mix_shader_1.inputs['Fac'], tex_image.outputs["Alpha"])
        node_tree.links.new(mix_shader_1.inputs[1], bsdf_transparent.outputs[0])
        node_tree.links.new(mix_shader_1.inputs[2], bsdf_diffuse.outputs[0])
        node_tree.links.new(bsdf_diffuse.inputs[0], tex_image.outputs[0])

        auto_align_nodes(node_tree)
        bpy.data.images[image.name].source='SEQUENCE' 
        return material


# -----------------------------------------------------------------------------
# Register
def import_images_button(self, context):
    self.layout.operator(IMPORT_OT_imageseq_as_plane.bl_idname,
                         text="Image Sequence as Plane", icon='TEXTURE')


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(import_images_button)
    bpy.types.INFO_MT_mesh_add.append(import_images_button)

#    bpy.utils.register_class(IMPORT_OT_imageseq_as_plane)
    # handle the keymap
#    wm = bpy.context.window_manager
#    km = wm.keyconfigs.addon.keymaps.new(name='Import Imageseq as Plane', space_type='EMPTY')
#    kmi = km.keymap_items.new(IMPORT_OT_imageseq_as_plane.bl_idname, 'SPACE', 'PRESS', ctrl=True, shift=True)
#    kmi.properties.total = 4
#    addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(import_images_button)
    bpy.types.INFO_MT_mesh_add.remove(import_images_button)

#    bpy.utils.unregister_class(IMPORT_OT_imageseq_as_plane)
    # handle the keymap
#    for km, kmi in addon_keymaps:
#        km.keymap_items.remove(kmi)
#    addon_keymaps.clear()

if __name__ == "__main__":
    register()
