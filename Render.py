bl_info = {
    "name": "Render WhiteModel",
    "author": "JinYiGao",
    "version": (1, 2, 0),
    "blender": (2, 80, 0),
    "description": "roof is red,body is gray",
    "category": "Object",
}

import bpy
import bmesh

class Render(bpy.types.Operator):

    bl_idname = "object.render"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Render WhiteModel"     # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    def execute(self,context):
        #select mesh and join
        bpy.ops.object.select_by_type(type='MESH')
        ob=bpy.context.selected_objects
        bpy.context.view_layer.objects.active=ob[0]
        bpy.ops.object.join()

        #move model to (0,0,0)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        #get the bound_box
        a=[v[:] for v in bpy.context.object.bound_box]
        length=a[6][0]-a[0][0]
        width=a[6][1]-a[0][1]
        scale=1/max(length,width)
        bpy.context.object.scale[0] = scale
        bpy.context.object.scale[1] = scale
        bpy.context.object.scale[2] = scale
        bpy.context.object.location[0] = 0
        bpy.context.object.location[1] = 0
        bpy.context.object.location[2] = -scale*a[0][2]
        bpy.context.object.rotation_euler[0] = 0.0
        bpy.context.object.rotation_euler[1] = 0.0
        bpy.context.object.rotation_euler[2] = 0.0

        #edit mode
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')

        #add material of gray
        matName1="Gray"
        bpy.data.materials.new(matName1)
        bpy.data.materials[matName1].use_nodes=True
        #bpy.data.materials[matName1].node_tree.nodes.remove(bpy.data.materials[matName1].node_tree.nodes.get('Principled BSDF'))
        material_output = bpy.data.materials[matName1].node_tree.nodes.get('Material Output')
        Glossy1=bpy.data.materials[matName1].node_tree.nodes.new('ShaderNodeBsdfDiffuse')
        Glossy1.inputs['Color'].default_value=(0.1,0.1,0.1,1)
        Glossy1.inputs['Roughness'].default_value=0
        bpy.data.materials[matName1].node_tree.links.new(material_output.inputs[0],Glossy1.outputs[0])

        #select top1 material
        bpy.context.object.active_material_index = 0
        bpy.context.object.active_material=bpy.data.materials[matName1]

        #keep the selected gray
        bpy.ops.object.material_slot_assign()

        #select faces of roof
        obj=bpy.context.edit_object.data
        bm=bmesh.from_edit_mesh(obj)
        for f in bm.faces:
            if f.normal.z==0.0 or f.normal.z<0.0:
                f.select=False
                bmesh.update_edit_mesh(obj,True)

        #for i in bm.edges:
            #i.select=True
            #bmesh.update_edit_mesh(obj,True)
            #bpy.ops.mesh.mark_freestyle_edge(clear=False)

        #add material of Red
        bpy.ops.object.material_slot_add()
        matName2="Red"
        bpy.data.materials.new(matName2)
        bpy.data.materials[matName2].use_nodes=True
        #bpy.data.materials[matName2].node_tree.nodes.remove(bpy.data.materials[matName2].node_tree.nodes.get('Principled BSDF'))
        material_output = bpy.data.materials[matName2].node_tree.nodes.get('Material Output')
        Glossy2=bpy.data.materials[matName2].node_tree.nodes.new('ShaderNodeBsdfDiffuse')
        Glossy2.inputs['Color'].default_value=(0.3,0.0,0.0,1)
        Glossy2.inputs['Roughness'].default_value=0
        bpy.data.materials[matName2].node_tree.links.new(material_output.inputs[0],Glossy2.outputs[0])

        #select top2 material
        bpy.context.object.active_material_index = 1
        bpy.context.object.active_material=bpy.data.materials[matName2]

        #keep the selected Red
        bpy.ops.object.material_slot_assign()

        #set Freestyle
        bpy.context.scene.render.use_freestyle = True
        freestyle_settings = bpy.context.scene.view_layers["View Layer"].freestyle_settings
        lineset = freestyle_settings.linesets["LineSet"]
        lineset.select_edge_mark = True
        bpy.context.scene.render.line_thickness = 0.8
        if length>1000 or width>1000:
            bpy.context.scene.render.line_thickness = 0.4

        #set render pixel
        bpy.context.scene.render.resolution_x = 3840
        bpy.context.scene.render.resolution_y = 2160

        #set light
        bpy.data.lights['Light'].type ='SUN'
        bpy.data.lights['Light'].energy=40.0
        bpy.data.lights['Light'].use_shadow=True
        bpy.data.lights['Light'].use_contact_shadow = True
        bpy.data.objects['Light'].location=(scale*length/2+1,0,1)

        #Finish
        bpy.ops.object.editmode_toggle()

        #create a plane
        bpy.ops.mesh.primitive_plane_add(size=2*length, enter_editmode=False, location=(0, 0, 0))
        bpy.data.objects['Plane'].select_set(True)
        bpy.context.object.active_material_index = 0
        bpy.data.materials.new("White")
        bpy.data.materials["White"].use_nodes=False
        bpy.context.object.active_material=bpy.data.materials["White"]
        bpy.context.object.active_material.diffuse_color = (1, 1, 1, 1)
        bpy.context.object.active_material.specular_intensity = 1
        bpy.context.object.active_material.roughness = 1

        #Add light[AREA]
        bpy.ops.object.light_add(type='AREA', radius=scale*width+1, location=(-(scale*length/2+1), 0, 1))
        bpy.context.object.data.energy = 150
        bpy.ops.transform.rotate(value=-0.851808, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))
        bpy.context.object.data.use_shadow = True
        bpy.context.object.data.use_contact_shadow = True

        bpy.ops.object.light_add(type='AREA', radius=scale*length+1, location=(0, scale*width/2+1, 1))
        bpy.ops.transform.rotate(value=-0.79003, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))
        bpy.context.object.data.energy = 150
        bpy.context.object.data.use_shadow = True
        bpy.context.object.data.use_contact_shadow = True

        bpy.ops.object.light_add(type='AREA', radius=scale*length+1, location=(0, -(scale*width/2+1), 1))
        bpy.ops.transform.rotate(value=0.895654, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))
        bpy.context.object.data.energy = 150
        bpy.context.object.data.use_shadow = True
        bpy.context.object.data.use_contact_shadow = True

        #add ReflectionCumbemap
        bpy.ops.object.lightprobe_add(type='CUBEMAP', enter_editmode=False, location=(0, 0, 0))
        bpy.ops.transform.resize(value=(-max(scale*length/2,scale*width/2+1), -max(scale*length/2,scale*width/2+1), -max(scale*length/2,scale*width/2+1)), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))

        #lock camera
        bpy.context.space_data.lock_camera = True

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(Render.bl_idname)

def register():
    bpy.utils.register_class(Render)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(Render)

if __name__ == "__main__":
    register()