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

# Title: Simple Carnival Save File No Confirmation
# Author: Jeff Boller (http://3d.simplecarnival.com)
# Description: Ctrl+S saves the current file without popping up Blender's annoying tiny confirmation dialog box.
# Requirements: Blender 2.6.7+ (http://www.blender.org)
###############################################################################################################################################################

###############################################################################################################################################################
# VERSION HISTORY
#
# 1.0.0 - 6/6/15 - Created
# 1.0.1 - 6/7/15 - Fixed a conflict with simple_carnival_select_children_and_parent add-on
#                  Removed the "File->Save File No Confirmation" menu option, since it's not needed
#
###############################################################################################################################################################

bl_info = {
    'name': "Simple Carnival Save File No Confirmation",
    'author': "Jeff Boller",
    'version': (1, 0, 0),
    'blender': (2, 7, 4),
    'api': 44136,
    'location': "",
    'description': "Ctrl+S saves the current file without popping up Blender's annoying tiny confirmation dialog box.",
    'wiki_url': "3d.simplecarnival.com",
    'tracker_url': "",
    'category': "Object"}

import bpy
import re

class save_file_no_confirmaton(bpy.types.Operator):
    """Ctrl+S saves the current file without popping up Blender's annoying tiny confirmation dialog box."""
    bl_idname = "object.logic_bricks_copy"  # I'm not sure if this is correct -- I had to pick out some existing API call. 
    bl_label = "Save File No Confirmation"

    def execute(self, context):
        if (bpy.data.filepath == ""):
            bpy.ops.wm.save_as_mainfile('INVOKE_DEFAULT')
        else:
            bpy.ops.wm.save_mainfile()
            self.report({'INFO'}, "File saved!")
        return {'FINISHED'}

def draw_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(save_file_no_confirmaton.bl_idname, text=save_file_no_confirmaton.bl_label)

#
# Register
#
addon_keymaps = []

def register():

    # handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY')
    kmi = km.keymap_items.new(save_file_no_confirmaton.bl_idname, 'S', 'PRESS', ctrl=True)
    addon_keymaps.append((km, kmi))

    bpy.utils.register_class(save_file_no_confirmaton)

def unregister():
    # remove keymap entry
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(save_file_no_confirmaton)

if __name__ == "__main__":
    register()