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

# Title: Simple Carnival Stereoscopic Camera
# Author: Jeff Boller (http://3d.simplecarnival.com), Sebastian Schneider <s.schneider@noeol.de> 
# Description: This plug-in allows Blender users to render stereoscopic (3D) images. This is a heavily modified version of Sebastian Schneider's Stereoscopic 
#              Camera, version 1.6.8 (http://www.noeol.de/s3d/ ). I have been using this plug-in to create stereoscopic animated music videos: 
#              http://www.simplecarnival.com
#              Documentation can be found at my technical 3D blog: http://3d.simplecarnival.com
# Requirements: Blender 2.73a+ (http://www.blender.org)

###############################################################################################################################################################
# VERSION HISTORY
#
# 1.6.8.1 - 5/26/14 - Made it so that the "Scene" scene isn't rendered (speeding up rendering time by 1/3)
# 1.6.8.2 - 5/26/14 - Made left/right individual outputs which save in _LEFT and _RIGHT directories with limg and rimg filenames
# 1.8.8.3 - 5/27/14 - Made it so it creates new scenes like this: Scene_L, Scene_R ...instead of this: Left_Camera, Right_Camera.
#                     Also made it so that it will take any random scene name and append the _L and _R onto it to make a left and right camera.
#                     However, the script makes the assumption that when you automatically create the nodes, the main render node with no
#                     transparencies is going to be called "Scene" (sans quotes).
# 1.8.8.4 - 5/27/14 - Now supports one stereo scene overlay, called "Overlay1" (sans quotes). The way it works is, create a scene called
#                     "Overlay1". The intention is to render these scenes in the Blender internal engine, since not everything is supported in
#                     Cycles yet (clouds, fog, etc.). However, you can still render everything as one big happy render. So you make your overlay
#                     in the "Overlay1" scene (if you're using the Blender internal engine, make sure that the render settings under Shading/Alpha
#                     is set to "Transparent"). Make the automatic left and right cameras so there are these two scenes: "Overlay1_L", "Overlay1_R".
#                     When you're in the Node editor and add the new "Left and Right" stereoscopic preset via the "Add nodes" button, the node
#                     setup will automatically work in the Overlay1 scenes and combine them properly. Note that, as of this writing, there is 
#                     only support for the "Left and Right" stereoscopic preset. None of these params are set up for the other types of stereoscopic
#                     rendering.
# 1.8.8.4 - 5/28/14 - OK, forget that one stereo scene overlay. I need multiple stereo overlays. Forget the scene called "Scene".
#                     The bottommost scene is called "Overlay.000" (with the _L and _R associated with it). Each layer on top of that is named one
#                     number higher (e.g. "Overlay.001", "Overlay.002", etc.) and all have _L and _R associated with it. The numbers must be
#                     contiguous and there must be a "center" scene (i.e. the scene doesn't have a _L and _R associated with it). All other scenes
#                     are ignored.
# 1.8.8.5 - 5/29/14 - The order was backwards ("Overlay.000" was the topmost layer, not the bottommost layer). That's been fixed. Made it so you're
#                     now allowed to skip over overlays -- they don't have to be contiguous numbers. Therefore, you can have 10, 30, 40, etc. like
#                     line numbers in a BASIC program (and so you can leave room in between in case you need to sandwich in other overlays).
#                     Supports "Overlay.000" to "Overlay.999". Higher numbers are placed in front of lower numbers. 000 is required, even if you have
#                     only one stereo scene. 000 should always be the background (the layer furthest back).
# 1.8.8.6 - 5/30/14 - Altering it so that .000 should be the topmost layer.
# 1.8.8.7 - 5/30/14 - Doing away with the "Overlay.000" nomenclature. Now that I've been eating my own dogfood, it would be easier to view things
#                     if they were like BASIC line numbers like this:
#	                      000 My topmost layer
#		              000 My topmost layer_L
#		              000 My topmost layer_R
#			      500 My middle layer
#			      500 My middle layer_L
#			      500 My middle layer_R
#                     etc.
#                     Made it so that it looks to see if you only have *one* stereo scene and then do the special hookup to the renderer. It doesn't have to 
#                     be a 000 scene.
# 1.8.8.8 - 5/31/14 - OK, enough with having to manually make _L and _R scenes and keep them in sync when you add new objects. Made it so that when you
#                     create the render nodes, it automatically creates all of the _L and _R scenes.
# 1.8.8.9 - 5/31/14 - Added option to automatically remove old nodes.
# 1.8.8.10 - 6/5/14 - Added ability to import stereo images. Here's how to do it:
#                     * Create an empty object (or really any parent object). It doesn't matter what you call the parent object. 
#                     * Have two child image sequences (both in the exact same location) called "stereoimageL" and "stereoimageR" (case sensitive). You can choose whichever
#                       one is shown in the view or rendered...it doesn't matter. The important thing is that you use the empty object to move/scale/rotate
#                       the object around. You never want to move the stereoimageL or stereoimageR image sequence without moving the other.
#                     * After Stereoscopic Camera copies the center scene to create the left scene, remove ALL objects in the left scene that are called 
#                       "stereoimageR". The loop through all the objects in the left scene called "stereoimageL" and turn their rendering (both preview
#                       and render) on.
#                     * After Stereoscopic Camera copies the center scene to create the right scene, remove ALL objects in the right scene that are called
#                       "stereoimageL". Then loop through all the objects in the right scene called "stereoimageR" and turn their rendering (both preview
#                       and render) on.
# 1.8.8.11 - 6/5/14 - Added an anaglyph preview checkbox/feature. Removed the 3D output button because, really, all that really matters for serious stereoscopic
#                     use is separate L&R images.
# 1.8.8.12 - 6/7/14 - Added a dropdown that lets the user pick whether the nodes that are created are 3D for all legit nodes, 3D for just this particular
#                     scene, or 2D for just this particular scene. As I was working with the smoke simulator, I discovered that I needed this.
# 1.8.8.13 - 6/8/14 - Realized that you can't have duplicate objects with the same name in a scene. So you can't have more than one object named 
#                     "stereoimageL". So now the check is only for the BEGINNING of the name. In other words, as long as your object starts with
#                     "stereoimageL" or "stereoimageR", then it'll be treated appropriately when making stereo scenes.
# 1.8.8.14 - 6/8/14 - Fixed a bug where it wasn't recognizing the "stereoimageL" and "stereoimageR" objects.
# 1.8.8.15 - 6/9/14 - Added the ability to put in a static L&R background image. (Well, not actually. I *want* to add it in, but I'm too tired tonight.)
# 1.8.8.16 - 6/9/14 - Made it so that making render nodes automatically makes all paths relative. Blender doesn't always save all textures as relative
#                     for some reason, so this is actually a hack to work around that bug. 
# 1.8.8.17 - 6/11/14 - If you choose "2D - only this scene", the checkbox for "Show Anaglyph Preview" is disabled.
# 1.8.8.18 - 6/12/14 - Starting to implement useImageBackground. Got it working for the 2D scenes. Need to implement it for the 3D scenes next.
# 1.8.8.19 - 6/13/14 - OK, useImageBackground is implemented across the board. 
# 1.8.8.20 - 6/15/14 - When opening up a background file that ends with a "L.png", or "LEFT.png", look for the equivalent "R.png" or "RIGHT.png" file in 
#                      that directory. If it exists, then automatically populate the right image with that file.
# 2.0.1 - 10/22/14 - Realized that the original Stereoscopic Camera doesn't copy all of the depth of field camera settings in Cycles. This has been sort of
#                    fixed. It doesn't copy keyframes in the timeline, but it copies whatever the current depth of field settings are at the current frame
#                    when you click "Set Stereo Camera". So if you do have keyframes on the center camera, go to each keyframe, hit "Set Stereo Camera", then
#                    go to each camera and manually set the keyframe for that keyframe.
# 2.0.2 - 11/19/14 - Commented out aperture_ratio stuff...was getting an error when setting the camera on a big scene. Will look into later.
# 2.0.3 - 11/23/14 - Added "Clean Screen Layouts" button.
# 2.0.4 - 11/26/14 - Removed "Clear Screen Layouts" button and split it off into its own script/menu option. Added "Remove Stereo Scenes" as a test for
#                    CUDA-enabled projects. (If you click "Remove Stereo Scenes" before clicking "Add Nodes", do big CUDA-enabled projects crash?
# 2.0.5 - 11/26/14 - Experimental code that reworks how the stereo scenes are recreated. Must try with big CUDA-enabled project. Fixed bug where single
#                    3D you couldn't render JUST one scene in 3D; it'll kept setting up a render for all scenes (though 2D rendering worked fine).
# 2.0.6 - 11/27/14 - Confirmed that "Add Stereo Nodes" now works properly with large CUDA-enabled projects. Removed "Remove Stereo Scenes".
# 2.0.7 - 11/28/14 - After you remove the stereo scenes, the script now assigns the scene you just created (the stereo scenes that you just created)
#                    to the screen layouts SBS LEFT and SBS RIGHT (assuming they exist). Also made it so that the Anaglyph option is unchecked by default.
# 2.0.8 - 11/29/14 - Fixed assigning the screen layouts SBS LEFT and SBS RIGHT so that they're using the stereo version of whatever scene you just created
#                    nodes on (it only worked before if those screen layouts were open).
# 2.0.9 - 12/9/14 - Added F11 keyboard shortcut to automatically create render nodes for the current scene.
# 2.0.10 - 3/15/15 - Added "Stereoscopic scenes successful" message, which is more intuitive than the previous cryptic message.
# 2.0.11 - 3/19/15 - First public release on GitHub.
#
###############################################################################################################################################################


