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

# Title: Simple Carnival Select Children and Parent
# Author: Jeff Boller (http://3d.simplecarnival.com)
# Description: If you have a hierarchy of objects and want to select the entire hierarchy, here's what you have to do in Blender:
#                   * Click on the parent object in the Outliner
#                   * Hover over the 3D View, press Shift+G, select "Children". (The parent object will become unselected.)
#                   * Re-select the parent object (hold down shift while doing so)
#              This script dispenses with the annoying behavior of the parent object becoming unselected and then having to reselect it. Also, it dispenses 
#              with having to be over a particular window when performing these options.
#              Since this add-on uses Shift+G -- the same shortcut as Blender's built-in "Select Grouped" menu (though this add-on is arguably more useful), 
#              you will need to disable the "Select Grouped" menu in Blender. Go to User Preferences -> Input. Search for Select Grouped (under Object Mode).
#              The shortcut is probably Shift+G. Uncheck the "Select Grouped" option. Click the "Save User Settings" button. You should now be able to use 
#              Shift+G to access this add-on instead.
# Requirements: Blender 2.6.7+ (http://www.blender.org)
###############################################################################################################################################################

###############################################################################################################################################################
# VERSION HISTORY
#
# 1.0.0 - 12/10/14 - Created
# 1.0.1 - 3/19/14 - First public release on GitHub.
#
###############################################################################################################################################################

bl_info = {
    'name': "Simple Carnival Select Children and Parent",
    'author': "Jeff Boller",
    'version': (1, 0, 1),
    'blender': (2, 6, 7),
    'api': 44136,
    'location': "",
    'description': "Selects all children belonging to a parent and keeps the parent selected.",
    'wiki_url': "3d.simplecarnival.com",
    'tracker_url': "",
    'category': "Object"}

import bpy
import re

class select_children_and_parent(bpy.types.Operator):
    """Selects all children belonging to a parent and keeps the parent selected."""
    bl_idname = "object.select_random"  # I'm not sure if this is correct -- I had to pick out some existing API call. The Select Random menu option still works, FWIW.
    bl_label = "Select Children and Parent"

    def execute(self, context):
        bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
        return {'FINISHED'}

def draw_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(select_children_and_parent.bl_idname, text=select_children_and_parent.bl_label)

#
# Register
#
addon_keymaps = []

def register():

    # handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY')
    kmi = km.keymap_items.new(select_children_and_parent.bl_idname, 'G', 'PRESS', shift=True)
    addon_keymaps.append((km, kmi))

    bpy.utils.register_class(select_children_and_parent)
    bpy.types.VIEW3D_MT_select_object.append(draw_func)

def unregister():
    # remove keymap entry
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(select_children_and_parent)
    bpy.types.VIEW3D_MT_select_object.remove(draw_func)

if __name__ == "__main__":
    register()