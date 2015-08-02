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

# Title: Simple Carnival Composite Sandwich
# Author: Jeff Boller (http://3d.simplecarnival.com)
# Description: This add-on allows Blender users create a "composite sandwich" -- that is, multiple scenes can be stacked and automatically
#              composited together. I previously created a similar add-on for making composite sandwiches -- "Simple Carnival Stereoscopic Camera". However,
#              that add-on is now obsolete with the introduction of Blender 2.75's built-in stereoscopic features.
# Requirements: My forked version of Blender called "Better Blender", version 2.75 or higher: https://github.com/simplecarnival/BetterBlender
#               I assume this will work on the official Blender 2.75.

###############################################################################################################################################################
# VERSION HISTORY
# 1.0.0 - 8/1/2015 - First version.
#
###############################################################################################################################################################


bl_info = {
    'name': "Simple Carnival Composite Sandwich",
    'author': "Jeff Boller",
    'version': (1, 0, 0),
    'blender': (2, 7, 5),
    'api': 44136,
    'location': "Select a Camera > Properties Panel > Camera Panel > Composite Sandwich",
    'description': "Creates automatic layered composite shots from multiple scenes",
    'warning': "", 
    'wiki_url': "3d.simplecarnival.com",
    'tracker_url': "",
    'category': "Object"}

import bpy
import mathutils
from math import *
from bpy.props import *