bl_info = {
    'name': "Simple Carnival Stereoscopic Camera",
    'author': "Jeff Boller, Sebastian Schneider <s.schneider@noeol.de>",
    'version': (2, 0, 9),
    'blender': (2, 6, 7),
    'api': 44136,
    'location': "Select a Camera > Properties Panel > Camera Panel > Stereoscopic Camera",
    'description': "Allows Blender to render stereoscopic images",
    'warning': "", 
    'wiki_url': "3d.simplecarnival.com",
    'tracker_url': "",
    'category': "Object"}

import bpy
import mathutils
from math import *
from bpy.props import *



#
# GUI (Panel)
#
class OBJECT_PT_stereo_camera(bpy.types.Panel):

    bl_label = "Stereoscopic Camera"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    # show this add-on only in the Camera-Data-Panel
    @classmethod
    def poll(self, context):
        return context.active_object.type  == 'CAMERA'

    #
    # Add some custom stereo properties to the selected camera
    #
    bpy.types.Object.stereo_camera_separation = bpy.props.FloatProperty(
        attr="stereo_camera_separation",
        name='stereo_camera_separation',
        description='Camera Separation in 1/1000 Blender Units',
        min=0.0, soft_min=0.0, max=10000, soft_max=10000, default=300)
        
    bpy.types.Object.stereo_focal_distance = bpy.props.FloatProperty(
        attr="stereo_focal_distance",
        name='stereo_focal_distance', 
        description='Distance to the Stereo-Window (Zero Parallax) in Blender Units',
        min=0.0, soft_min=0.0, max=1000, soft_max=1000, default=20)
        
    bpy.types.Object.max_parallax = bpy.props.FloatProperty(
        attr="max_parallax",
        name="max_parallax", 
        description='Max parallax angle in degree. Default 1.0', 
        min=0.0, soft_min=0.0, max=3.0, soft_max=3.0, default=1.0)
        
    bpy.types.Object.near_plane_distance = bpy.props.FloatProperty(
        attr="near_plane_distance",
        name="near_plane_distance", 
        description='Distance to Near-Plane in Blender Units (has no effect on the stereo output)',
        min=0.0, soft_min=0.0, max=100000, soft_max=100000, default=10)
        
    bpy.types.Object.far_plane_distance = bpy.props.FloatProperty(
        attr="far_plane_distance", 
        name="far_plane_distance",
        description='Distance to Far-Plane in Blender Units (has no effect on the stereo output)',
        min=0.0, soft_min=0.0, max=100000, soft_max=100000, default=100)

    bpy.types.Object.viewer_distance = bpy.props.FloatProperty(
        attr="viewer_distance",
        name="viewer_distance", 
        description='Distance between Viewer and the Projection Screen (e.g. Theater canvas, Stereo-TV or Display) in inch', 
        min=0.0, soft_min=0.0, max=10000, soft_max=10000, default=20)
        
    bpy.types.Object.stereo_camera_shift_x = bpy.props.FloatProperty(
        attr="stereo_camera_shift_x",
        name="stereo_camera_shift_x")
        
    bpy.types.Object.stereo_camera_delta = bpy.props.FloatProperty(
        attr="stereo_camera_delta", 
        name="stereo_camera_delta")
        
    bpy.types.Object.max_disparity = bpy.props.FloatProperty(
        attr="max_disparity", 
        name="max_disparity")

    bpy.types.Object.toein_angle = bpy.props.FloatProperty(
        attr="toein_angle", 
        name="toein_angle")
    
    bpy.types.Object.screen_ppi = bpy.props.IntProperty(
        attr="screen_ppi",
        name="screen_ppi", 
        description='Pixel per Inch on the Projection Screen (Theater Canvas, Stereo TV or Display)', 
        min=1, soft_min=1, max=1000, soft_max=1000, default=96)
    
    bpy.types.Object.show_stereo_window = bpy.props.BoolProperty(
        attr="show_stereo_window", 
        name="show_stereo_window", 
        default=True)
        
    bpy.types.Object.show_near_far_plane = bpy.props.BoolProperty(
        attr="show_near_far_plane", 
        name="show_near_far_plane", 
        default=False)    
    
    bpy.types.Object.camera_type = bpy.props.EnumProperty(
        attr="camera_type",
        items=( ("OFFAXIS", "Off-Axis", "Default (best stereo result)"),
                ("CONVERGE", "Converge", "Toe-In Camera (could create uncomfortable vertical parallax)"),
                ("PARALLEL", "Parallel", "Simple stereo camera (zero parallax at infinity)")),
        name="camera_type", 
        description="", 
        default="OFFAXIS")

    #
    # draw the gui
    #
    def draw(self, context):
        layout = self.layout

        # get the custom stereo camera properties
        camera = context.scene.camera
        tmp_cam = context.scene.camera
        if(camera.name[:2]=="L_" or camera.name[:2]=="R_"):
            camera = bpy.data.objects[camera.name[2:]]

        # cam separation input
        row = layout.row()
        row.prop(camera, "camera_type", text="Stereo Camera Type", expand=True)

        # cam separation input
        row = layout.row()
        row.prop(camera, "stereo_camera_separation", text="Camera Separation")

        # OFF-AXIS:
        if(camera.camera_type == "OFFAXIS"):
            # focal distance input
            row = layout.row()
            row.prop(camera, "stereo_focal_distance", text="Zero Parallax")
            
            # show the zero parallax (stereo window as a plane) or not
            col = layout.column(align=True)
            col.prop(camera, "show_stereo_window", text="Show Stereo Window (Zero Parallax)")
            #col.separator()
    
            # boolean: show the near- and far plane or not
            col = layout.column(align=True)
            col.prop(camera, "show_near_far_plane", text="Auto set of Near- and Farplane")
            if(camera.show_near_far_plane):
                split = layout.split()
                
                # near- and far plane distance input
                col = split.column(align=True)
                col.label(text="Max Parallax:")
                col.prop(camera, "max_parallax", text="Angle")
    
                # user parameters for viewer distance and screen resolution          
                col = split.column(align=True)
                col.active = camera.show_near_far_plane
                col.prop(camera, "viewer_distance", text="Dist") # viewer distance in inch
                col.prop(camera, "screen_ppi", text="PPI") # pixel per inch
            
                # show the parallax info
                col = layout.column(align=True)
                col.active = camera.show_near_far_plane
        
        # CONVERGE (Toe-In):
        if(camera.camera_type == "CONVERGE"):
            # focal distance input
            row = layout.row()
            row.prop(camera, "stereo_focal_distance", text="Zero Parallax")
            
            # show the zero parallax (stereo window as a plane) or not
            col = layout.column(align=True)
            col.prop(camera, "show_stereo_window", text="Show Stereo Window (Zero Parallax)")
            #col.separator()
        
        # PARALLEL:
        if(camera.camera_type == "PARALLEL"):
            pass
    
        # 'Set Stereo Camera' button
        row = layout.row()
        row.operator('stereocamera.set_stereo_camera')
        
        # Set active render camera
        col = layout.column(align=True)
        col.separator()
        col.label(text="Active Render Camera: "+tmp_cam.name)

        # Set active render camera
        row = layout.row(align=True) 
        row.operator('stereocamera.set_left_as_render_cam')
        row.operator('stereocamera.set_center_as_render_cam')
        row.operator('stereocamera.set_right_as_render_cam')  
        
        # Create Left and Right Scene
        row = layout.row()
        row.operator('stereocamera.create_left_right_scene')



