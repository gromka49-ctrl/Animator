bl_info = {
    "name": "Animator JSON Bridge",
    "author": "Animator contributors",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "File > Import/Export",
    "description": "Import and export neutral bone animation clips as JSON",
    "category": "Import-Export",
}

import bpy
import json
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper


def _active_armature():
    obj = bpy.context.view_layer.objects.active
    if obj and obj.type == 'ARMATURE':
        return obj
    for candidate in bpy.context.selected_objects:
        if candidate.type == 'ARMATURE':
            return candidate
    return None


def _quat_from_value(value):
    # Animator stores quaternions as [x, y, z, w]; Blender uses [w, x, y, z].
    return (value[3], value[0], value[1], value[2])


def _value_from_quat(q):
    return [q[1], q[2], q[3], q[0]]


def _insert_track(action, armature, track):
    bone_name = track.get('boneName')
    prop = track.get('property')
    bone = armature.pose.bones.get(bone_name)
    if not bone:
        return False

    if prop == 'rotation' or prop == 'quaternion':
        bone.rotation_mode = 'QUATERNION'
        data_path = f'pose.bones["{bone_name}"].rotation_quaternion'
        index = -1
    elif prop == 'position':
        data_path = f'pose.bones["{bone_name}"].location'
        index = -1
    elif prop == 'scale':
        data_path = f'pose.bones["{bone_name}"].scale'
        index = -1
    else:
        return False

    for key in track.get('keyframes', []):
        frame = float(key.get('time', 0)) * float(action['__animator_fps']) + 1
        value = key.get('value', [])
        if prop == 'rotation' or prop == 'quaternion':
            bone.rotation_quaternion = _quat_from_value(value)
        elif prop == 'position':
            bone.location = value
        else:
            bone.scale = value
        bone.keyframe_insert(data_path=data_path, index=index, frame=frame, group=bone_name)
    return True


class ANIMATOR_OT_import_json(bpy.types.Operator, ImportHelper):
    bl_idname = "animator.import_json_clip"
    bl_label = "Import Animator JSON Clip"
    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        armature = _active_armature()
        if not armature:
            self.report({'ERROR'}, "Select an armature before importing a clip")
            return {'CANCELLED'}
        try:
            with open(self.filepath, 'r', encoding='utf-8') as handle:
                clip = json.load(handle)
        except Exception as exc:
            self.report({'ERROR'}, f"Could not read JSON: {exc}")
            return {'CANCELLED'}

        action = bpy.data.actions.new(clip.get('name', 'Animator Clip'))
        action.use_fake_user = True
        action['animator_fps'] = float(clip.get('fps', 30))
        action['animator_duration'] = float(clip.get('duration', 0))
        action['__animator_fps'] = float(clip.get('fps', 30))
        armature.animation_data_create()
        armature.animation_data.action = action

        missing = []
        for track in clip.get('tracks', []):
            if not _insert_track(action, armature, track):
                missing.append(track.get('boneName', '<unknown>'))
        if '__animator_fps' in action:
            del action['__animator_fps']
        if missing:
            self.report({'WARNING'}, "Imported with missing/unsupported bones: " + ', '.join(sorted(set(missing))))
        else:
            self.report({'INFO'}, f"Imported {action.name}")
        return {'FINISHED'}


class ANIMATOR_OT_export_json(bpy.types.Operator, ExportHelper):
    bl_idname = "animator.export_json_clip"
    bl_label = "Export Animator JSON Clip"
    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        armature = _active_armature()
        if not armature or not armature.animation_data or not armature.animation_data.action:
            self.report({'ERROR'}, "Select an armature with an active Action")
            return {'CANCELLED'}
        action = armature.animation_data.action
        fps = float(action.get('animator_fps', context.scene.render.fps or 30))
        end_frame = action.frame_range[1] if action.fcurves else 1
        clip = {
            'version': 1,
            'name': action.name,
            'duration': max(0.0, (end_frame - 1) / fps),
            'fps': fps,
            'loop': False,
            'tracks': []
        }
        grouped = {}
        for fcurve in action.fcurves:
            path = fcurve.data_path
            if not path.startswith('pose.bones['):
                continue
            bone_name = path.split('pose.bones["', 1)[1].split('"]', 1)[0]
            if path.endswith('rotation_quaternion'):
                prop, size = 'quaternion', 4
            elif path.endswith('location'):
                prop, size = 'position', 3
            elif path.endswith('scale'):
                prop, size = 'scale', 3
            else:
                continue
            grouped.setdefault((bone_name, prop), {})[fcurve.array_index] = fcurve
            times = sorted({kp.co.x for curve in grouped[(bone_name, prop)].values() for kp in curve.keyframe_points})
            keyframes = []
            for frame in times:
                values = [0.0] * size
                for axis, curve in grouped[(bone_name, prop)].items():
                    nearest = min(curve.keyframe_points, key=lambda kp: abs(kp.co.x - frame))
                    values[axis] = float(nearest.co.y)
                if prop == 'quaternion':
                    values = _value_from_quat(values)
                keyframes.append({'time': (frame - 1) / fps, 'value': values})
            existing = next((t for t in clip['tracks'] if t['boneName'] == bone_name and t['property'] == prop), None)
            if existing:
                existing['keyframes'] = keyframes
            else:
                clip['tracks'].append({'boneName': bone_name, 'property': prop, 'keyframes': keyframes})
        try:
            with open(self.filepath, 'w', encoding='utf-8') as handle:
                json.dump(clip, handle, indent=2)
        except Exception as exc:
            self.report({'ERROR'}, f"Could not write JSON: {exc}")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Exported {action.name}")
        return {'FINISHED'}


def menu_import(self, context):
    self.layout.operator(ANIMATOR_OT_import_json.bl_idname, text="Animator JSON Clip (.json)")


def menu_export(self, context):
    self.layout.operator(ANIMATOR_OT_export_json.bl_idname, text="Animator JSON Clip (.json)")


classes = (ANIMATOR_OT_import_json, ANIMATOR_OT_export_json)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_export)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_export)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
