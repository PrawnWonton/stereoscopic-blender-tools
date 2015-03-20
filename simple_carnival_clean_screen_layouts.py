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

# Title: Simple Carnival Clean Screen Layouts
# Author: Jeff Boller (http://3d.simplecarnival.com)
# Description: When you create a new window by shift+clicking the window splitter in Blender, it will create a new screen layout, which is designated by 
#              a . and three digit extension. Over time, a project file may accumulate dozens of extraneous screen layouts. This script will delete any 
#              layouts that have a .### extension. You can find the "Clean Screen Layouts" option in the Info panel under the Window menu option.
# Requirements: Blender 2.6.7+ (http://www.blender.org)

###############################################################################################################################################################
# VERSION HISTORY
#
# 1.0.0 -- 11/26/2014 - Made a cleaner delete
# 1.0.1 -- 11/29/2014 - Made it so that it doesn't delete any screen layouts that are active.
# 1.0.2 -- 3/19/2014 - First public release on GitHub
#
###############################################################################################################################################################

bl_info = {
    'name': "Simple Carnival Clean Screen Layouts",
    'author': "CoDEmanX, Jeff Boller",
    'version': (1, 0, 2),
    'blender': (2, 6, 7),
    'api': 44136,
    'location': "Info panel -> 'Window' menu option -> 'Clean Screen Layouts'",
    'description': "Deletes all screen layouts which end with .###",
    'wiki_url': "3d.simplecarnival.com",
    'tracker_url': "",
    'category': "Object"}

import bpy
import re

class SimpleOperator(bpy.types.Operator):
    """Delete screen layouts which end with .###"""
    bl_idname = "screen.clear"
    bl_label = "Clean Screen Layouts"

    def execute(self, context):
        screen_name = context.screen.name
        for screen in bpy.data.screens:
            if re.match(".*\.\d{3}$", screen.name) is not None:
                s = screen.name
                allowed_to_delete = 1
                # Make sure we don't have any windows that have this particular screen layout open. (Blender will crash.)
                for window in bpy.context.window_manager.windows:
                    if (window.screen.name == s):
                        self.report({'WARNING'}, "Cannot delete screen layout '" + window.screen.name + "' because it is open.")
                        allowed_to_delete = 0
                        break
                if (allowed_to_delete == 1):
                    bpy.ops.screen.delete({'window': context.window, 'screen': screen, 'region': None})
                    self.report({'INFO'}, "Deleted screen '" + s + "'")
        screen = bpy.data.screens.get(screen_name)
        if screen is not None:
            context.window.screen = screen
        return {'FINISHED'}

def draw_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(SimpleOperator.bl_idname, text=SimpleOperator.bl_label)

def register():
    bpy.utils.register_class(SimpleOperator)
    bpy.types.INFO_MT_window.append(draw_func)

def unregister():
    bpy.utils.unregister_class(SimpleOperator)
    bpy.types.INFO_MT_header.remove(draw_func)

if __name__ == "__main__":
    register()