#
# 'Set Left Camera' Operator
#
class OBJECT_OT_set_left_render_camera(bpy.types.Operator):
    bl_label = 'Left'
    bl_idname = 'stereocamera.set_left_as_render_cam'
    bl_description = 'Set Left as active Render Camera'
    bl_options = {'REGISTER', 'UNDO'}

    # on mouse up:
    def invoke(self, context, event):
        camera = bpy.context.scene.camera
        if(camera.name[:2]=="L_" or camera.name[:2]=="R_"):
            center_cam = bpy.data.objects[camera.name[2:]]
        else:
            center_cam = camera
            
        active_cam = bpy.data.objects['L_'+center_cam.name]
        bpy.context.scene.camera = active_cam
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = active_cam
        active_cam.select = True
        
        return {'FINISHED'}



#
# 'Set Center Camera' Operator
#
class OBJECT_OT_set_center_render_camera(bpy.types.Operator):
    bl_label = 'Center'
    bl_idname = 'stereocamera.set_center_as_render_cam'
    bl_description = 'Set Center as active Render Camera'
    bl_options = {'REGISTER', 'UNDO'}
    
    # on mouse up:
    def invoke(self, context, event):
        camera = bpy.context.scene.camera
        if(camera.name[:2]=="L_" or camera.name[:2]=="R_"):
            center_cam = bpy.data.objects[camera.name[2:]]
        else:
            center_cam = camera
            
        active_cam = bpy.data.objects[center_cam.name]
        bpy.context.scene.camera = active_cam
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = active_cam
        active_cam.select = True
        
        return {'FINISHED'}



#
# 'Set Right Camera' Operator
#
class OBJECT_OT_set_right_render_camera(bpy.types.Operator):
    bl_label = 'Right'
    bl_idname = 'stereocamera.set_right_as_render_cam'
    bl_description = 'Set Right as active Render Camera'
    bl_options = {'REGISTER', 'UNDO'}
    
    # on mouse up:
    def invoke(self, context, event):
        camera = bpy.context.scene.camera
        if(camera.name[:2]=="L_" or camera.name[:2]=="R_"):
            center_cam = bpy.data.objects[camera.name[2:]]
        else:
            center_cam = camera
            
        active_cam = bpy.data.objects['R_'+center_cam.name]
        bpy.context.scene.camera = active_cam
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = active_cam
        active_cam.select = True
        
        return {'FINISHED'}


#
# Operator 'Set Stereo Camera'
#
class OBJECT_OT_set_stereo_camera(bpy.types.Operator):
    bl_label = 'Set Stereo Camera'
    bl_idname = 'stereocamera.set_stereo_camera'
    bl_description = 'Setup the Stereoscopic Camera'
    bl_options = {'REGISTER', 'UNDO'}

    # call the operator 'Set Stereo Camera'
    def execute(self, context):

        # do the stereoscopic calculation
        self.stereoscopic_calculation(context)

        # do the settings (add or set the left/right camera)
        self.set_left_right_stereo_camera(context)

        return {'FINISHED'}

    #
    # Stereoscopic calculation
    #
    def stereoscopic_calculation(self, context):
        
        import math
        import bpy
    
        # get the custom stereo camera properties
        camera = context.scene.camera
        if(camera.name[:2]=="L_" or camera.name[:2]=="R_"):
            camera = bpy.data.objects[camera.name[2:]]
            
        stereo_base = camera.stereo_camera_separation/1000 # 1/1000 Blender Units
        focal_dist = camera.stereo_focal_distance
        camera_fov = camera.data.angle
        theta = camera.max_parallax
        viewer_dist = camera.viewer_distance
        ppi = camera.screen_ppi
    
    	# get the horizonal render resolution
        render_width = context.scene.render.resolution_x
        render_factor = bpy.context.scene.render.resolution_percentage/100
        render_width = render_width * render_factor
    
        # OFF-AXIS:
        if(camera.camera_type=="OFFAXIS"):
            # calculate delta in pixel at zero parallax:
            camera.stereo_camera_delta = (render_width*stereo_base)/(2*focal_dist*math.tan(camera_fov/2))
            # calculate blenders camera shift_x depending on render resolution and delta in pixel:
            camera.stereo_camera_shift_x = camera.stereo_camera_delta/render_width

            ### DEUBUG ###
            print('')
            print("### Stereoscopic Off-Axis shift ###")
            print("Render Width: "+str(render_width)+" Pixel")
            print("Stereo Base: "+str(stereo_base)+" B.U.")
            print("Focal Distance: "+str(focal_dist)+" B.U.")
            print("Camera Angle FoV: "+str(camera_fov)+ " Radians"+" (or "+str(math.degrees(camera_fov))+" Degree)")
            print("Delta Zero Parallax: "+str(camera.stereo_camera_delta)+ " Pixel")
            print('')
            #### DEBUG ###
           
            if(camera.show_near_far_plane):
                # calculate the maximum parallax in pixel for the given angle
                alpha = math.radians(theta/2)
                beta = math.radians(90-alpha)
                camera.max_disparity = ((math.sin(alpha))*viewer_dist) / ((math.sin(beta)))
                camera.max_disparity = (camera.max_disparity*2)*ppi
                
                ### DEBUG ###
                print("Max. Delta at Near- and Farplane: "+str(camera.max_disparity)+" Pixel")
                ### DEBUG ###

                # calculate near- and farplane distance
                delta = camera.stereo_camera_delta
                disparity = camera.max_disparity
                camera.near_plane_distance = ( ((stereo_base*render_width)/(delta+disparity)) / (math.tan(camera_fov/2)) ) / 2
                ### DEBUG ###
                print("Nearplane Distance: "+str(camera.near_plane_distance)+" B.U.")
                ### DEBUG ###
                if(delta>disparity):
                    camera.far_plane_distance = ( ((stereo_base*render_width)/(delta-disparity)) / (math.tan(camera_fov/2)) ) / 2
                    ### DEBUG ###
                    print("Farplane Distance: "+str(camera.far_plane_distance)+" B.U.")
                    print('')
                    ### DEBUG ###
                else:
                    camera.far_plane_distance = camera.data.clip_end # farplane at infinity
                    ### DEBUG ###
                    print("Farplane Distance: > Camera Clip End at "+str(camera.data.clip_end)+" B.U.")
                    print('')
                    ### DEBUG ###
            
        if(camera.camera_type=="CONVERGE"):
            # calculate (inward-)rotation angle of the left and right camera
            camera.toein_angle = math.degrees( math.atan2((stereo_base/2), focal_dist) )
            ### DEBUG ###
            print('')
            print('### Stereoscopic Converge/Toein camera ###')
            print("Stereo Base: "+str(stereo_base)+" B.U.")
            print("Focal Distance: "+str(focal_dist)+" B.U.")
            print("Camera Angle FoV: "+str(camera_fov)+ " Radians"+' (or '+str(math.degrees(camera_fov))+' Degree)')
            print("Toein Angle: "+str(camera.toein_angle)+' Degree (each camera)')
            print('')
            ### DEBUG ###
            
        if(camera.camera_type=="PARALLEL"):
            pass
            
        return {'FINISHED'}
    
    #
    # Add or Set the Left- and right Camera
    #
    def set_left_right_stereo_camera(op, context):

        import math
        import bpy
    
        tmp_camera = bpy.context.scene.camera 
        if(tmp_camera.name[:2]=="L_" or tmp_camera.name[:2]=="R_"):
            center_cam = bpy.data.objects[tmp_camera.name[2:]]
        else:
            center_cam = tmp_camera
        active_cam = bpy.data.objects[center_cam.name]
        bpy.context.scene.camera = active_cam
        camera = bpy.context.scene.camera 
    
        # check for existing stereocamera objects
        left_cam_exists = 0
        right_cam_exists = 0
        zero_plane_exists = 0
        near_plane_exists = 0
        far_plane_exists = 0
        scn = bpy.context.scene
        for ob in scn.objects:
            if(ob.name == "L_"+center_cam.name):
                left_cam_exists = 1
            if(ob.name == "R_"+center_cam.name):
                right_cam_exists = 1
            if(ob.name == "SW_"+center_cam.name):
                zero_plane_exists = 1
            if(ob.name == "NP_"+center_cam.name):
                near_plane_exists = 1
            if(ob.name == "FP_"+center_cam.name):
                far_plane_exists = 1
    
        # add a new or (if exists) get the left camera
        if(left_cam_exists==0):
            left_cam = bpy.data.cameras.new('L_'+center_cam.name)
            left_cam_obj = bpy.data.objects.new('L_'+center_cam.name, left_cam)
            scn.objects.link(left_cam_obj)
        else:
            left_cam_obj = bpy.data.objects['L_'+center_cam.name]  
            left_cam = left_cam_obj.data 
    
        # add a new or (if exists) get the right camera
        if(right_cam_exists==0):
            right_cam = bpy.data.cameras.new('R_'+center_cam.name)
            right_cam_obj = bpy.data.objects.new('R_'+center_cam.name, right_cam)
            scn.objects.link(right_cam_obj)    
        else:
            right_cam_obj = bpy.data.objects['R_'+center_cam.name]
            right_cam = right_cam_obj.data


        # add a new or (if exists) get the zero parallax plane
        if(zero_plane_exists==0):
            add_plane = bpy.ops.mesh.primitive_plane_add
            add_plane(location=(0,0,0), layers=(True, False, False,False, False, False, False, False, False, False, False, False,False, False, False, False, False, False, False, False))
            zero_plane_obj = bpy.context.active_object
            zero_plane_obj.name = 'SW_'+center_cam.name
        else:
            zero_plane_obj = bpy.data.objects['SW_'+center_cam.name]
        
        # add a new or (if exists) get the near plane
        if(near_plane_exists==0):
            add_plane = bpy.ops.mesh.primitive_plane_add
            add_plane(location=(0,0,0), layers=(True, False, False,False, False, False, False, False, False, False, False, False,False, False, False, False, False, False, False, False))
            near_plane_obj = bpy.context.active_object
            near_plane_obj.name = 'NP_'+center_cam.name
        else:
            near_plane_obj = bpy.data.objects['NP_'+center_cam.name]
        
      	# add a new or (if exists) get the far plane
        if(far_plane_exists==0):
            add_plane = bpy.ops.mesh.primitive_plane_add
            add_plane(location=(0,0,0), layers=(True, False, False,False, False, False, False, False, False, False, False, False,False, False, False, False, False, False, False, False))
            far_plane_obj = bpy.context.active_object
            far_plane_obj.name = 'FP_'+center_cam.name
        else:
            far_plane_obj = bpy.data.objects['FP_'+center_cam.name]         

        # OFF-AXIS:
        if(camera.camera_type=="OFFAXIS"):
            
            # set the left camera
            left_cam.angle = center_cam.data.angle
            left_cam.clip_start = center_cam.data.clip_start
            left_cam.clip_end = center_cam.data.clip_end
            left_cam.dof_distance = center_cam.data.dof_distance
            left_cam.dof_object = center_cam.data.dof_object
            left_cam.shift_y = center_cam.data.shift_y
            left_cam.shift_x = (camera.stereo_camera_shift_x/2)+center_cam.data.shift_x
            left_cam_obj.location = -(camera.stereo_camera_separation/1000)/2,0,0
            left_cam_obj.rotation_euler = (0.0,0.0,0.0) # reset
            left_cam_obj.data.cycles.aperture_blades = bpy.data.objects["Camera"].data.cycles.aperture_blades
            left_cam_obj.data.cycles.aperture_size = bpy.data.objects["Camera"].data.cycles.aperture_size
            left_cam_obj.data.cycles.aperture_rotation = bpy.data.objects["Camera"].data.cycles.aperture_rotation
            left_cam_obj.data.cycles.aperture_type = bpy.data.objects["Camera"].data.cycles.aperture_type 
