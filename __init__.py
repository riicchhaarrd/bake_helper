bl_info = {
	"name": "Bake Helper",
	"blender": (2, 80, 0),
	"category": "Object",
}

import bpy
from bpy.types import (Panel, Operator)
from bpy.props import (StringProperty, IntProperty,
					   PointerProperty,
					   )
					   
from bpy.types import (Panel,
					   PropertyGroup,
					   )

# ------------------------------------------------------------------------
#	 Operators
# ------------------------------------------------------------------------

class Operator1(Operator):
	"""Operator"""
	bl_idname = "object.operator1"
	bl_label = ""

	def execute(self, context):
		def setup_mesh(ob):
			obj = bpy.context.active_object
			new_mat = bpy.data.materials.new(name="NewMaterial")

			if ob.data.materials:
				ob.data.materials[0] = new_mat
			else:
				ob.data.materials.append(new_mat)

			bpy.context.object.active_material = new_mat
			bpy.context.object.active_material.use_nodes = True
			nodes = bpy.context.object.active_material.node_tree.nodes
			links = bpy.context.object.active_material.node_tree.links

			for node in nodes:
				nodes.remove(node)

			principled_node = nodes.new('ShaderNodeBsdfPrincipled')
			principled_node.location = (-200, 0)  # Adjust the location if needed

			image_node = nodes.new('ShaderNodeTexImage')
			image_node.location = (-600, 0)	 # Adjust the location if needed

			empty_image = bpy.data.images.new(name="EmptyImage", width=512, height=512)

			image_node.image = empty_image

			#links.new(image_node.outputs[0], principled_node.inputs['Base Color'])

			output_node = nodes.new('ShaderNodeOutputMaterial')
			output_node.location = (200, 0)	 # Adjust the location if needed

			links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
			
			for node in nodes:
				node.select = False

			image_node.select = True
			bpy.context.object.active_material.node_tree.nodes.active = image_node

			obj.data.materials[0] = new_mat
			#bpy.ops.object.bake()
			
		if bpy.context.active_object is None:
			print("No active object selected.")
		else:
			bpy.ops.object.select_all(action='DESELECT')

			for obj in bpy.context.scene.objects:
				if obj.type == 'MESH':
					obj.select_set(True)
					setup_mesh(obj)

		return {'FINISHED'}
		
class Operator2(Operator):
	"""Operator"""
	bl_idname = "object.operator2"
	bl_label = ""

	def execute(self, context):
		for obj in bpy.context.scene.objects:
			if obj.type == 'MESH':
				for slot in obj.material_slots:
					if slot.material:
						if not slot.material.use_nodes:
							slot.material.use_nodes = True

						tree = slot.material.node_tree

						image_node = None
						for node in tree.nodes:
							if node.type == 'TEX_IMAGE' and node.image:
								image_node = node
								break

						if image_node is None:
							continue

						output_node = None
						for node in tree.nodes:
							if node.type == 'OUTPUT_MATERIAL':
								output_node = node
								break
								
						if output_node:
							links = tree.links
							for link in links:
								if link.from_node == image_node:
									links.remove(link)
							links.new(image_node.outputs[0], output_node.inputs[0])

		return {'FINISHED'}
		
class Operator3(Operator):
	"""Operator"""
	bl_idname = "object.operator3"
	bl_label = ""

	def execute(self, context):
		for obj in bpy.context.scene.objects:
			if obj.type == 'MESH':
				# Iterate through all materials of the object
				for slot in obj.material_slots:
					if slot.material:
						if not slot.material.use_nodes:
							slot.material.use_nodes = True

						tree = slot.material.node_tree

						principled_node = None
						for node in tree.nodes:
							if node.type == 'BSDF_PRINCIPLED':
								principled_node = node
								break
						output_node = None
						for node in tree.nodes:
							if node.type == 'OUTPUT_MATERIAL':
								output_node = node
								break

						if principled_node and output_node:
							links = tree.links
							for link in links:
								links.remove(link)
							links.new(principled_node.outputs[0], output_node.inputs[0])

		return {'FINISHED'}

# ------------------------------------------------------------------------
#	 Panel in Object Mode
# ------------------------------------------------------------------------

class MyProperties(PropertyGroup):

	image_resolution: IntProperty(
		name="Bake image resolution",
		description=":",
		default=1024,
		)

	#bar: StringProperty(
	#	 name="Bar",
	#	 description=":",
	#	 default="",
	#	 maxlen=1024,
	#	 )
		
class OBJECT_PT_CustomPanel(Panel):
	bl_idname = "object.custom_panel"
	bl_label = "Bake Helper"
	bl_space_type = "VIEW_3D"	
	bl_region_type = "UI"
	bl_category = "Tools"
	bl_context = "objectmode"	


	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		mytool = scene.my_tool
		obj = context.object

		layout.label(text="Properties:")

		layout.prop(mytool, "image_resolution")
		#col = layout.column(align=True)
		#row = col.row(align=True)
		#row.prop(obj, "show_name", toggle=True, icon="FILE_FONT")
		#row.prop(obj, "show_wire", toggle=True, text="Wireframe", icon="SHADING_WIRE")
		#col.prop(obj, "show_all_edges", toggle=True, text="Show all Edges", icon="MOD_EDGESPLIT")
		layout.separator()

		layout.label(text="Operators:")

		col = layout.column(align=True)
		col.operator(Operator1.bl_idname, text="Add image to meshes", icon="CONSOLE")
		col.operator(Operator2.bl_idname, text="Material output: Baked image", icon="CONSOLE")
		col.operator(Operator3.bl_idname, text="Material output: Principled BSDF node", icon="CONSOLE")

		layout.separator()

# ------------------------------------------------------------------------
#	 Registration
# ------------------------------------------------------------------------

classes = (
	MyProperties,
	OBJECT_PT_CustomPanel,
	Operator1,
	Operator2,
	Operator3
)
def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)

	bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)

def unregister():
	from bpy.utils import unregister_class
	for cls in reversed(classes):
		unregister_class(cls)
	del bpy.types.Scene.my_tool

if __name__ == "__main__":
	register()
