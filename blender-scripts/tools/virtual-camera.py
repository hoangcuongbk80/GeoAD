import bpy
import mathutils
import math
import os  
import shutil
import random

# Paths and configuration
data_dir = '/blender-scripts/data'
save_dir = '/blender-scripts/data/001'
all_obj = ['object1', 'object2', 'object3', 'object4', 'object5',
           'object6', 'object7', 'object8', 'object9', 'object10']
objects = ['object1', 'object2', 'object3', 'object4', 'object5']

# Option to reset dataset folders
reset_data = False
if reset_data:
    if os.path.isdir(data_dir):
        shutil.rmtree(data_dir)
    os.makedirs(data_dir + '/depth', exist_ok=True)
    os.makedirs(data_dir + '/mask', exist_ok=True)
    for obj in all_obj:
        os.makedirs(data_dir + '/mask/' + obj, exist_ok=True)
        
# Ensure directories exist for saving
os.makedirs(save_dir + '/depth', exist_ok=True)
os.makedirs(save_dir + '/mask', exist_ok=True)
os.makedirs(save_dir + '/anomalies', exist_ok=True)  # New directory for anomaly maps
for obj in objects:
    os.makedirs(save_dir + '/mask/' + obj, exist_ok=True)
        
# Function to update the camera's position and orientation
def update_camera(camera, focus_point=mathutils.Vector((0.0, 0.0, 0.0)), distance=1.5):
    """
    Focus the camera to a specific focus point and set its position at a given distance.

    :param camera: Camera object in the Blender scene.
    :param focus_point: Coordinates of the focus point (default=(0, 0, 0)).
    :param distance: Distance from the camera to the focus point.
    """
    looking_direction = camera.location - focus_point
    rot_quat = looking_direction.to_track_quat('Z', 'Y')

    camera.rotation_euler = rot_quat.to_euler()
    camera.location = rot_quat @ mathutils.Vector((0.0, 0.0, distance))

# Function to add anomalies to objects
def add_anomaly(obj, anomaly_type='dent', intensity=0.1):
    """
    Add a controlled anomaly to the given object.

    :param obj: Blender object to which the anomaly will be added.
    :param anomaly_type: Type of anomaly ('dent', 'scratch', 'missing').
    :param intensity: Intensity of the anomaly (default=0.1).
    """
    if anomaly_type == 'dent':
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_random(percent=intensity * 100)
        bpy.ops.transform.shrink_fatten(value=-0.02)  # Create a dent
        bpy.ops.object.mode_set(mode='OBJECT')
    elif anomaly_type == 'scratch':
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_random(percent=intensity * 100)
        bpy.ops.transform.translate(value=(0, 0.02, 0))  # Create scratches
        bpy.ops.object.mode_set(mode='OBJECT')
    elif anomaly_type == 'missing':
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_random(percent=intensity * 100)
        bpy.ops.mesh.delete(type='VERT')  # Create missing parts
        bpy.ops.object.mode_set(mode='OBJECT')

# Save object poses to a file
with open(os.path.join(save_dir, "object_pose.txt"), 'w') as fs:
    fs.write("object_ID x y z rx ry rz\n")
    for obj in bpy.data.objects:
        if obj.name not in ['Camera', 'Grid', 'Light']:
            fs.write(f"{obj.name} ")
            loc = obj.location
            fs.write(f"{loc[0]:.6f} {loc[1]:.6f} {loc[2]:.6f} ")
            rot = obj.rotation_euler
            fs.write(f"{rot[0]:.6f} {rot[1]:.6f} {rot[2]:.6f}\n")

# Configure camera for rendering
cam = bpy.data.objects['Camera']
num_view = 10
pi = math.pi
radius = 8

# Open camera pose file
camera_pose_path = os.path.join(save_dir, "camera_pose.txt")
with open(camera_pose_path, "w") as f:
    f.write("image x y z rx ry rz\n")
    idx = 0

    # Generate multiple views with anomalies
    for z in range(8, 18):  # Vary camera height
        for i in range(num_view):  # Rotate around the object
            print(f"\nRendering image index: {idx}")
            cam_Z = 1.0 * z
            cam_X = radius * math.cos(i * pi / num_view)
            cam_Y = radius * math.sin(i * pi / num_view)
            cam.location = (cam_X, cam_Y, cam_Z)
            update_camera(cam)

            # Randomly add anomalies to objects
            for obj_name in objects:
                obj = bpy.data.objects.get(obj_name)
                if obj and random.random() > 0.5:  # 50% chance to add anomaly
                    anomaly_type = random.choice(['dent', 'scratch', 'missing'])
                    add_anomaly(obj, anomaly_type, intensity=0.1)

            # Render the scene
            bpy.ops.render.render(write_still=True)

            # Rename and save depth, mask, and anomaly images
            old_name = os.path.join(data_dir, 'depth/Image0000.exr')
            new_name = os.path.join(save_dir, 'depth', f"{idx}.exr")
            if os.path.exists(old_name):
                os.rename(old_name, new_name)

            for obj in objects:
                old_mask_name = os.path.join(data_dir, f'mask/{obj}/Image0000.png')
                new_mask_name = os.path.join(save_dir, 'mask', obj, f"{idx}.png")
                if os.path.exists(old_mask_name):
                    os.rename(old_mask_name, new_mask_name)

            # Save anomaly maps (binary maps indicating anomaly regions)
            anomaly_map_path = os.path.join(save_dir, 'anomalies', f"{idx}.png")
            bpy.ops.render.render(write_still=True, filepath=anomaly_map_path)

            # Save camera pose
            img_name = f"{idx}.exr"
            loc = cam.location
            rot = cam.rotation_euler
            f.write(f"{img_name} {loc[0]:.6f} {loc[1]:.6f} {loc[2]:.6f} {rot[0]:.6f} {rot[1]:.6f} {rot[2]:.6f}\n")
            
            idx += 1

print("Dataset generation completed successfully!")