#            left_cam_obj.data.cycles.aperture_ratio = bpy.data.objects["Camera"].data.cycles.aperture_ratio
#            left_cam_obj.animation_data.action = bpy.data.objects["Camera"].animation_data.action

            # set the right camera
            right_cam.angle = center_cam.data.angle
            right_cam.clip_start = center_cam.data.clip_start
            right_cam.clip_end = center_cam.data.clip_end
            right_cam.dof_distance = center_cam.data.dof_distance
            right_cam.dof_object = center_cam.data.dof_object
            right_cam.shift_y = center_cam.data.shift_y
            right_cam.shift_x = -(camera.stereo_camera_shift_x/2)+center_cam.data.shift_x
            right_cam_obj.location = (camera.stereo_camera_separation/1000)/2,0,0
            right_cam_obj.rotation_euler = (0.0,0.0,0.0) # reset
            right_cam_obj.data.cycles.aperture_blades = bpy.data.objects["Camera"].data.cycles.aperture_blades
            right_cam_obj.data.cycles.aperture_size = bpy.data.objects["Camera"].data.cycles.aperture_size
            right_cam_obj.data.cycles.aperture_rotation = bpy.data.objects["Camera"].data.cycles.aperture_rotation
            right_cam_obj.data.cycles.aperture_type = bpy.data.objects["Camera"].data.cycles.aperture_type 
#            right_cam_obj.data.cycles.aperture_ratio = bpy.data.objects["Camera"].data.cycles.aperture_ratio
#            right_cam_obj.animation_data.action =  bpy.data.objects["Camera"].animation_data.action
    
            # set the planes
            zero_plane_obj.location = (0,0,-camera.stereo_focal_distance)
            near_plane_obj.location = (0,0,-camera.near_plane_distance)
            far_plane_obj.location = (0,0,-camera.far_plane_distance)
    		
            # set the 'real size' of the planes (frustum) 
            scene = bpy.context.scene
            render_width = scene.render.resolution_x
            render_height = scene.render.resolution_y
            camera_fov = math.degrees(center_cam.data.angle)
            alpha = math.radians(camera_fov/2)
            beta  = math.radians(90-(camera_fov/2))
            # stereo window:
            sw_x = ((math.sin(alpha))*camera.stereo_focal_distance) / ((math.sin(beta)))
            sw_y = (render_height * sw_x) / render_width
            zero_plane_obj.scale[0] = (sw_x)
            zero_plane_obj.scale[1] = (sw_y)
            # near plane:
            sw_x = ((math.sin(alpha))*camera.near_plane_distance) / ((math.sin(beta)))
            sw_y = (render_height * sw_x) / render_width
            near_plane_obj.scale[0] = (sw_x)
            near_plane_obj.scale[1] = (sw_y)   
            # far plane:
            sw_x = ((math.sin(alpha))*camera.far_plane_distance) / ((math.sin(beta)))
            sw_y = (render_height * sw_x) / render_width
            far_plane_obj.scale[0] = (sw_x)
            far_plane_obj.scale[1] = (sw_y)   
                
            # do not render the planes
            zero_plane_obj.hide_render = True
            near_plane_obj.hide_render = True
            far_plane_obj.hide_render = True
            
            # show the zero-parallax-plane (stereo window) or not
            if(camera.show_stereo_window):
                zero_plane_obj.hide = False
            else:
                zero_plane_obj.hide = True
    
            # show the near- and far-plane or not
            if(camera.show_near_far_plane):
                near_plane_obj.hide = False
                far_plane_obj.hide = False
            else:
                near_plane_obj.hide = True
                far_plane_obj.hide = True


            # add the left/right camera and zero-parallax-plane as child
            left_cam_obj.parent = center_cam
            right_cam_obj.parent = center_cam
            zero_plane_obj.parent = center_cam
            near_plane_obj.parent = center_cam
            far_plane_obj.parent = center_cam  
    
        # CONVERGE (Toe-in):
        if(camera.camera_type=="CONVERGE"):
            # set the left camera
            left_cam.angle = center_cam.data.angle
            left_cam.clip_start = center_cam.data.clip_start
            left_cam.clip_end = center_cam.data.clip_end
            left_cam.dof_distance = center_cam.data.dof_distance
            left_cam.dof_object = center_cam.data.dof_object
            left_cam.shift_y = center_cam.data.shift_y
            left_cam.shift_x = center_cam.data.shift_x # reset
            left_cam_obj.location = -(camera.stereo_camera_separation/1000)/2,0,0
            left_cam_obj.rotation_euler = (0.0,-math.radians(camera.toein_angle),0.0)
            left_cam_obj.data.cycles.aperture_blades = bpy.data.objects["Camera"].data.cycles.aperture_blades
            left_cam_obj.data.cycles.aperture_size = bpy.data.objects["Camera"].data.cycles.aperture_size
            left_cam_obj.data.cycles.aperture_rotation = bpy.data.objects["Camera"].data.cycles.aperture_rotation
            left_cam_obj.data.cycles.aperture_type = bpy.data.objects["Camera"].data.cycles.aperture_type 