class NODE_EDITOR_PT_preset(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_label = "Composite Sandwich"

    @classmethod
    def poll(cls, context):
        view = context.space_data
        return (view)

    def draw(self, context):
        scn = bpy.context.scene
        view = context.space_data

        if (view.tree_type == 'COMPOSITING' or view.tree_type == 'CompositorNodeTree') and (view.id.use_nodes):    
            layout = self.layout
            col = layout.column()
            row = col.row()
            row.prop(scn, 'composite_sandwich_presets')
            row = layout.row()
            row.operator('compositesandwich.create_sandwich')
            row = layout.row()
            row.prop(scn, 'replace_current_nodes')
        else:
            layout = self.layout
            row = layout.row() 
            row.label(text="In order to create a")
            row = layout.row()
            row.label(text="composite sandwich,")
            row = layout.row()
            row.label(text="select 'COMPOSITING'")
            row = layout.row()
            row.label(text="and check 'Use Nodes'")


class OBJECT_OT_create_sandwich(bpy.types.Operator):
    bl_label = 'Create Sandwich (F9)'
    bl_idname = 'compositesandwich.create_sandwich'
    bl_description = 'Creates the composite sandwich. Use the F9 key to automatically create a sandwich.'

    # On mouse up:
    def invoke(self, context, event):
        self.make_sandwich(context)
        return {'FINISHED'}

    def make_sandwich(self, context):
        import bpy
        import re        
        scene = bpy.context.scene        
        tree = scene.node_tree
        my_sandwich_selection = scene.composite_sandwich_presets # We need to store this, as scene.composite_sandwich_presets somehow gets internally reset by the time we need its value later in this function.
        originalSceneName = bpy.context.screen.scene.name

        if (scene.replace_current_nodes == True):
             for i in tree.nodes:
                  tree.nodes.remove(i)

        if (my_sandwich_selection == "2DNODES-ONE"):
            # Do the simplest render possible
            center_render_layer = tree.nodes.new('CompositorNodeRLayers')
            center_render_layer.location = (0,280)
            try:
                center_render_layer.scene = bpy.data.scenes[originalSceneName]
            except:
                pass

            # We need to have an output node. So create it.
            file_output_node_center = tree.nodes.new('CompositorNodeOutputFile')
            file_output_node_center.file_slots.clear()

            file_output_node_center.base_path = "//"
            file_output_node_center.file_slots.new("img")
            file_output_node_center.location = (300, 600)

            # Comp output
            composite_node = tree.nodes.new('CompositorNodeComposite')
            composite_node.location = (300, 250)

            # Hook them all up
            tree.links.new(center_render_layer.outputs[0],file_output_node_center.inputs[0])
            tree.links.new(center_render_layer.outputs[0],composite_node.inputs[0])
            return
        else: # my_sandwich_selection == "NODES-ALL"
            # First, get a list of all of our scenes.
            scene_list_raw=[] 
            for scene in bpy.data.scenes:
                 scene_list_raw.append(scene.name)
            scene_list=[] # Legit scenes
            testOverlayNum = 0
            numOfOverlaysFound = 0
            while testOverlayNum <= 999:
                sPrefix = "%03d ." % (testOverlayNum)
                regex = re.compile(sPrefix)
                matches = [string for string in scene_list_raw if re.match(regex, string)]
                matchIndex=1
                sceneC = ""
                for myMatch in matches:
                    print("Matches found for '" + sPrefix + "': " + myMatch)
                    sceneC = myMatch
                    numOfOverlaysFound = numOfOverlaysFound + 1
                    scene_list.append(sceneC)
                    matchIndex = matchIndex + 1

                testOverlayNum = testOverlayNum + 1

            # Create the file output.
            outputNodeLocationX = 200
            file_output_node_left = tree.nodes.new('CompositorNodeOutputFile')
            file_output_node_left.base_path = "//"
            file_output_node_left.file_slots.clear()
            file_output_node_left.file_slots.new("img")
            file_output_node_left.location = (outputNodeLocationX, 270)

            if numOfOverlaysFound == 0:
                return # There's nothing to do, so get out.

            # Check for our special case where we have only one legit composite scene.
            if numOfOverlaysFound == 1:
                # Just connect things with no AlphaOver nodes.
                sceneL = scene_list[0]
                # Set the image node.
                left_render_layer = tree.nodes.new('CompositorNodeRLayers')
                left_render_layer.location = (0,280)
                try:
                    left_render_layer.scene = bpy.data.scenes[sceneL]
                except:
                    pass

                # We have no overlay. Just hook directly from the render nodes into the output nodes.
                tree.links.new(left_render_layer.outputs[0],file_output_node_left.inputs[0])
                return

            # OK, we have to create a funky set of layers.
            currentOverlayNum = 1
            currentXVal = 0
            for currentScene in scene_list:
                if currentOverlayNum != numOfOverlaysFound: # We still need the AlphaOvers because we're not done yet
                    # Make the AlphaOver that we're going to be feeding into.
                    alphaover1_L = tree.nodes.new('CompositorNodeAlphaOver')
                    alphaover1_L.location = (currentXVal,370)
                    alphaover1_L.premul = 0.5

                # Create this overlay node.
                sL = currentScene

                # The next batch of nodes need to move over to the left.
                currentXVal = currentXVal - 200

                # Overlay L
                overlay_layer_L = tree.nodes.new('CompositorNodeRLayers')
                overlay_layer_L.location = (currentXVal,160)
                try:
                    overlay_layer_L.scene = bpy.data.scenes[sL]
                except:
                    pass

                if currentOverlayNum == 1:
                    # Special condition where this AlphaOver is the end of the line. Must plug this into the final renderer.
                    tree.links.new(alphaover1_L.outputs[0],file_output_node_left.inputs[0])

                    # Connect the overlays to the AlphaOvers.
                    tree.links.new(overlay_layer_L.outputs[0],alphaover1_L.inputs[2])
                elif currentOverlayNum == numOfOverlaysFound:
                    # We're at the very topmost layer.
                    # Connect the overlay into the AlphaOver from the *previous iteration of this loop*.
                    tree.links.new(overlay_layer_L.outputs[0],alphaoverOLD1_L.inputs[1])
                else:
                    # Connect the overlays to the AlphaOvers.
                    tree.links.new(overlay_layer_L.outputs[0],alphaover1_L.inputs[2])

                    # We need to plug into the AlphaOver from the previous iteration of this loop.
                    tree.links.new(alphaover1_L.outputs[0],alphaoverOLD1_L.inputs[1])

                if currentOverlayNum != numOfOverlaysFound: # We still need the AlphaOvers because we're not done yet
                    # Remember our old AlphaOvers for the next iteration.
                    alphaoverOLD1_L = alphaover1_L

                currentOverlayNum = currentOverlayNum + 1

#
# Register
#
addon_keymaps = []

def register():

    # handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY')
    kmi = km.keymap_items.new(OBJECT_OT_create_sandwich.bl_idname, 'F9', 'PRESS')
    addon_keymaps.append((km, kmi))

    bpy.utils.register_module(__name__)

    bpy.types.Scene.composite_sandwich_presets = bpy.props.EnumProperty(attr="composite_preset",
        items=[ ("NODES-ALL", "All scenes", "Make a composite sandwich for all scenes"),
                ("NODES-ONE", "Only this scene", "Make a composite sandwich for only this scene")],
        name="Create",
        description="Select which kind of composite sandwich to make.", 
        default="NODES-ALL")

    bpy.types.Scene.replace_current_nodes = bpy.props.BoolProperty(
        name="Replace Current Nodes", 
        description="Replace Current Nodes?", 
        default=True)

def unregister():
    # remove keymap entry
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_module(__name__)
	
if __name__ == "__main__":
    register()