#            left_cam_obj.data.cycles.aperture_ratio = bpy.data.objects["Camera"].data.cycles.aperture_ratio
    
            # set the right camera
            right_cam.angle = center_cam.data.angle
            right_cam.clip_start = center_cam.data.clip_start
            right_cam.clip_end = center_cam.data.clip_end
            right_cam.dof_distance = center_cam.data.dof_distance
            right_cam.dof_object = center_cam.data.dof_object
            right_cam.shift_y = center_cam.data.shift_y
            right_cam.shift_x = center_cam.data.shift_x # reset
            right_cam_obj.location = (camera.stereo_camera_separation/1000)/2,0,0
            right_cam_obj.rotation_euler = (0.0,math.radians(camera.toein_angle),0.0)
            right_cam_obj.data.cycles.aperture_blades = bpy.data.objects["Camera"].data.cycles.aperture_blades
            right_cam_obj.data.cycles.aperture_size = bpy.data.objects["Camera"].data.cycles.aperture_size
            right_cam_obj.data.cycles.aperture_rotation = bpy.data.objects["Camera"].data.cycles.aperture_rotation
            right_cam_obj.data.cycles.aperture_type = bpy.data.objects["Camera"].data.cycles.aperture_type 
#            right_cam_obj.data.cycles.aperture_ratio = bpy.data.objects["Camera"].data.cycles.aperture_ratio
    
            # set the zero parallax plane
            zero_plane_obj.location = (0,0,-camera.stereo_focal_distance)
    		
            # set the 'real size' of the plane (frustum) 
            scene = bpy.context.scene
            render_width = scene.render.resolution_x
            render_height = scene.render.resolution_y
            camera_fov = math.degrees(center_cam.data.angle)
            alpha = math.radians(camera_fov/2)
            beta  = math.radians(90-(camera_fov/2))
    		# stereo window:
            sw_x = ((math.sin(alpha))*camera.stereo_focal_distance) / ((math.sin(beta)))
            sw_y = (render_height * sw_x) / render_width
            zero_plane_obj.scale[0] = (sw_x)
            zero_plane_obj.scale[1] = (sw_y)
                
            # do not render the planes
            zero_plane_obj.hide_render = True
            
            # show the zero-parallax-plane (stereo window) or not
            if(camera.show_stereo_window):
                zero_plane_obj.hide = False
            else:
                zero_plane_obj.hide = True
    
            # do not show the near- and far-plane
            near_plane_obj.hide = True
            far_plane_obj.hide = True
    
            # add the left/right camera and zero-parallax-plane as child
            left_cam_obj.parent = center_cam
            right_cam_obj.parent = center_cam
            zero_plane_obj.parent = center_cam

        # PARALLEL:
        if(camera.camera_type=="PARALLEL"):
            # set the left camera
            left_cam.angle = center_cam.data.angle
            left_cam.clip_start = center_cam.data.clip_start
            left_cam.clip_end = center_cam.data.clip_end
            left_cam.dof_distance = center_cam.data.dof_distance
            left_cam.dof_object = center_cam.data.dof_object
            left_cam.shift_y = center_cam.data.shift_y
            left_cam.shift_x = center_cam.data.shift_x # reset
            left_cam_obj.location = -(camera.stereo_camera_separation/1000)/2,0,0
            left_cam_obj.rotation_euler = (0.0,0.0,0.0) # reset
            left_cam_obj.data.cycles.aperture_blades = bpy.data.objects["Camera"].data.cycles.aperture_blades
            left_cam_obj.data.cycles.aperture_size = bpy.data.objects["Camera"].data.cycles.aperture_size
            left_cam_obj.data.cycles.aperture_rotation = bpy.data.objects["Camera"].data.cycles.aperture_rotation
            left_cam_obj.data.cycles.aperture_type = bpy.data.objects["Camera"].data.cycles.aperture_type 
#            left_cam_obj.data.cycles.aperture_ratio = bpy.data.objects["Camera"].data.cycles.aperture_ratio

    
            # set the right camera
            right_cam.angle = center_cam.data.angle
            right_cam.clip_start = center_cam.data.clip_start
            right_cam.clip_end = center_cam.data.clip_end
            right_cam.dof_distance = center_cam.data.dof_distance
            right_cam.dof_object = center_cam.data.dof_object
            right_cam.shift_y = center_cam.data.shift_y
            right_cam.shift_x = center_cam.data.shift_x # reset
            right_cam_obj.location = (camera.stereo_camera_separation/1000)/2,0,0
            right_cam_obj.rotation_euler = (0.0,0.0,0.0) # reset
            right_cam_obj.data.cycles.aperture_blades = bpy.data.objects["Camera"].data.cycles.aperture_blades
            right_cam_obj.data.cycles.aperture_size = bpy.data.objects["Camera"].data.cycles.aperture_size
            right_cam_obj.data.cycles.aperture_rotation = bpy.data.objects["Camera"].data.cycles.aperture_rotation
            right_cam_obj.data.cycles.aperture_type = bpy.data.objects["Camera"].data.cycles.aperture_type 
#            right_cam_obj.data.cycles.aperture_ratio = bpy.data.objects["Camera"].data.cycles.aperture_ratio

            # do not show any planes
            zero_plane_obj.hide = True
            near_plane_obj.hide = True
            far_plane_obj.hide = True
                
            # do not render the planes
            zero_plane_obj.hide_render = True
            near_plane_obj.hide_render = True
            far_plane_obj.hide_render = True
    
            # add the left/right camera as child
            left_cam_obj.parent = center_cam
            right_cam_obj.parent = center_cam                    

        # select the center camera (object mode)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.camera = tmp_camera
        bpy.context.scene.objects.active = tmp_camera
        tmp_camera.select = True
        
        return {'FINISHED'} 


#
# 'Create L and R Scene' Operator
#
class OBJECT_OT_create_left_right_scene(bpy.types.Operator):
    bl_label = 'Create L and R Scene'
    bl_idname = 'stereocamera.create_left_right_scene'
    bl_description = 'Create Left and Right Camera Scene'
    bl_options = {'REGISTER', 'UNDO'}
    
    # on mouse up:
    def execute(self, context):
        camera = bpy.context.scene.camera
        
        # check for existing cameras
        scn = bpy.context.scene
        left_cam_exists = 0
        right_cam_exists = 0
        for ob in scn.objects:
            if(ob.name[:2]=="L_"):
                left_cam_exists = 1
            if(ob.name[:2]=="R_"):
                right_cam_exists = 1
        
        # ok, call the function
        if(left_cam_exists and right_cam_exists):
            self.create_scenes(context)
                    
        return {'FINISHED'}
    
    #
    # create new left and right camera scene
    #
    def create_scenes(self, context):
        
        import bpy
#        from bge.logic import getCurrentScene
        
        center_scene = context.scene
        center_cam_name = context.scene.camera.name
        name_scene_left = context.scene.name + "_L" 
        name_scene_right = context.scene.name + "_R"

        # We should never have to delete the left and right camera scenes, as that should have been taken care of before we got to this function.
#        # delete left and right camera scenes if exists
#        try:
#            bpy.data.scenes.remove(bpy.data.scenes[name_scene_left])
#            bpy.data.scenes.remove(bpy.data.scenes[name_scene_right])
#        except:
#            pass
            
        # Create Left Scene
        bpy.ops.scene.new(type='LINK_OBJECTS')
        left_scene = context.scene
        left_scene.name = name_scene_left
        left_scene.camera = bpy.data.objects["L_"+center_cam_name]
        left_scene.background_set = center_scene

        # Create Right Scene
        bpy.ops.scene.new(type='LINK_OBJECTS')
        right_scene = context.scene
        right_scene.name = name_scene_right
        right_scene.camera = bpy.data.objects["R_"+center_cam_name]
        right_scene.background_set = center_scene

        # Loop through all the objects in the left scene. Delete all objects that start with "stereoimageR".
        # Make sure all objects that start with "stereoimageL" are visible and are able to be rendered.
        for object in left_scene.objects:
            if (object.name.startswith("stereoimageR")):
                left_scene.objects.unlink(object)
            if (object.name.startswith("stereoimageL")):
                object.hide = 0
                object.hide_select = 1
                object.hide_render = 0

        # Loop through all the objects in right scene. Delete all objects that start with "stereoimageL".
        # Make sure all objects that start with "stereoimageR" are visible and are able to be rendered.
        for object in right_scene.objects:
            if (object.name.startswith("stereoimageL")):
                right_scene.objects.unlink(object)
            if (object.name.startswith("stereoimageR")):
                object.hide = 0
                object.hide_select = 1
                object.hide_render = 0

        self.report({'INFO'}, "Created scene '" + name_scene_left + "'")
        self.report({'INFO'}, "Created scene '" + name_scene_right + "'")
        self.report({'INFO'}, "Stereoscopic scenes successful!")


        # back to the center scene
        context.screen.scene = center_scene
    
        return {'FINISHED'}



#
# Stereoscopic Node presets
#    
class NODE_EDITOR_PT_preset(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_label = "Stereoscopic presets"

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
            row.prop(scn, 'stereo_comp_presets')
        
            row = layout.row()
            row.operator('stereocamera.add_stereo_node_preset')

            row = layout.row()
            row.prop(scn, 'stereo_comp_show_anaglyph_preview')
            row.enabled = scn.stereo_comp_presets != "2DNODES-ONE"

            row = layout.row()
            row.prop(scn, 'stereo_comp_replace_current_nodes')

            row = layout.row()
            row.prop(scn, 'stereo_comp_bkgd_image_L')

            row = layout.row()
            row.prop(scn, 'stereo_comp_bkgd_image_R')

#            row = layout.row()
#            row.operator('stereocamera.remove_stereo_scenes')

        else:
            layout = self.layout
            row = layout.row() 
            row.label(text="Info: ")
            row = layout.row() 
            row.label(text="Select 'COMPOSITING'")
            row = layout.row()
            row.label(text="and check 'Use Nodes'")


#
# Operator 'Add nodes'
#
class OBJECT_OT_add_stereo_node_preset(bpy.types.Operator):
    bl_label = 'Add nodes'
    bl_idname = 'stereocamera.add_stereo_node_preset'
    bl_description = 'Adds a stereoscopic node preset'

#    def execute(self, context):
#        self.add_preset(self, context)
#        return {'FINISHED'}

    # on mouse up:
    def invoke(self, context, event):

        # add the selected preset
        self.add_preset(context)

        return {'FINISHED'}

    #
    # add the node presets
    #
    def add_preset(self, context):
        
        import bpy
        import re
        
        scene = bpy.context.scene
        
        tree = scene.node_tree
        
        render_factor = bpy.context.scene.render.resolution_percentage/100
        
        res_x = int(scene.render.resolution_x * render_factor)
        res_y = int(scene.render.resolution_y * render_factor)

        #
        # Left and Right
        #
        # Custom option created by jjb
        bpy.ops.file.make_paths_relative() # Hack to automatically make all paths relative. Because Blender doesn't always honor this.
        if (scene.stereo_comp_replace_current_nodes == True):
             for i in tree.nodes:
                  tree.nodes.remove(i)

        useImageBackground = 0
        if len(scene.stereo_comp_bkgd_image_L.strip()) > 0 or len(scene.stereo_comp_bkgd_image_R.strip()) > 0:
            useImageBackground = 1

        if (scene.stereo_comp_presets == "2DNODES-ONE"):
            if useImageBackground == 0: 
                # Do the simplest render possible
                originalSceneName = bpy.context.screen.scene.name 
                center_render_layer = tree.nodes.new('CompositorNodeRLayers')
                center_render_layer.location = (0,280)
                try: 
                    center_render_layer.scene = bpy.data.scenes[originalSceneName]
                except:
                    pass

                # We need to have an output node. So create it.
                file_output_node_center = tree.nodes.new('CompositorNodeOutputFile')
                file_output_node_center.file_slots.clear()
            
                if originalSceneName.endswith("_L"):
                    file_output_node_center.base_path = "//_LEFT"
                    file_output_node_center.file_slots.new("limg")                
                elif originalSceneName.endswith("_R"):
                    file_output_node_center.base_path = "//_RIGHT"
                    file_output_node_center.file_slots.new("rimg")                
                else:
                    file_output_node_center.base_path = "//_CENTER"
                    file_output_node_center.file_slots.new("cimg")

                file_output_node_center.location = (300, 600) 

                # Comp output
                composite_node = tree.nodes.new('CompositorNodeComposite')
                composite_node.location = (300, 250)
    
                # Hook them all up
                tree.links.new(center_render_layer.outputs[0],file_output_node_center.inputs[0])        
                tree.links.new(center_render_layer.outputs[0],composite_node.inputs[0])        
            else:
                # Make a simple scene with a static background
                originalSceneName = bpy.context.screen.scene.name 
                center_render_layer = tree.nodes.new('CompositorNodeRLayers')
                center_render_layer.location = (-400,280)
                try: 
                    center_render_layer.scene = bpy.data.scenes[originalSceneName]
                except:
                    pass

                # We need to have an output node. So create it.
                file_output_node_center = tree.nodes.new('CompositorNodeOutputFile')
                file_output_node_center.file_slots.clear()
            
                # We need an image in the background.
                image_background = tree.nodes.new('CompositorNodeImage')
                image_background.location = (-400,-200)

                # We need to scale the image to match the render size.
                image_background_scale = tree.nodes.new('CompositorNodeScale')
                image_background_scale.location = (-400,0)
                image_background_scale.space = 'RENDER_SIZE'
                image_background_scale.frame_method = 'FIT'
                
                # We need an alphaover.
                alphaoverBackground = tree.nodes.new('CompositorNodeAlphaOver')
                alphaoverBackground.location = (-200,370) 
                alphaoverBackground.premul = 0.5

                if originalSceneName.endswith("_L"):
                    file_output_node_center.base_path = "//_LEFT"
                    file_output_node_center.file_slots.new("limg")
                    try:
                        t = bpy.data.images.load(scene.stereo_comp_bkgd_image_L)
                        image_background.image = t
                    except:
                        pass
                
                elif originalSceneName.endswith("_R"):
                    file_output_node_center.base_path = "//_RIGHT"
                    file_output_node_center.file_slots.new("rimg")
                    try:
                        t = bpy.data.images.load(scene.stereo_comp_bkgd_image_R)
                        image_background.image = t
                    except:
                        pass               
                else:
                    file_output_node_center.base_path = "//_CENTER"
                    file_output_node_center.file_slots.new("cimg")
                    try:
                        t = bpy.data.images.load(scene.stereo_comp_bkgd_image_L)
                        image_background.image = t
                    except:
                        pass

                

                file_output_node_center.location = (300, 600) 

                # Comp output
                composite_node = tree.nodes.new('CompositorNodeComposite')
                composite_node.location = (300, 250)
    
                # Hook them all up
                tree.links.new(image_background.outputs[0],image_background_scale.inputs[0])
                tree.links.new(image_background_scale.outputs[0],alphaoverBackground.inputs[1])
                tree.links.new(center_render_layer.outputs[0],alphaoverBackground.inputs[2])        
                tree.links.new(alphaoverBackground.outputs[0],file_output_node_center.inputs[0])        
                tree.links.new(alphaoverBackground.outputs[0],composite_node.inputs[0])        

        my_stereo_comp_selection = scene.stereo_comp_presets # We need to store this, as scene.stereo_comp_presets somehow gets internally reset by the time we need its value further down the line.

        if (my_stereo_comp_selection == "3DNODES-ALL") or (my_stereo_comp_selection == "3DNODES-ONE"):
            # First, wipe out all of the _L and _R scenes that exist.
            # We do this here so complex scenes with CUDA-enabled video cards don't crash (Blender tends to crash if you add/delete scenes piecemeal?)
            OBJECT_OT_remove_stereo_scenes.remove_stereo_scenes(self, context)

            # First, recreate ALL of the L&R images for ALL scenes that don't have a _L or _R suffix.
            # Find out what the names for all non _L and _R scenes are.
            # First, get a list of all of our stereo scenes.
            scene_list_raw=[] # The raw scene list
            for scene in bpy.data.scenes:
                 scene_list_raw.append(scene.name) 
            scene_list=[] # Center name only
            maxOverlayNum = -1
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
                      if (matchIndex == 1):
                           sceneC = myMatch		         
                      matchIndex = matchIndex + 1		     
                 if not sceneC == "" and not sceneC.endswith("_L") and not sceneC.endswith("_R"): # It's legit! (We should never get _L and _R here -- those should be wiped out)
                      maxOverlayNum = testOverlayNum
                      numOfOverlaysFound = numOfOverlaysFound + 1
                      scene_list.append(sceneC)
                 testOverlayNum = testOverlayNum + 1
            # Now create the _L and _R scenes for everything in scene_list.
            originalSceneName = bpy.context.screen.scene.name # We need to remember what scene we were on.
            for currentScene in scene_list:            
                  print("CURRENT SCENE: " + currentScene)
                  bpy.context.screen.scene=bpy.data.scenes[currentScene] # To make the _L and _R camera scenes, we need to actually be *on* the scene.
                  camera = bpy.context.scene.camera
                  bpy.ops.object.select_all(action='DESELECT')
                  bpy.context.scene.objects.active = camera
                  camera.select = True
                  # check for existing cameras
                  scn = bpy.context.scene
                  left_cam_exists = 0
                  right_cam_exists = 0
                  for ob in scn.objects:
                       if(ob.name[:2]=="L_"):
                            left_cam_exists = 1
                       if(ob.name[:2]=="R_"):
                            right_cam_exists = 1
            
                  # OK, call the function
                  if(left_cam_exists and right_cam_exists):
                       OBJECT_OT_create_left_right_scene.create_scenes(self, context)
    
            bpy.context.screen.scene=bpy.data.scenes[originalSceneName] # Go back to the scene we were originally on.

            # We also need to assign the screen layouts SBS LEFT and SBS RIGHT so that they're using the stereo version
            # of originalSceneName (assuming it exists).
            for screen in bpy.data.screens:
                if (screen.name == "SBS LEFT"):
                    for scene in bpy.data.scenes:
                        if (scene.name == (originalSceneName + "_L")):
                            screen.scene = scene
                            break
                if (screen.name == "SBS RIGHT"):
                    for scene in bpy.data.scenes:
                        if (scene.name == (originalSceneName + "_R")):
                            screen.scene = scene
                            break

            # OK, we're done creating all of our stereo scenes. Let's go ahead with making nodes.
    
            # First, get a list of all of our stereo scenes.
            scene_list_raw=[] # The raw scene list

            if (my_stereo_comp_selection == "3DNODES-ONE"):
                scene_list_raw.append(originalSceneName)
                scene_list_raw.append(originalSceneName + "_L")
                scene_list_raw.append(originalSceneName + "_R")
            elif (my_stereo_comp_selection == "3DNODES-ALL"):
                for scene in bpy.data.scenes:
                     scene_list_raw.append(scene.name) 
            scene_list=[] # Legit scenes (center name only)
            maxOverlayNum = -1
            testOverlayNum = 0
            numOfOverlaysFound = 0
            while testOverlayNum <= 999:
                 sPrefix = "%03d ." % (testOverlayNum)
                 regex = re.compile(sPrefix)
                 matches = [string for string in scene_list_raw if re.match(regex, string)]         
                 matchIndex=1		 
                 iThisIsLegit = 0 # guilty until proven innocent
                 sceneC = ""
                 for myMatch in matches: 		 
                      print("Matches found for '" + sPrefix + "': " + myMatch)
                      if (matchIndex == 1):
                           sceneC = myMatch		         
                      if (matchIndex == 2) and (myMatch.endswith("_L")):
                           iThisIsLegit = iThisIsLegit + 1
                      if (matchIndex == 3) and (myMatch.endswith("_R")):
                           iThisIsLegit = iThisIsLegit + 1                            
                      matchIndex = matchIndex + 1		     
                 if iThisIsLegit == 2: # It's legit!
                      maxOverlayNum = testOverlayNum
                      numOfOverlaysFound = numOfOverlaysFound + 1
                      scene_list.append(sceneC)
                 testOverlayNum = testOverlayNum + 1

            # No matter what our setup is, we need to have the output nodes. So create those.
            outputNodeLocationX = 200
            if (scene.stereo_comp_show_anaglyph_preview == True):
                outputNodeLocationX = 950 # It needs to be moved over further
            # file output left
            file_output_node_left = tree.nodes.new('CompositorNodeOutputFile')
            file_output_node_left.base_path = "//_LEFT"
            file_output_node_left.file_slots.clear()
            file_output_node_left.file_slots.new("limg")
            file_output_node_left.location = (outputNodeLocationX, 270) 
    
            # file output right
            file_output_node_right = tree.nodes.new('CompositorNodeOutputFile')
            file_output_node_right.base_path = "//_RIGHT" 
            file_output_node_right.file_slots.clear()
            file_output_node_right.file_slots.new("rimg")
            file_output_node_right.location = (outputNodeLocationX, 0)

            # If we have a static background, put in the nodes for it.
            if useImageBackground == 1: 
                # Do the left background node
                image_background_L = tree.nodes.new('CompositorNodeImage')
                image_background_L.location = (-400,280)
                try:
                    t = bpy.data.images.load(scene.stereo_comp_bkgd_image_L)
                    image_background_L.image = t
                except:
                    pass
                # We need to scale the image to match the render size.
                image_background_scale_L = tree.nodes.new('CompositorNodeScale')
                image_background_scale_L.location = (-400,0)
                image_background_scale_L.space = 'RENDER_SIZE'
                image_background_scale_L.frame_method = 'FIT'
                # ...and the AlphaOver that it's going to go into.
                alphaoverBackground_L = tree.nodes.new('CompositorNodeAlphaOver')
                alphaoverBackground_L.location = (-300,400) 
                alphaoverBackground_L.premul = 0.5
                # ...and pre-hook it up:
                tree.links.new(image_background_L.outputs[0],image_background_scale_L.inputs[0])
                tree.links.new(image_background_scale_L.outputs[0],alphaoverBackground_L.inputs[1])


                # Do the right background node
                image_background_R = tree.nodes.new('CompositorNodeImage')
                image_background_R.location = (-400,-280)
                try:
                    t = bpy.data.images.load(scene.stereo_comp_bkgd_image_R)
                    image_background_R.image = t
                except:
                    pass
                # We need to scale the image to match the render size.
                image_background_scale_R = tree.nodes.new('CompositorNodeScale')
                image_background_scale_R.location = (-400,0)
                image_background_scale_R.space = 'RENDER_SIZE'
                image_background_scale_R.frame_method = 'FIT'
                # ...and the AlphaOver that it's going to go into.
                alphaoverBackground_R = tree.nodes.new('CompositorNodeAlphaOver')
                alphaoverBackground_R.location = (-300,-400) 
                alphaoverBackground_R.premul = 0.5
                # ...and pre-hook it up:
                tree.links.new(image_background_R.outputs[0],image_background_scale_R.inputs[0])
                tree.links.new(image_background_scale_R.outputs[0],alphaoverBackground_R.inputs[1])

    
            if (scene.stereo_comp_show_anaglyph_preview == True):
                # Make the anaglyph image. We'll plug into the main node once we figure out where our final node is.
    
                # Separate red from the left image
                left_seperate = tree.nodes.new('CompositorNodeSepRGBA')
                left_seperate.location = (200,250)
               
                # Separate green and blue from the right image
                right_seperate = tree.nodes.new('CompositorNodeSepRGBA')
                right_seperate.location = (200,-20)
                
                # Combine red and cyan
                combine_node = tree.nodes.new('CompositorNodeCombRGBA')
                combine_node.location = (450, 100)
                
                # Comp output
                composite_node = tree.nodes.new('CompositorNodeComposite')
                composite_node.location = (700, 100)
                
                # Noodle from red seperate to combine
                tree.links.new(left_seperate.outputs[0],combine_node.inputs[0])  
                
                # Noodle from cyan seperate to combine
                tree.links.new(right_seperate.outputs[1],combine_node.inputs[1])
                tree.links.new(right_seperate.outputs[2],combine_node.inputs[2])
                
                # Noddle from combine to comp output 
                tree.links.new(combine_node.outputs[0],composite_node.inputs[0])        
    




            if numOfOverlaysFound == 0:
                 # There's nothing to do, so get out.
                 return 
    
            # Check for our special case where we have only one legit stereo scene.
            if numOfOverlaysFound == 1:
                if useImageBackground == 0:
                     # Just connect things with no AlphaOver nodes and no image background.
                     sceneL = scene_list[0] + "_L"
                     sceneR = scene_list[0] + "_R"
                     # Set the left image node. 
                     left_render_layer = tree.nodes.new('CompositorNodeRLayers')
                     left_render_layer.location = (0,280)
                     try: 
                         left_render_layer.scene = bpy.data.scenes[sceneL]
                     except:
                         pass
            
                     # Set the right image node. 
                     right_render_layer = tree.nodes.new('CompositorNodeRLayers')
                     right_render_layer.location = (0,-10)
                     try: 
                         right_render_layer.scene = bpy.data.scenes[sceneR]
                     except:
                         pass
    
                     # We have no overlay. Just hook directly from the render nodes into the output nodes.
                     tree.links.new(left_render_layer.outputs[0],file_output_node_left.inputs[0])
                     tree.links.new(right_render_layer.outputs[0],file_output_node_right.inputs[0])     
                     if (scene.stereo_comp_show_anaglyph_preview == True):
                         # ...and hook up the anaglyph node.  
                         tree.links.new(left_render_layer.outputs[0],left_seperate.inputs[0])            
                         tree.links.new(right_render_layer.outputs[0],right_seperate.inputs[0])             
                     return
                else: # useImageBackground == 1
                     # Just connect things with an image background.

                     sceneL = scene_list[0] + "_L"
                     sceneR = scene_list[0] + "_R"
                     # Set the left image node. 
                     left_render_layer = tree.nodes.new('CompositorNodeRLayers')
                     left_render_layer.location = (0,280)
                     try: 
                         left_render_layer.scene = bpy.data.scenes[sceneL]
                     except:
                         pass
            
                     # Set the right image node. 
                     right_render_layer = tree.nodes.new('CompositorNodeRLayers')
                     right_render_layer.location = (0,-10)
                     try: 
                         right_render_layer.scene = bpy.data.scenes[sceneR]
                     except:
                         pass

                     # Hook up the left and right scenes to the AlphaOvers that have the image
                     tree.links.new(left_render_layer.outputs[0],alphaoverBackground_L.inputs[2])
                     tree.links.new(right_render_layer.outputs[0],alphaoverBackground_R.inputs[2])
                     # Now hook up the AlphaOvers to the file outputs.
                     tree.links.new(alphaoverBackground_L.outputs[0],file_output_node_left.inputs[0])
                     tree.links.new(alphaoverBackground_R.outputs[0],file_output_node_right.inputs[0])     
                     if (scene.stereo_comp_show_anaglyph_preview == True):
                         # ...and hook up the anaglyph node.  
                         tree.links.new(alphaoverBackground_L.outputs[0],left_seperate.inputs[0])            
                         tree.links.new(alphaoverBackground_R.outputs[0],right_seperate.inputs[0])             
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
    
                      alphaover1_R = tree.nodes.new('CompositorNodeAlphaOver')
                      alphaover1_R.location = (currentXVal,-270)
                      alphaover1_R.premul = 0.5
    
    
                 # Create this overlay node.
                    
                 # Make the names.
                 sL = currentScene + '_L'
                 sR = currentScene + '_R'
    
    
                 # The next batch of nodes need to move over to the left.
                 currentXVal = currentXVal - 200
    
                 # Overlay L
                 overlay_layer_L = tree.nodes.new('CompositorNodeRLayers')
                 overlay_layer_L.location = (currentXVal,160)
                 try: 
                      overlay_layer_L.scene = bpy.data.scenes[sL]
                 except:
                      pass
    
                 # Overlay R
                 overlay_layer_R = tree.nodes.new('CompositorNodeRLayers')
                 overlay_layer_R.location = (currentXVal,-480)
                 try: 
                      overlay_layer_R.scene = bpy.data.scenes[sR]
                 except:
                      pass
    
    
                 if currentOverlayNum == 1:
                      # Special condition where this AlphaOver is the end of the line. Must plug this into the final renderer.
                      tree.links.new(alphaover1_L.outputs[0],file_output_node_left.inputs[0])
                      tree.links.new(alphaover1_R.outputs[0],file_output_node_right.inputs[0])     
                      if (scene.stereo_comp_show_anaglyph_preview == True):
                          # ...and hook up the anaglyph node.  
                          tree.links.new(alphaover1_L.outputs[0],left_seperate.inputs[0])            
                          tree.links.new(alphaover1_R.outputs[0],right_seperate.inputs[0])  
    
                      # Connect the overlays to the AlphaOvers.
                      tree.links.new(overlay_layer_L.outputs[0],alphaover1_L.inputs[2])
                      tree.links.new(overlay_layer_R.outputs[0],alphaover1_R.inputs[2])
    
                 elif currentOverlayNum == numOfOverlaysFound:
                      # We're at the very topmost layer.
                      if useImageBackground == 0:
                          # Connect the overlay into the AlphaOver from the *previous iteration of this loop*.
                          tree.links.new(overlay_layer_L.outputs[0],alphaoverOLD1_L.inputs[1])
                          tree.links.new(overlay_layer_R.outputs[0],alphaoverOLD1_R.inputs[1])
                      else: # useImageBackground == 1:
                          # Connect the overlay into the alphaoverBackground so that we put in the background image.
                          tree.links.new(overlay_layer_L.outputs[0],alphaoverBackground_L.inputs[2])
                          tree.links.new(overlay_layer_R.outputs[0],alphaoverBackground_R.inputs[2])
                          # Now hook up the AlphaOvers into the AlphaOvers from the *previous iteration of this loop*.
                          tree.links.new(alphaoverBackground_L.outputs[0],alphaoverOLD1_L.inputs[1])
                          tree.links.new(alphaoverBackground_R.outputs[0],alphaoverOLD1_R.inputs[1])     

                 else:
                      # Connect the overlays to the AlphaOvers.
                      tree.links.new(overlay_layer_L.outputs[0],alphaover1_L.inputs[2])
                      tree.links.new(overlay_layer_R.outputs[0],alphaover1_R.inputs[2])
    
                      # We need to plug into the AlphaOver from the previous iteration of this loop.
                      tree.links.new(alphaover1_L.outputs[0],alphaoverOLD1_L.inputs[1])
                      tree.links.new(alphaover1_R.outputs[0],alphaoverOLD1_R.inputs[1])
    
                 if currentOverlayNum != numOfOverlaysFound: # We still need the AlphaOvers because we're not done yet
                      # Remember our old AlphaOvers for the next iteration.
                      alphaoverOLD1_L = alphaover1_L
                      alphaoverOLD1_R = alphaover1_R
    
                 currentOverlayNum = currentOverlayNum + 1
    
                    


#
# Operator 'Remove Stereo Scenes'
#
class OBJECT_OT_remove_stereo_scenes(bpy.types.Operator):
    bl_label = 'Remove Stereo Scenes'
    bl_idname = 'stereocamera.remove_stereo_scenes'
    bl_description = 'Removes all stereo scenes from the project. This will hopefully prevent CUDA-enabled projects from crashing if you click this before clicking the Add Nodes button.'

    # on mouse up:
    def invoke(self, context, event):

        # add the selected preset
        self.remove_stereo_scenes(context)

        return {'FINISHED'}

    def remove_stereo_scenes(self, context):
        for scene in bpy.data.scenes:
            s = scene.name
            if ((s[-2:] == "_L") or (s[-2:] == "_R")) and (s[3:4] == " ") and (s[0:3].isdigit()):
                try:
                    bpy.data.scenes.remove(bpy.data.scenes[s])
                    self.report({'INFO'}, "Deleted scene '" + s + "'")

                except:
                    pass










def upd(self, context):
    import os
    if self.stereo_comp_bkgd_image_L.upper().endswith("L.PNG"):
        t = self.stereo_comp_bkgd_image_L[:-5] + "R.png"
        if os.path.exists(bpy.path.abspath(t)):
            self.stereo_comp_bkgd_image_R = t
    if self.stereo_comp_bkgd_image_L.upper().endswith("LEFT.PNG"):
        t = self.stereo_comp_bkgd_image_L[:-8] + "RIGHT.png"
        if os.path.exists(bpy.path.abspath(t)):
            self.stereo_comp_bkgd_image_R = t



#
# Register
#
addon_keymaps = []

def register():

    # handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY')
#    kmi = km.keymap_items.new(OBJECT_OT_add_stereo_node_preset.bl_idname, 'SPACE', 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new(OBJECT_OT_add_stereo_node_preset.bl_idname, 'F11', 'PRESS')
    addon_keymaps.append((km, kmi))

    bpy.utils.register_module(__name__)

    bpy.types.Scene.stereo_comp_presets = bpy.props.EnumProperty(attr="stereo_comp_preset",
        items=[ ("3DNODES-ALL", "3D nodes - all scenes", "Make stereo nodes for all scenes"),
                ("3DNODES-ONE", "3D nodes - only this scene", "Make stereo nodes for only this scene"), 
		("2DNODES-ONE", "2D node - only this scene", "Make center node for only this scene"),],
        name="Create", 
        description="Select which sort of nodes to create", 
        default="3DNODES-ALL")

    bpy.types.Scene.stereo_comp_replace_current_nodes = bpy.props.BoolProperty(
        name="Replace Current Nodes", 
        description="Replace Current Nodes?", 
        default=True)

    bpy.types.Scene.stereo_comp_show_anaglyph_preview = bpy.props.BoolProperty(
        name="Show Anaglyph Preview", 
        description="Show Anaglyph Preview?", 
        default=False)
	
    bpy.types.Scene.stereo_comp_bkgd_image_L = bpy.props.StringProperty(
            name="L Background Image",
            subtype='FILE_PATH',
            update=upd,
            )

    bpy.types.Scene.stereo_comp_bkgd_image_R = bpy.props.StringProperty(
            name="R Background Image",
            subtype='FILE_PATH',
            )

def unregister():
    # remove keymap entry
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_module(__name__)
	
if __name__ == "__main__":
    register()
